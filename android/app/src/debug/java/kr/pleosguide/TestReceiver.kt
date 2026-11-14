package kr.pleosguide
import android.content.*
/** Debug-only harness. It can drive real SDK operations; every input is labeled MOCK_EVENT. */
class TestReceiver:BroadcastReceiver() {
    override fun onReceive(context:Context,intent:Intent) {
        val service=TutorialService.current
        val text=intent.getStringExtra("text")
        val feature=intent.getStringExtra("feature")
        EvidenceRecorder(context).event("TEST_INJECTION",SourceType.MOCK_EVENT,"text=$text;feature=$feature")
        if(text!=null) service?.input(text,SourceType.MOCK_EVENT)
        if(feature!=null) Feature.values().firstOrNull { it.name==feature }?.let { service?.startFeature(it,SourceType.MOCK_EVENT) }
        intent.getStringExtra("command")?.let {
            if(it=="PCM") runCatching { service?.testPcm(context.assets.open("stt-test.pcm").use { stream -> stream.readBytes() }) }
                .onFailure { e -> EvidenceRecorder(context).event("TEST_PCM_ERROR",SourceType.TEST_PCM,e.toString()) }
            else context.startForegroundService(Intent(context,TutorialService::class.java).setAction(it))
        }
    }
}
