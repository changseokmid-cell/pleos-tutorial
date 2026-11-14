package kr.pleosguide

import android.content.Context
import kotlinx.coroutines.*
import java.util.UUID
import kotlin.math.abs

class TutorialCoordinator(private val context: Context, private val scope: CoroutineScope,
    private val repository: VehicleContextRepository, private val speech: SpeechSession, private val evidence: EvidenceRecorder) {
    private val learning = LearningStore(context)
    var session: TutorialSession? = null; private set
    var latest: ContextSnapshot? = null; private set
    private var wasParked: Boolean? = null
    private var observedDrivingMs = 0L
    private var lastSampleAt = 0L
    private var previousSignature = ""
    private var actionJob: Job? = null
    private fun record(kind: String, source: SourceType, detail: String) = evidence.event(kind, source, detail, session?.id)
    private fun show(text: String, speak: Boolean = true, listenAfter: Boolean = false) {
        context.state().edit().putString("message", text).putString("feature", session?.feature?.title ?: "필요한 순간, 내 차 사용 안내")
            .putString("sessionId", session?.id ?: "").putString("phase", session?.phase?.name ?: "IDLE").putString("history", learning.summary()).apply()
        record("GUIDANCE", SourceType.LIVE_SDK, text)
        if (speak) speech.speak(text, if (listenAfter) ({ if (session != null) speech.listen() }) else null)
    }
    fun sample(snapshot: ContextSnapshot) {
        latest = snapshot
        val now = System.currentTimeMillis()
        if (wasParked == false && snapshot.parked == false && lastSampleAt > 0 && now-lastSampleAt < 10000) observedDrivingMs += now-lastSampleAt
        val parkedTransition = wasParked == false && snapshot.parked == true
        wasParked = snapshot.parked; lastSampleAt=now
        val signature = snapshot.samples.mapValues { it.value.value }.toString()
        if (signature != previousSignature) { record("SNAPSHOT", SourceType.LIVE_SDK, snapshot.samples.toString()); previousSignature = signature }
        context.state().edit().putString("context", "${if (snapshot.parked == true) "P · 정차" else if (snapshot.parked == false) "주행 상태" else "기어 확인 중"}   ·   SYNC ${snapshot.value<Boolean>("sync") ?: "—"}   ·   동승석 ${snapshot.value<Boolean>("passengerOccupied") ?: "미확인"}")
            .putString("driverTemp", snapshot.value<Float>("driverTemp")?.toString() ?: "—")
            .putString("passengerTemp", snapshot.value<Float>("passengerTemp")?.toString() ?: "—")
            .putBoolean("safeDetails", snapshot.safeDetails).apply()
        val s=session
        if (s != null) {
            if (now > s.expiresAt) { finish("무응답으로 안내를 마쳤습니다. 필요할 때 다시 불러 주세요."); return }
            if (!snapshot.safeDetails && s.phase != Phase.HANDED_OFF) {
                // First release supports detailed learning/vehicle commands while parked only.
                actionJob?.cancel(); finish("주행 중에는 자세한 체험 안내를 멈춥니다. 정차 후 이어 주세요."); return
            }
            if (s.feature == Feature.SYNC && s.phase == Phase.GUIDING && snapshot.syncReady && snapshot.value<Boolean>("sync") == false &&
                s.target != null && s.baselineDriver != null && abs((snapshot.value<Float>("passengerTemp") ?: -100f)-s.target!!) < .1f &&
                abs((snapshot.value<Float>("driverTemp") ?: -100f)-s.baselineDriver!!) < .1f) {
                s.actionStatus=ActionStatus.CONFIRMED; learning.mark(s.feature,"action","LIVE_SDK manual change confirmed")
                s.phase=Phase.FEEDBACK; show("좌우 독립 설정을 차량 신호로 확인했습니다. 동승석은 ${s.target}도입니다. 체감은 어떠신가요?", listenAfter=true)
            }
            if (s.feature == Feature.GLEO && s.phase == Phase.HANDED_OFF && snapshot.value<Boolean>("ac") == false && s.step == 0) {
                s.step=1; learning.mark(s.feature,"action","A/C OFF observed; radio UNKNOWN")
                record("PARTIAL_OBSERVATION", SourceType.LIVE_SDK,"A/C OFF; radio UNKNOWN; causal attribution to Gleo unverified")
                show("A/C 꺼짐은 차량 신호로 확인했습니다. 라디오는 직접 듣고 확인해 주세요. 튜토리얼 응답으로 체험을 남길 수 있습니다.", speak=false)
            }
            return
        }
        if (parkedTransition && snapshot.safeDetails && (snapshot.value<Int>("tripMinutes")?.let { it >= 120 } == true || observedDrivingMs >= 120*60000L) && now-learning.seen(Feature.ERGO) > 24*3600000L) {
            start(Feature.ERGO, "P transition;tripMinutes=${snapshot.value<Int>("tripMinutes")};appObservedDrivingMs=$observedDrivingMs", SourceType.LIVE_SDK)
        }
    }
    fun start(feature: Feature, trigger: String, source: SourceType): Boolean {
        if (session != null) { record("DUPLICATE_SUPPRESSED",source,feature.name); return false }
        if (!context.settings().getBoolean("enabled.${feature.name}",true)) { show("이 기능의 안내가 꺼져 있습니다."); return false }
        val c=latest
        if (c?.safeDetails != true) { show("차량 상태와 정차 조건을 확인한 뒤 체험을 시작할 수 있습니다."); return false }
        if (feature == Feature.SYNC && !c.syncReady) { show("동승석 착좌와 공조 전원, 좌우 온도를 확인하지 못했습니다."); return false }
        if (feature == Feature.SPREAD && c.value<Boolean>("power") != true) { show("공조 전원을 확인한 뒤 직풍 안내를 시작해 주세요."); return false }
        val s=TutorialSession(UUID.randomUUID().toString(),feature,trigger,expiresAt=System.currentTimeMillis()+90000)
        s.baselineDriver=c.value("driverTemp"); s.baselinePassenger=c.value("passengerTemp")
        session=s; learning.mark(feature,"offered",trigger); record("OFFER",source,trigger)
        val text=when(feature) {
            Feature.SYNC -> {
                s.target = (s.baselinePassenger!!+3f).coerceAtMost(28f)
                "동승석 온도를 따로 조절할 수 있어요. 운전석 ${s.baselineDriver}도는 유지하고, 동승석을 ${s.target}도로 바꿔 볼까요? 원하는 온도를 말하거나 수락해 주세요."
            }
            Feature.ERGO -> "정차하셨네요. 에르고 모션 시트가 장착되어 있다면 피로 완화 스트레칭을 체험할 수 있어요. 시트 옆 버튼 사용법을 안내할까요?"
            Feature.SOUND -> "뒤쪽 음악이 크다는 요청에는 전체 음량 대신 소리의 중심을 앞으로 옮기는 방법이 있어요. 사운드 위치 설정을 안내할까요?"
            Feature.SPREAD -> "얼굴에 직접 닿는 바람이 불편하군요. 전동 에어벤트가 있다면 온도 대신 바람을 분산하는 SPREAD를 선택할 수 있어요. 안내할까요?"
            Feature.GLEO -> "에어컨과 라디오를 따로 조작하려면, Gleo에 한 문장으로 부탁하는 방법을 익혀 보세요. 사용법을 안내할까요?"
        }
        show(text,listenAfter=true); return true
    }
    fun input(text: String, source: SourceType) {
        record("INPUT",source,text)
        val s=session
        if (s == null) {
            val f=Utterances.feature(text)
            if (f != null) start(f,text,source) else show("동승석 온도, 시트 스트레칭, 뒤쪽 음악, 얼굴로 오는 바람, 에어컨과 라디오 중 불편한 점을 말해 주세요.")
            return
        }
        if (Utterances.negative(text)) { finish("안내를 취소했습니다. 설정을 추가로 바꾸지 않습니다."); return }
        if (s.phase == Phase.EXECUTING) { record("DUPLICATE_SUPPRESSED",source,"action in progress"); return }
        if (System.currentTimeMillis() > s.expiresAt) { finish("응답 시간이 지나 체험을 마쳤습니다."); return }
        s.expiresAt=System.currentTimeMillis()+90000
        if (s.phase == Phase.FEEDBACK || s.phase == Phase.HANDED_OFF) {
            learning.mark(s.feature,"experience","${source.name}:$text")
            record("EXPERIENCE_REPORT",source,"$text;not_sensor_confirmation")
            if (text.contains("다음") || text.contains("혼자") || text.contains("다시")) learning.mark(s.feature,"reuse","USER_REPORT:$text")
            finish("말씀하신 체감을 기록했습니다. 다음에 스스로 사용해 보셨다면 다시 알려 주세요."); return
        }
        if (s.phase == Phase.GUIDING) {
            if (s.feature == Feature.SOUND && s.step == 0) {
                learning.mark(s.feature,"positionExperience","${source.name}:$text"); record("POSITION_REPORT",source,text)
                s.step=1
                show("위치 체험을 기록했습니다. 음장을 비교하기 전에는 소리 위치를 가운데로 복원해 주세요. 복원하셨다면 '가운데로 했어요'라고 말씀해 주세요.",listenAfter=true); return
            }
            if (s.feature == Feature.SOUND && s.step == 1) {
                if (!text.contains("가운데") && !text.contains("복원")) { show("음장 비교 전에 위치를 가운데로 복원했는지 먼저 알려 주세요.",listenAfter=true); return }
                s.step=2; s.phase=Phase.FEEDBACK
                record("CENTER_RESTORED_REPORT",source,text)
                show("사운드 설정에서 실제 장착된 음장 효과를 확인하세요. 같은 스테레오 곡과 음량으로 효과를 껐다 켜며 비교해 보세요. Centerpoint는 멀티채널 음원에 동작하지 않습니다. 메뉴가 없으면 건너뛰세요. 차이는 어떤가요?",listenAfter=true); return
            }
            s.phase=Phase.FEEDBACK
            learning.mark(s.feature,"manualOperationReport","${source.name}:$text"); record("MANUAL_OPERATION_REPORT",source,text)
            val extra = when(s.feature) {
                Feature.ERGO -> "버튼은 전신, 허리, 골반, 꺼짐 순서입니다. 전신에서 끝내려면 세 번 더 누르세요. 몸을 받치는 느낌은 어떤가요?"
                Feature.SPREAD -> {
                    val c=latest
                    val unchanged=c?.coherent==true && c.value<Float>("driverTemp")==s.baselineDriver && c.value<Float>("passengerTemp")==s.baselinePassenger
                    record("TEMPERATURE_OBSERVATION",SourceType.LIVE_SDK,"unchanged=$unchanged;SPREAD mode UNKNOWN")
                    if(unchanged) "좌우 목표 온도는 유지된 것을 확인했습니다. 바람 느낌은 어떤가요?" else "현재 목표 온도를 확인해 주세요. 바람 느낌은 어떤가요?"
                }
                else -> "사용하신 결과를 말씀해 주세요. 차량 신호로 확인되지 않은 부분은 체감 응답으로만 기록합니다."
            }
            show(extra,listenAfter=true); return
        }
        val requested=Utterances.temperature(text)
        if (s.feature == Feature.SYNC && requested != null && requested != s.target) {
            if (requested !in 16f..32f) { show("차량에서 지원하는 온도를 말씀해 주세요.",listenAfter=true); return }
            s.target=requested; show("운전석 ${s.baselineDriver}도는 유지하고 동승석을 ${requested}도로 설정할까요?",listenAfter=true); return
        }
        if (!Utterances.accept(text)) { show("체험하려면 '네', 중단하려면 '취소'라고 말씀해 주세요.",listenAfter=true); return }
        s.consent=true; learning.mark(s.feature,"accepted",source.name); record("CONSENT",source,"target=${s.target}")
        if (latest?.safeDetails != true) { finish("정차 조건이 바뀌어 체험을 중단했습니다."); return }
        when(s.feature) {
            Feature.SYNC -> {
                s.phase=Phase.EXECUTING; show("지원 여부를 확인하고 동승석 온도를 요청합니다. 반영값을 다시 확인하겠습니다.")
                actionJob=scope.launch {
                    val result=try { repository.independentTemperature(s.target!!,s.baselineDriver!!,s.id) }
                        catch(e:CancellationException) { throw e }
                        catch(e:Exception) { record("ACTION_ERROR",SourceType.LIVE_SDK,e.toString()); ActionResult(ActionStatus.UNKNOWN,"요청 결과를 확인하지 못했습니다. 공조 화면을 확인해 주세요.") }
                    if (session?.id != s.id) return@launch
                    s.actionStatus=result.status; learning.mark(s.feature,"action",result.status.name)
                    record("ACTION_RESULT",SourceType.LIVE_SDK,"${result.status}:${result.reason}")
                    s.phase=if(result.status==ActionStatus.CONFIRMED) Phase.FEEDBACK else Phase.GUIDING
                    show(result.reason + if(result.status==ActionStatus.CONFIRMED) " 체감은 어떠신가요?" else "",listenAfter=result.status==ActionStatus.CONFIRMED)
                }
            }
            Feature.ERGO -> { s.phase=Phase.GUIDING; show("장착 차량의 시트 옆 피로 완화 스트레칭 버튼을 한 번 눌러 주세요. 전신 모드에서는 쿠션과 허리 지지가 순차적으로 움직입니다. 실제 버튼과 움직임을 확인한 뒤 말씀해 주세요.",listenAfter=true) }
            Feature.SOUND -> { s.phase=Phase.GUIDING; show("설정, 사운드의 위치 메뉴에서 중심점을 앞쪽으로 옮겨 보세요. 같은 곡과 음량을 유지하며 앞과 뒤에서 들리는 차이를 확인해 주세요. 음장은 위치 체험 뒤에 따로 비교합니다.",listenAfter=true) }
            Feature.SPREAD -> { s.phase=Phase.GUIDING; show("공조 화면의 자동 풍향 모드에서 SPREAD, 승객 회피 모드를 선택해 주세요. 좌우 설정 온도는 그대로 두세요. 메뉴가 없으면 장착 사양을 먼저 확인하세요. 선택하셨다면 알려 주세요.",listenAfter=true) }
            Feature.GLEO -> {
                s.phase=Phase.HANDED_OFF; s.expiresAt=System.currentTimeMillis()+180000
                show("헤이 글레오, 에어컨 끄고 라디오 켜줘, 라고 직접 말씀해 보세요. A/C와 송풍 전원은 서로 다릅니다. 이제 마이크를 Gleo에 양보합니다.",speak=false)
                speech.speak(context.state().getString("message","")!!) { speech.yieldToGleo() }
                // speak() may fail before callback; release immediately on explicit handoff below or timeout.
            }
        }
    }
    fun finish(message: String) {
        actionJob?.cancel(); actionJob=null
        record("SESSION_END",SourceType.LIVE_SDK,message); session?.phase=Phase.ENDED
        session=null; speech.stop(); show(message,speak=false)
    }
    fun close() { finish("튜토리얼 모드가 꺼졌습니다.") }
}
