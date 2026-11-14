package kr.pleosguide

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import org.json.JSONObject
import org.json.JSONTokener

class GleoReceiver : BroadcastReceiver() {
    override fun onReceive(context:Context,intent:Intent) {
        val action=intent.action ?: return
        val evidence=EvidenceRecorder(context)
        var status="fail"; var message="The action could not be processed."
        var data=JSONObject()
        // Android broadcast alone cannot prove that a natural Gleo voice invocation occurred.
        val source=SourceType.UNVERIFIED_INTENT
        try {
            val raw=intent.getStringExtra("ACTION_PARAM")
            val params=if(raw!=null) {
                val parsed=JSONTokener(raw).nextValue()
                if(parsed is JSONObject) parsed else if(parsed is String) JSONObject(parsed) else throw IllegalArgumentException("Object expected")
            } else JSONObject().also { o -> intent.extras?.keySet()?.forEach { key -> o.put(key,intent.extras?.get(key)) } }
            evidence.event("GLEO_ACTION_RECEIVED",source,"$action:$params")
            val service=TutorialService.current
            when(action) {
                "SET_TUTORIAL_MODE" -> {
                    if(!params.has("enabled")) { status="asking"; message="Please specify whether to enable the tutorial." }
                    else if(params.opt("enabled") !is Boolean) { message="Enabled must be a boolean." }
                    else if(params.getBoolean("enabled")) {
                        context.startForegroundService(Intent(context,TutorialService::class.java))
                        status="success"; message="Tutorial mode activation was requested. Vehicle operations have not been performed."
                    } else {
                        context.stopService(Intent(context,TutorialService::class.java))
                        status="success"; message="Tutorial mode was turned off."
                    }
                }
                "START_FEATURE_GUIDE" -> {
                    if(!params.has("feature")) { status="asking"; message="Please specify a feature." }
                    else {
                        val f=Feature.values().firstOrNull { it.name==params.optString("feature") }
                        if(f==null) message="The feature value is unsupported."
                        else if(service==null) message="Please enable tutorial mode first."
                        else if(service.startFeature(f,source)) { status="success"; message="The guide session was started. No vehicle operation has been confirmed." }
                        else message="A session is already active or the parked vehicle conditions are not met."
                    }
                }
                "RESPOND_TO_GUIDE" -> {
                    val session=service?.coordinator?.session
                    when {
                        !params.has("sessionId") || !params.has("response") -> { status="asking"; message="A session ID and response are required." }
                        params.opt("sessionId") !is String || params.opt("response") !is String -> message="Session ID and response must be strings."
                        session==null || session.id!=params.getString("sessionId") -> message="The session has expired or does not match."
                        params.getString("response").length !in 1..300 -> message="The response length is invalid."
                        session.phase==Phase.EXECUTING -> message="The existing operation is still pending. No duplicate operation was started."
                        else -> { service.input(params.getString("response"),source); status="success"; message="The response was accepted by the guide. This does not confirm vehicle execution." }
                    }
                }
                else -> message="Unknown action."
            }
            service?.coordinator?.session?.let { data.put("sessionId",it.id).put("phase",it.phase.name).put("feature",it.feature.name) }
        } catch(e:Exception) { message="The request was invalid or could not be processed."; evidence.event("GLEO_ACTION_ERROR",source,e.toString()) }
        val response=JSONObject().put("functionName",action).put("status",status).put("message",message)
            .put("mode","silent").put("data","[$data]")
        context.sendBroadcast(Intent("ai.pleos.playground.intent.action.APP_ACTION_RESPONSE").putExtra("packageName",context.packageName).putExtra("response",response.toString()))
        evidence.event("GLEO_CALLBACK_SENT",source,response.toString())
        // callback sent != Gleo received; actual natural-language end-to-end trial is separate.
    }
}
