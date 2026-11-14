package kr.pleosguide

import android.app.*
import android.content.Intent
import android.os.IBinder
import kotlinx.coroutines.*

class TutorialService : Service() {
    companion object { var current: TutorialService? = null; private set }
    private val scope=CoroutineScope(SupervisorJob()+Dispatchers.Main.immediate)
    private lateinit var evidence: EvidenceRecorder
    private lateinit var repository: VehicleContextRepository
    private lateinit var speech: SpeechSession
    lateinit var coordinator: TutorialCoordinator; private set
    override fun onCreate() {
        super.onCreate()
        val manager=getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(NotificationChannel("guide","차량 기능 안내",NotificationManager.IMPORTANCE_LOW))
        val open=PendingIntent.getActivity(this,0,Intent(this,MainActivity::class.java),PendingIntent.FLAG_IMMUTABLE)
        val listen=PendingIntent.getService(this,1,Intent(this,TutorialService::class.java).setAction("LISTEN"),PendingIntent.FLAG_IMMUTABLE)
        val stop=PendingIntent.getService(this,2,Intent(this,TutorialService::class.java).setAction("STOP"),PendingIntent.FLAG_IMMUTABLE)
        startForeground(25,Notification.Builder(this,"guide").setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("내 차 사용 안내 켜짐").setContentText("필요할 때 말하기를 눌러 짧게 요청하세요.").setContentIntent(open)
            .addAction(Notification.Action.Builder(null,"말하기",listen).build())
            .addAction(Notification.Action.Builder(null,"끄기",stop).build()).setOngoing(true).build())
        evidence=EvidenceRecorder(this); repository=VehicleContextRepository(this,evidence)
        speech=SpeechSession(this,evidence) { text,source -> coordinator.input(text,source) }
        coordinator=TutorialCoordinator(this,scope,repository,speech,evidence)
        current=this; state().edit().putBoolean("active",true).apply()
        evidence.event("MODE_ON",SourceType.USER_REPORT,"user-started foreground service")
        scope.launch {
            repository.initialize()
            withContext(Dispatchers.IO) { repository.probe() }
            var nextProbe=System.currentTimeMillis()+30000
            while(isActive) {
                try {
                    if(System.currentTimeMillis()>=nextProbe) { withContext(Dispatchers.IO) { repository.probe() }; nextProbe=System.currentTimeMillis()+30000 }
                    coordinator.sample(withContext(Dispatchers.IO) { repository.snapshot() })
                } catch(e:CancellationException) { throw e } catch(e:Exception) { evidence.event("POLL_ERROR",SourceType.LIVE_SDK,e.toString()) }
                delay(1000)
            }
        }
    }
    override fun onStartCommand(intent: Intent?, flags:Int, startId:Int):Int {
        when(intent?.action) {
            "STOP" -> stopSelf()
            "LISTEN" -> speech.listen()
            "YIELD" -> speech.yieldToGleo()
            "SPEAK_TEST" -> speech.speak("내 차 사용 안내입니다. 한국어 음성 출력을 확인합니다.")
        }
        return START_NOT_STICKY
    }
    fun input(text:String,source:SourceType=SourceType.USER_REPORT) { speech.stop(); coordinator.input(text,source) }
    fun startFeature(feature:Feature,source:SourceType=SourceType.USER_REPORT) = coordinator.start(feature,"explicit request",source)
    fun cancel() = coordinator.finish("안내를 취소했습니다.")
    fun testPcm(bytes:ByteArray) { if(BuildConfig.DEBUG) speech.testPcm(bytes) }
    override fun onDestroy() {
        current=null; coordinator.close(); scope.cancel(); speech.close(); repository.close()
        state().edit().putBoolean("active",false).putBoolean("safeDetails",false).apply()
        evidence.event("MODE_OFF",SourceType.LIVE_SDK,"subscriptions, microphone, focus and foreground service released")
        super.onDestroy()
    }
    override fun onBind(intent: Intent?):IBinder? = null
}
