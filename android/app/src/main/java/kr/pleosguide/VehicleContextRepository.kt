package kr.pleosguide

import ai.pleos.playground.vehicle.Vehicle
import ai.pleos.playground.vehicle.api.model.area.SeatArea
import ai.pleos.playground.vehicle.api.model.capability.AccessType
import ai.pleos.playground.vehicle.api.model.capability.CapabilityConfig
import ai.pleos.playground.vehicle.constant.area.SeatValue
import ai.pleos.playground.vehicle.constant.unit.TemperatureUnit
import android.car.Car
import android.car.VehicleGear
import android.car.VehiclePropertyIds
import android.car.hardware.CarPropertyValue
import android.car.hardware.property.CarPropertyManager
import android.car.drivingstate.CarUxRestrictionsManager
import android.car.media.CarAudioManager
import android.content.Context
import android.os.Build
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlin.coroutines.resume
import kotlin.math.abs

class VehicleContextRepository(private val context: Context, private val evidence: EvidenceRecorder) {
    private val sdk = Vehicle(context)
    private val left = SeatArea(SeatValue.ROW_1_LEFT)
    private val right = SeatArea(SeatValue.ROW_1_RIGHT)
    private var car: Car? = null
    private val areas = mutableMapOf<String, SeatArea>()
    private val access = mutableMapOf<String, String>()
    private val reported = mutableMapOf<String, String>()
    private val lock = Mutex()
    private var tempRange: ClosedFloatingPointRange<Float>? = null
    private var increment: Float? = null
    private val seatMapped = Build.FINGERPRINT == "Pleos/crp_avd/crp_avd_x86_64:14/RELEASE.release_connect_v2.1.0/release_connect_v2.1.0:user/test-keys"
    suspend fun initialize() = withContext(Dispatchers.IO) {
        sdk.initialize(); evidence.event("VEHICLE_INIT", SourceType.LIVE_SDK, "${Build.FINGERPRINT};seatMapping=$seatMapped")
    }
    private fun note(key: String, message: String) {
        if (reported.put(key, message) != message) evidence.event("CAPABILITY_OR_ERROR", SourceType.LIVE_SDK, "$key=$message")
    }
    private suspend fun <T> await(key: String, call: ((T?) -> Unit, (Exception) -> Unit) -> Unit): T? {
        val value = withTimeoutOrNull(1800) {
            suspendCancellableCoroutine<T?> { c ->
                try { call({ if (c.isActive) c.resume(it) }, { note(key, it.toString()); if (c.isActive) c.resume(null) }) }
                catch (e: Exception) { note(key, e.toString()); if (c.isActive) c.resume(null) }
            }
        }
        if (value == null) note("$key.null", "missing or timed out")
        return value
    }
    private suspend fun area(key: String, query: ((CapabilityConfig, List<SeatArea>) -> Unit, (Exception) -> Unit) -> Unit): SeatArea? {
        areas[key]?.let { return it }
        return await<SeatArea>(key) { ok, fail -> query({ config, list ->
            access[key] = config.accessType.toString()
            note(key, "${config.accessType};areas=${list.map { it.values.toList() }}")
            val result = list.filter { SeatValue.ROW_1_LEFT in it.values }.minByOrNull { it.values.size }
                ?.takeIf { config.accessType == AccessType.READ || config.accessType == AccessType.READ_WRITE }
            if (result != null) areas[key] = result
            ok(result)
        }, fail) }
    }
    suspend fun probe() {
        area("power", sdk.getHVAC()::checkHvacPowerCapabilities)
        area("sync", sdk.getHVAC()::checkHvacDualCapabilities)
        area("ac", sdk.getHVAC()::checkHvacAcCapabilities)
        await<Boolean>("tempCapability") { ok, fail ->
            sdk.getHVAC().checkHvacTemperatureCapabilities({ config, ranges, conversion ->
                access["temperature"] = config.accessType.toString()
                val range = ranges.entries.firstOrNull { it.key.values.toSet() == right.values.toSet() }?.value
                if (range != null) tempRange = range.minValue..range.maxValue
                increment = conversion?.incrementCelsius
                note("temperature", "${config.accessType};ranges=$ranges;conversion=$conversion")
                ok(true)
            }, fail)
        }
        await<Boolean>("tripCapability") { ok, fail -> sdk.getOdometer().checkTripCurrentDrivingTimeCapabilities({
            access["tripMinutes"] = it.accessType.toString(); note("tripMinutes", it.toString()); ok(true)
        }, fail) }
        withContext(Dispatchers.IO) {
            try {
                ensureCar()
                val audio = car?.getCarManager(Car.AUDIO_SERVICE) as? CarAudioManager
                note("audio", "managerAvailable=${audio != null};controlPermission=${context.checkSelfPermission("android.car.permission.CAR_CONTROL_AUDIO_SETTINGS")};fader and sound effects absent from public compile API; no hidden API attempted")
            } catch (e: Exception) { note("audio", e.toString()) }
        }
    }
    private fun ensureCar() { if (car == null) car = Car.createCar(context) }
    private fun carState(): Pair<Boolean?, Boolean?> {
        ensureCar()
        val parked = try {
            val m = car?.getCarManager(Car.PROPERTY_SERVICE) as? CarPropertyManager
            val v = m?.getProperty(Int::class.javaObjectType, VehiclePropertyIds.GEAR_SELECTION, 0)
            v?.takeIf { it.status == CarPropertyValue.STATUS_AVAILABLE }?.value?.let { it == VehicleGear.GEAR_PARK }
        } catch (e: Exception) { note("gear", e.toString()); null }
        val restricted = try {
            val m = car?.getCarManager(Car.CAR_UX_RESTRICTION_SERVICE) as? CarUxRestrictionsManager
            m?.currentCarUxRestrictions?.let { r ->
                note("ux", "requiresDO=${r.isRequiresDistractionOptimization};restrictions=${r.activeRestrictions}")
                r.isRequiresDistractionOptimization
            }
        } catch (e: Exception) { note("ux", e.toString()); null }
        return parked to restricted
    }
    suspend fun snapshot(): ContextSnapshot = lock.withLock { coroutineScope {
        val started = System.currentTimeMillis()
        val samples = java.util.concurrent.ConcurrentHashMap<String, VehicleSample<*>>()
        suspend fun <T> sample(key: String, unit: String = "", region: String = "global", read: suspend () -> T?) {
            val v = read()
            samples[key] = VehicleSample(key, v, unit, region, capability = access[key] ?: "READ_ATTEMPT", error = if (v == null) "unavailable" else null)
        }
        val jobs = mutableListOf<Deferred<Unit>>()
        jobs += async(Dispatchers.IO) { val (p, r) = carState(); sample("parked") { p }; sample("uxRestricted") { r } }
        for ((name, seat) in listOf("driverOccupied" to left, "passengerOccupied" to right,
            "rearLeftOccupied" to SeatArea(SeatValue.ROW_2_LEFT), "rearRightOccupied" to SeatArea(SeatValue.ROW_2_RIGHT))) {
            jobs += async { sample(name, region = seat.values.toList().toString()) {
                // The old binary console mapping was verified only for the passenger. Other seats remain raw/unknown.
                val raw = await<Boolean>(name) { ok, fail -> sdk.getSeat().getCurrentSeatOccupancy(seat, ok, fail) }
                samples["${name}Raw"] = VehicleSample("${name}Raw", raw, area = seat.values.toList().toString())
                if (name == "passengerOccupied" && seatMapped) raw?.not() else null
            } }
        }
        for (key in listOf("power", "sync", "ac")) jobs += async { sample(key, region = areas[key]?.values?.toList().toString()) {
            areas[key]?.let { a -> await<Boolean>(key) { ok, fail -> when (key) {
                "power" -> sdk.getHVAC().getHvacPowerState(a, ok, fail)
                "sync" -> sdk.getHVAC().getHvacDualState(a, ok, fail)
                else -> sdk.getHVAC().getHvacAcState(a, ok, fail)
            } } }
        } }
        for ((key, seat) in listOf("driverTemp" to left, "passengerTemp" to right)) jobs += async {
            sample(key, "C", seat.values.toList().toString()) {
                await<Float>(key) { ok, fail -> sdk.getHVAC().getHvacTemperature(seat, TemperatureUnit.CELSIUS, ok, fail) }?.takeIf { it.isFinite() }
            }
        }
        jobs += async { sample("tripMinutes", "min") { await<Int>("tripMinutes") { ok, fail -> sdk.getOdometer().getTripCurrentDrivingTime(ok, fail) }?.takeIf { it >= 0 } } }
        jobs.awaitAll()
        ContextSnapshot(samples.toMap(), started, System.currentTimeMillis())
    } }
    fun canSetTemperature(value: Float): Boolean {
        val range = tempRange ?: return false
        if (access["temperature"] != "READ_WRITE" || value !in range) return false
        val step = increment ?: return true
        if (step <= 0) return false
        val n = (value - range.start) / step
        return abs(n - kotlin.math.round(n)) < .01f
    }
    suspend fun independentTemperature(target: Float, baseline: Float, session: String): ActionResult {
        val before = snapshot()
        if (!before.syncReady || abs((before.value<Float>("driverTemp") ?: -100f) - baseline) > .1f)
            return ActionResult(ActionStatus.FAILED, "조건 또는 운전석 설정이 변경되었습니다.", before)
        if (access["temperature"] == "READ_WRITE" && !canSetTemperature(target))
            return ActionResult(ActionStatus.FAILED, "차량의 지원 온도 범위나 간격에 맞지 않습니다. 값을 확인한 뒤 새로 요청해 주세요.", before)
        if (access["sync"] != "READ_WRITE" || !canSetTemperature(target))
            return ActionResult(ActionStatus.UNKNOWN, "쓰기 권한이나 지원 온도를 확인하지 못했습니다. 공조 화면에서 SYNC를 끄고 지원되는 동승석 온도를 직접 선택해 주세요.", before)
        if (before.value<Boolean>("sync") == true) {
            evidence.event("COMMAND_REQUESTED", SourceType.LIVE_SDK, "setHvacDual(false)", session)
            val ack = await<Boolean>("setDual") { ok, fail -> sdk.getHVAC().setHvacDual(areas.getValue("sync"), false, { _, _ -> ok(true) }, fail) }
            evidence.event("COMMAND_ACK", SourceType.LIVE_SDK, "dual=$ack;not_confirmation", session)
            if (ack != true) return ActionResult(ActionStatus.UNKNOWN, "연동 해제 응답을 확인하지 못했습니다. 자동 재시도하지 않습니다.", snapshot())
            delay(350)
        }
        val unlocked = snapshot()
        evidence.event("INDEPENDENT_READ", SourceType.LIVE_SDK, unlocked.samples.toString(), session)
        if (!unlocked.syncReady || unlocked.value<Boolean>("sync") != false || abs((unlocked.value<Float>("driverTemp") ?: -100f) - baseline) > .1f)
            return ActionResult(ActionStatus.UNKNOWN, "연동 해제나 운전석 유지를 확인하지 못해 온도를 변경하지 않았습니다.", unlocked)
        evidence.event("COMMAND_REQUESTED", SourceType.LIVE_SDK, "setHvacTemperature(passenger,$target)", session)
        val ack = await<Boolean>("setTemperature") { ok, fail -> sdk.getHVAC().setHvacTemperature(right, target, TemperatureUnit.CELSIUS, { _, _ -> ok(true) }, fail) }
        evidence.event("COMMAND_ACK", SourceType.LIVE_SDK, "temperature=$ack;not_confirmation", session)
        repeat(3) {
            delay(400)
            val after = snapshot()
            evidence.event("INDEPENDENT_READ", SourceType.LIVE_SDK, after.samples.toString(), session)
            val driver = after.value<Float>("driverTemp")
            val passenger = after.value<Float>("passengerTemp")
            if (after.syncReady && after.value<Boolean>("sync") == false && driver != null && passenger != null && abs(driver-baseline)<.1f && abs(passenger-target)<.1f)
                return ActionResult(ActionStatus.CONFIRMED, "운전석 ${driver}도는 유지되고, 동승석은 ${passenger}도로 독립 설정된 것을 확인했습니다.", after)
            if (!after.syncReady || (driver != null && abs(driver-baseline)>.1f))
                return ActionResult(ActionStatus.UNKNOWN, "설정 또는 차량 조건이 바뀌었습니다. 변경 결과를 확인해 주세요.", after)
        }
        return ActionResult(ActionStatus.UNKNOWN, "요청했지만 목표값 반영은 확인되지 않았습니다. 공조 화면을 확인해 주세요.", snapshot())
    }
    fun close() { sdk.release(); car?.disconnect() }
}
