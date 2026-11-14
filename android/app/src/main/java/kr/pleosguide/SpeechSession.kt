package kr.pleosguide

import android.content.Context
import android.content.pm.PackageManager
import android.media.AudioAttributes
import android.media.AudioFocusRequest
import android.media.AudioManager
import android.os.Handler
import android.os.Looper
import ai.pleos.playground.stt.SpeechToText
import ai.pleos.playground.tts.TextToSpeech
import java.util.Locale

/** One official ON_DEVICE speech owner. No ambient listening or external STT. */
class SpeechSession(private val context: Context, private val evidence: EvidenceRecorder,
    private val onText: (String, SourceType) -> Unit) {
    private val main = Handler(Looper.getMainLooper())
    private val stt = SpeechToText(context, ai.pleos.playground.stt.constant.Mode.ON_DEVICE)
    private val tts = TextToSpeech(context, ai.pleos.playground.tts.constant.Mode.ON_DEVICE)
    private val audio = context.getSystemService(AudioManager::class.java)
    private val attributes = AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_ASSISTANCE_NAVIGATION_GUIDANCE)
        .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH).build()
    private var focus: AudioFocusRequest? = null
    private var sttReady = false
    private var ttsReady = false
    private var listening = false
    private var speaking = false
    private var closed = false
    private var done: (() -> Unit)? = null
    private var timeout: Runnable? = null
    private fun event(kind: String, detail: String, source: SourceType = SourceType.LIVE_SDK) {
        evidence.event(kind, source, detail)
        context.state().edit().putString("voice", "$kind · $detail").apply()
    }
    private val recognition = object : ai.pleos.playground.stt.listener.ResultListener {
        override fun onReady() { main.post { if (listening) event("STT_READY", "ON_DEVICE ko-KR vehicle microphone") } }
        override fun onStartedRecognition() { main.post { if (listening) event("STT_STARTED", "vehicle microphone") } }
        override fun onUpdated(stt: String, completed: Boolean) { main.post {
            if (!listening || closed) return@post
            event(if (completed) "STT_FINAL" else "STT_PARTIAL", stt, SourceType.LIVE_STT)
            if (completed) { stop(); if (stt.isNotBlank()) onText(stt, SourceType.LIVE_STT) }
        } }
        override fun onUpdatedEpdData(on: Long, off: Long) = Unit
        override fun onUpdatedRms(rms: Double) = Unit
        override fun onEndedRecognition() { main.post { if (listening) { event("STT_ENDED", "no completed text"); stop() } } }
        override fun onError(errorType: ai.pleos.playground.stt.constant.ErrorType) { main.post { event("STT_ERROR", errorType.toString()); if (listening) stop() } }
    }
    private val synthesis = object : ai.pleos.playground.tts.listener.EventListener {
        override fun onStart() { main.post { if (speaking) event("TTS_STARTED", "official ON_DEVICE") } }
        override fun onReady() = Unit
        override fun onDone() { main.post {
            if (speaking && !closed) { event("TTS_DONE", "SDK playback completion"); val next=done; done=null; stop(); next?.invoke() }
        } }
        override fun onStop() = Unit
        override fun onUpdatedRms(rms: Double) = Unit
        override fun onError(errorType: ai.pleos.playground.tts.constant.ErrorType) { main.post { event("TTS_ERROR", errorType.toString()); if (speaking) stop() } }
    }
    init {
        try {
            stt.addListener(recognition)
            tts.addEventListener(synthesis)
            stt.initialize(object : ai.pleos.playground.stt.listener.OnInitializeListener {
                override fun onSuccess() { main.post { if (!closed) { sttReady=true; stt.setLocale(Locale.KOREAN); event("STT_INIT_OK", "ON_DEVICE ko-KR") } } }
                override fun onFailure(errorType: ai.pleos.playground.stt.constant.ErrorType) { event("STT_INIT_FAILED", errorType.toString()) }
            })
            tts.initialize(object : ai.pleos.playground.tts.listener.OnInitializeListener {
                override fun onSuccess() { main.post { if (!closed) { ttsReady=true; tts.setLocale(Locale.KOREAN); tts.setAudioAttributes(attributes); event("TTS_INIT_OK", "ON_DEVICE ko-KR") } } }
                override fun onFailure(errorType: ai.pleos.playground.tts.constant.ErrorType) { event("TTS_INIT_FAILED", errorType.toString()) }
            })
        } catch (e: Exception) { event("SPEECH_INIT_EXCEPTION", e.toString()) }
    }
    private fun acquire(): Boolean {
        val request = AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN_TRANSIENT)
            .setAudioAttributes(attributes).setOnAudioFocusChangeListener { if (it < 0) { event("FOCUS_LOST", it.toString()); stop() } }.build()
        if (audio.requestAudioFocus(request) != AudioManager.AUDIOFOCUS_REQUEST_GRANTED) { event("FOCUS_DENIED", "speech deferred"); return false }
        focus=request; return true
    }
    private fun timeout(ms: Long, kind: String) {
        timeout = Runnable { event(kind, "resources released"); stop() }.also { main.postDelayed(it, ms) }
    }
    fun speak(text: String, after: (() -> Unit)? = null): Boolean {
        stop()
        if (closed || !ttsReady) { event("TTS_UNAVAILABLE", "initialization not ready; text remains visible"); return false }
        if (!acquire()) return false
        return try { speaking=true; done=after; event("TTS_REQUESTED", text); timeout(45000,"TTS_TIMEOUT"); tts.speak(text, true); true }
        catch (e: Exception) { event("TTS_EXCEPTION", e.toString()); stop(); false }
    }
    fun listen(): Boolean {
        stop()
        if (closed || !sttReady || context.checkSelfPermission("android.permission.RECORD_AUDIO") != PackageManager.PERMISSION_GRANTED) {
            event("STT_UNAVAILABLE", "initialization or microphone permission missing"); return false
        }
        if (!acquire()) return false
        return try { listening=true; event("STT_REQUESTED", "vehicle microphone; 12 seconds; ON_DEVICE ko-KR"); timeout(12000,"STT_TIMEOUT"); stt.request(); true }
        catch (e: Exception) { event("STT_EXCEPTION", e.toString()); stop(); false }
    }
    fun stop() {
        timeout?.let(main::removeCallbacks); timeout=null; done=null
        val wasListening=listening; val wasSpeaking=speaking; listening=false; speaking=false
        if (wasListening) runCatching { stt.stop() }
        if (wasSpeaking) runCatching { tts.stop() }
        focus?.let { audio.abandonAudioFocusRequest(it) }; focus=null
    }
    fun yieldToGleo() { stop(); event("AUDIO_YIELDED", "microphone and focus released for native Gleo") }
    fun close() { closed=true; stop(); runCatching { stt.removeListener(recognition); stt.release() }; runCatching { tts.removeEventListener(synthesis); tts.release() } }
}
