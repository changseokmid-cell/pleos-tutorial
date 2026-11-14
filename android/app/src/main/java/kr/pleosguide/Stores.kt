package kr.pleosguide

import android.app.Application
import android.content.Context
import android.util.Log
import org.json.JSONObject
import java.io.File

fun Context.state() = getSharedPreferences("runtime", Context.MODE_PRIVATE)
fun Context.settings() = getSharedPreferences("settings", Context.MODE_PRIVATE)
class GuideApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        state().edit().clear().putString("message", "튜토리얼을 켜면 차량 상태에 맞춰 안내합니다.").apply()
    }
}
class EvidenceRecorder(context: Context) {
    private val file = File(context.filesDir, "evidence.jsonl")
    @Synchronized fun event(kind: String, source: SourceType, detail: String, session: String? = null) {
        val json = JSONObject().put("time", System.currentTimeMillis()).put("kind", kind).put("sourceType", source.name)
            .put("sessionId", session ?: JSONObject.NULL).put("detail", detail)
        // Bound local diagnostics; learning records are stored independently.
        if (file.length() > 8_000_000) file.renameTo(File(file.parentFile, "evidence.previous.jsonl"))
        file.appendText(json.toString() + "\n")
        Log.i("PleosGuide", json.toString())
    }
}
class LearningStore(context: Context) {
    private val prefs = context.getSharedPreferences("learning", Context.MODE_PRIVATE)
    fun seen(feature: Feature) = prefs.getLong("${feature.name}.offered", 0L)
    fun mark(feature: Feature, event: String, value: String) {
        prefs.edit().putString("${feature.name}.$event", value).putLong("${feature.name}.$event.at", System.currentTimeMillis()).apply()
        if (event == "offered") prefs.edit().putLong("${feature.name}.offered", System.currentTimeMillis()).apply()
    }
    fun summary() = Feature.values().joinToString("\n") { f ->
        "${f.title} · " + listOf("accepted", "action", "experience", "reuse").mapNotNull { key ->
            prefs.getString("${f.name}.$key", null)?.let {
                when(key) {
                    "accepted" -> "체험 수락"
                    "action" -> if(it=="CONFIRMED") "차량 상태 확인" else "실행 상태 미확인"
                    "experience" -> "체감 응답 기록"
                    else -> "다음 사용에 대한 응답 기록"
                }
            }
        }.joinToString(" / ").ifEmpty { "체험 기록 없음" }
    }
}
