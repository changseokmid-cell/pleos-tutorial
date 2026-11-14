package kr.pleosguide

import org.junit.Assert.*
import org.junit.Test

class GuideSafetyTest {
    private fun cabin(vararg changes: Pair<String,Any?>, age:Long=0):ContextSnapshot {
        val now=System.currentTimeMillis()-age
        val values=mutableMapOf<String,Any?>("parked" to true,"uxRestricted" to false,"passengerOccupied" to true,"power" to true,"sync" to true,"driverTemp" to 21f,"passengerTemp" to 21f)
        values.putAll(changes)
        return ContextSnapshot(values.mapValues { VehicleSample(it.key,it.value,observedAt=now) },now,now)
    }
    @Test fun missingSeatIsNotEmptyOrOccupied() { assertFalse(cabin("passengerOccupied" to null).syncReady); assertFalse(cabin("passengerOccupied" to false).syncReady) }
    @Test fun unknownUxAndDrivingPreventControl() { assertFalse(cabin("uxRestricted" to null).syncReady); assertFalse(cabin("parked" to false).syncReady); assertFalse(cabin("uxRestricted" to true).syncReady) }
    @Test fun staleSnapshotCannotAuthorizeCommands() { assertFalse(cabin(age=6000).syncReady); assertTrue(cabin().syncReady) }
    @Test fun unsupportedSignalCannotBecomeFalse() { assertNull(cabin("sync" to null).value<Boolean>("sync")); assertFalse(cabin("sync" to null).syncReady) }
    @Test fun directAirAndHeatAreDifferentIntents() { assertEquals(Feature.SPREAD,Utterances.feature("시원한데 바람이 얼굴로 와요")); assertNull(Utterances.feature("덥다")) }
    @Test fun rearMusicRequestIsNotThoughtDetection() { assertEquals(Feature.SOUND,Utterances.feature("뒤에는 음악이 좀 커")); assertNull(Utterances.feature("좀 졸린데")) }
    @Test fun cancellationPrecedesAcceptance() { assertTrue(Utterances.negative("아니, 하지 마")); assertFalse(Utterances.accept("잠깐")) }
    @Test fun temperatureIsAnExplicitNumericRequest() { assertEquals(24.5f,Utterances.temperature("동승석 24.5도")!!,0f); assertNull(Utterances.temperature("따뜻하게")) }
    @Test fun multipleNativeActionsRouteToGleoLesson() { assertEquals(Feature.GLEO,Utterances.feature("에어컨 끄고 라디오 켜줘")) }
}
