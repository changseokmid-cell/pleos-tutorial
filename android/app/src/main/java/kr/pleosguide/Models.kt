package kr.pleosguide

enum class SourceType { LIVE_SDK, LIVE_STT, LIVE_GLEO, UNVERIFIED_INTENT, TEST_PCM, MOCK_EVENT, USER_REPORT, MANUAL_OBSERVATION }
enum class Feature(val title: String) { SYNC("좌석별 독립 온도"), ERGO("시트 스트레칭"), SOUND("사운드 위치·음장"), SPREAD("직풍 피하기"), GLEO("한 문장으로 두 가지 요청") }
enum class Phase { PROPOSED, EXECUTING, GUIDING, FEEDBACK, HANDED_OFF, ENDED }
enum class ActionStatus { REQUESTED, CONFIRMED, FAILED, UNKNOWN }
data class VehicleSample<T>(val name: String, val value: T?, val unit: String = "", val area: String = "global",
    val observedAt: Long = System.currentTimeMillis(), val capability: String = "UNKNOWN", val error: String? = null,
    val sourceType: SourceType = SourceType.LIVE_SDK) {
    fun valid(now: Long = System.currentTimeMillis()) = value != null && error == null && now - observedAt in 0..5000
}
data class ContextSnapshot(val samples: Map<String, VehicleSample<*>>, val startedAt: Long, val endedAt: Long) {
    @Suppress("UNCHECKED_CAST") fun <T> value(name: String): T? = samples[name]?.takeIf { it.valid() }?.value as? T
    val coherent get() = endedAt - startedAt < 3000 && System.currentTimeMillis() - endedAt in 0..5000
    val parked get() = value<Boolean>("parked")
    val safeDetails get() = coherent && parked == true && value<Boolean>("uxRestricted") == false
    val syncReady get() = safeDetails && value<Boolean>("passengerOccupied") == true && value<Boolean>("power") == true &&
        value<Boolean>("sync") != null && value<Float>("driverTemp") != null && value<Float>("passengerTemp") != null
}
data class TutorialSession(val id: String, val feature: Feature, val triggerEvidence: String,
    var phase: Phase = Phase.PROPOSED, var consent: Boolean = false, var expiresAt: Long,
    var target: Float? = null, var baselineDriver: Float? = null, var baselinePassenger: Float? = null,
    var step: Int = 0, var actionStatus: ActionStatus = ActionStatus.UNKNOWN)
data class ActionResult(val status: ActionStatus, val reason: String, val after: ContextSnapshot? = null)

/** Explicit utterances only. No inferred pain, thoughts or speaker-seat detection. */
object Utterances {
    fun feature(text: String): Feature? = when {
        Regex("직풍|얼굴.*바람|바람.*얼굴|스프레드|SPREAD", RegexOption.IGNORE_CASE).containsMatchIn(text) -> Feature.SPREAD
        Regex("동승석|조수석|싱크|SYNC", RegexOption.IGNORE_CASE).containsMatchIn(text) -> Feature.SYNC
        Regex("스트레칭|에르고|허리.*뻐근").containsMatchIn(text) -> Feature.ERGO
        Regex("뒷.*음악|뒤.*음악|소리.*앞|사운드|음장").containsMatchIn(text) -> Feature.SOUND
        Regex("라디오.*에어컨|에어컨.*라디오|복합|멀티.*명령").containsMatchIn(text) -> Feature.GLEO
        else -> null
    }
    fun temperature(text: String): Float? = Regex("(?<![0-9])([1-3][0-9](?:\\.[05])?)\\s*도").find(text)?.groupValues?.get(1)?.toFloatOrNull()
    fun negative(text: String) = Regex("안 할|하지 마|싫|취소|그만|나중|아니|거절").containsMatchIn(text)
    fun accept(text: String) = Regex("^(네|예|응|좋아|그래)|해 보|해봐|해 봐|시작|수락|바꿔|맞아").containsMatchIn(text)
}
