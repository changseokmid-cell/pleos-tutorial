package kr.pleosguide

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.widget.*

class MainActivity:Activity(),SharedPreferences.OnSharedPreferenceChangeListener {
    private lateinit var mode:Button
    private lateinit var contextText:TextView
    private lateinit var temperatures:TextView
    private lateinit var message:TextView
    private lateinit var voice:TextView
    private lateinit var history:TextView
    private lateinit var details:LinearLayout
    private val ink=Color.rgb(229,241,240)
    private fun label(size:Float)=TextView(this).apply { textSize=size; setTextColor(ink); setPadding(8,8,8,8) }
    private fun button(text:String,click:()->Unit)=Button(this).apply { this.text=text; textSize=20f; minHeight=72; setOnClickListener{click()} }
    override fun onCreate(savedInstanceState:Bundle?) {
        super.onCreate(savedInstanceState)
        val root=LinearLayout(this).apply { orientation=LinearLayout.VERTICAL; setPadding(64,24,64,24); setBackgroundColor(Color.rgb(15,29,34)) }
        root.addView(label(34f).apply { text="내 차 사용 안내"; setTypeface(null,Typeface.BOLD) })
        root.addView(label(18f).apply { text="몰랐던 기능을, 필요한 순간에.  ·  차량 상태와 직접 말씀하신 요청을 연결합니다." })
        contextText=label(20f); root.addView(contextText)
        temperatures=label(42f); root.addView(temperatures)
        message=label(28f).apply { setTextColor(Color.rgb(137,229,210)); minHeight=130 }; root.addView(message)
        val actions=LinearLayout(this).apply { gravity=Gravity.CENTER_VERTICAL }
        mode=button("튜토리얼 켜기") {
            if(TutorialService.current!=null) stopService(Intent(this,TutorialService::class.java))
            else if(checkSelfPermission(Manifest.permission.RECORD_AUDIO)!=PackageManager.PERMISSION_GRANTED)
                requestPermissions(arrayOf(Manifest.permission.RECORD_AUDIO),70)
            else startForegroundService(Intent(this,TutorialService::class.java))
        }
        actions.addView(mode)
        actions.addView(button("말하기 · 12초") { command("LISTEN") })
        actions.addView(button("안내 취소") { TutorialService.current?.cancel() })
        actions.addView(button("Gleo에 양보") { command("YIELD") })
        root.addView(actions)
        details=LinearLayout(this).apply { orientation=LinearLayout.VERTICAL }; root.addView(details)
        val replies=LinearLayout(this)
        replies.addView(button("네, 체험할게요") { TutorialService.current?.input("네, 해 볼게요") })
        replies.addView(button("조작했어요") { TutorialService.current?.input("조작했어요") })
        replies.addView(button("가운데로 복원했어요") { TutorialService.current?.input("가운데로 복원했어요") })
        replies.addView(button("차이를 느꼈어요") { TutorialService.current?.input("차이를 느꼈어요") })
        details.addView(replies)
        val row=LinearLayout(this)
        val input=EditText(this).apply { hint="정차 중 요청 또는 체감 입력"; textSize=20f; setTextColor(ink); setHintTextColor(Color.GRAY); setSingleLine(true) }
        row.addView(input,LinearLayout.LayoutParams(0,72,1f)); row.addView(button("전달") { val t=input.text.toString(); if(t.isNotBlank()) TutorialService.current?.input(t); input.setText("") })
        details.addView(row)
        val features=LinearLayout(this)
        Feature.values().forEach { f -> features.addView(button(f.title) { TutorialService.current?.startFeature(f) },LinearLayout.LayoutParams(0,88,1f)) }
        details.addView(features)
        details.addView(label(16f).apply { text="장착 사양에 따라 안내가 달라집니다. 에르고·사운드·SPREAD는 순정 조작 안내와 체감 기록을 제공합니다." })
        val settingsRow=LinearLayout(this)
        Feature.values().forEach { f -> settingsRow.addView(CheckBox(this).apply {
            text="${f.name} 안내"; setTextColor(ink); isChecked=settings().getBoolean("enabled.${f.name}",true)
            setOnCheckedChangeListener { _, checked -> settings().edit().putBoolean("enabled.${f.name}",checked).apply() }
        }) }
        details.addView(settingsRow)
        voice=label(14f); details.addView(voice)
        history=label(16f); details.addView(history)
        if(BuildConfig.DEBUG) details.addView(button("공식 한국어 음성 확인") { command("SPEAK_TEST") })
        setContentView(ScrollView(this).apply { isFillViewport=true; addView(root) })
    }
    private fun command(action:String) { if(TutorialService.current!=null) startService(Intent(this,TutorialService::class.java).setAction(action)) }
    override fun onRequestPermissionsResult(requestCode:Int,permissions:Array<out String>,grantResults:IntArray) {
        super.onRequestPermissionsResult(requestCode,permissions,grantResults)
        if(requestCode==70) startForegroundService(Intent(this,TutorialService::class.java))
    }
    override fun onStart() { super.onStart(); state().registerOnSharedPreferenceChangeListener(this); render() }
    override fun onStop() { state().unregisterOnSharedPreferenceChangeListener(this); super.onStop() }
    override fun onSharedPreferenceChanged(p:SharedPreferences?,key:String?)=render()
    private fun render() {
        val s=state(); val active=s.getBoolean("active",false)
        mode.text=if(active) "튜토리얼 끄기" else "튜토리얼 켜기"
        contextText.text=s.getString("context","차량 상태는 모드를 켠 뒤 확인합니다.")
        temperatures.text="운전석  ${s.getString("driverTemp","—")}°     동승석  ${s.getString("passengerTemp","—")}°"
        message.text=s.getString("message","")
        details.visibility=if(s.getBoolean("safeDetails",false)) View.VISIBLE else View.GONE
        voice.text=s.getString("voice","")
        history.text="체험 이력\n"+LearningStore(this).summary()
    }
}
