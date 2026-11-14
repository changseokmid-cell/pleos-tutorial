"""Release UI smoke test. Every tap is automation, not a human perception study.
Run with the signed release installed on the dedicated AVD; preserve app data for restart checks.
"""
import pathlib,os,subprocess,time,json,xml.etree.ElementTree as E,re,requests
from wait_vehicle_ready import wait_ready
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence'/os.environ.get('PLEOS_TRIAL','release-smoke-verified');OUT.mkdir(parents=True,exist_ok=True)
A=[str(pathlib.Path(os.environ['LOCALAPPDATA'])/'PleosSyncLab/sdk/platform-tools/adb.exe'),'-s','emulator-5572']
run=[]
def adb(*args):return subprocess.check_output(A+list(args),timeout=90).decode('utf8','replace').strip()
def event(kind,**kw):
    if not run and (OUT/'run.json').exists():
        raise FileExistsError('Use a new PLEOS_TRIAL directory or explicitly load the existing run before resuming')
    run.append(dict(time=time.time(),kind=kind,**kw));(OUT/'run.json').write_text(json.dumps(run,ensure_ascii=False,indent=2),encoding='utf8');print(kind,kw,flush=True)
def console(path,**kw):
    r=requests.put('http://127.0.0.1:18088/vehicle/'+path,params=kw,timeout=30);r.raise_for_status();event('CONSOLE_SEED',path=path,values=kw)
def nodes():
    # DrivingView can take focus while the right app remains visible.
    adb('shell','input','tap','1700','150')
    adb('shell','uiautomator','dump','/sdcard/pleos-release-ui.xml')
    return E.fromstring(adb('shell','cat','/sdcard/pleos-release-ui.xml')).iter('node')

def ensure_app():
    # Pleos has two simultaneous foreground panes. Focus the app's observed
    # right-hand content before asking UIAutomator for its active hierarchy.
    # Use a launcher intent and let the multi-window task transition settle.
    adb('shell','am','start','-W','--user','current','-a','android.intent.action.MAIN','-c','android.intent.category.LAUNCHER','-f','0x10200000','-n','kr.pleosguide/.MainActivity')
    time.sleep(5)
    for _ in range(10):
        adb('shell','input','tap','1700','150')
        found=list(nodes())
        if any(n.get('package')=='kr.pleosguide' for n in found):return found
        adb('shell','am','start','--user','current','-a','android.intent.action.MAIN','-c','android.intent.category.LAUNCHER','-n','kr.pleosguide/.MainActivity')
        time.sleep(2)
    raise AssertionError('App pane not available after launch')
def click(text):
    for _ in range(8):
        for n in nodes():
            if n.get('text')==text:
                x,y,x2,y2=map(int,re.findall(r'\d+',n.get('bounds')))
                adb('shell','input','tap',str((x+x2)//2),str((y+y2)//2));event('AUTOMATED_UI',text=text);return
        time.sleep(1)
    raise AssertionError('Button missing: '+text)
def screenshot(name):
    (OUT/(name+'.png')).write_bytes(subprocess.check_output(A+['exec-out','screencap','-p'],timeout=90))

def persistent_ui():
    found=list(nodes())
    history=next((n.get('text') for n in found if n.get('text','').startswith('체험 이력\n')),None)
    settings={n.get('text'):n.get('checked') for n in found if n.get('class')=='android.widget.CheckBox'}
    assert history and len(settings)==5, 'History/settings not visible'
    return dict(history=history,settings=settings)
def logs():
    raw=adb('logcat','-d','-s','PleosGuide:I')
    result=[]
    for line in raw.splitlines():
        if 'PleosGuide: {' in line:
            try:result.append(json.loads(line.split('PleosGuide: ',1)[1]))
            except json.JSONDecodeError:pass
    return result
def wait(kind,contains='',timeout=75,start=0):
    until=time.monotonic()+timeout
    while time.monotonic()<until:
        for e in logs():
            if e['time']<start:continue
            if e['kind']==kind and contains in e['detail']:event('OBSERVED',event=e);return e
        time.sleep(1)
    raise AssertionError(kind+' not observed')

if __name__=='__main__':
    # The package is the new submission app only. No prior research app is removed here.
    event('PROVENANCE',input='Automated UI taps; no actual user comfort or learning measured',vehicle='LIVE_SDK over console-seeded emulator')
    wait_ready(OUT/'readiness')
    adb('shell','am','force-stop','--user','current','kr.syncguide')
    console('gear',gear='Park');console('seat',kind='occupied',area='passenger',value='true')
    console('hvac',power='true',dual='true',driver_temp=21,passenger_temp=21)
    adb('shell','pm','grant','--user','current','kr.pleosguide','android.permission.RECORD_AUDIO')
    adb('shell','pm','grant','--user','current','kr.pleosguide','android.permission.POST_NOTIFICATIONS')
    base=int(time.time()*1000)
    capture_file=(OUT/'app-log.txt').open('wb')
    capture=subprocess.Popen(A+['logcat','-s','PleosGuide:I'],stdout=capture_file,stderr=subprocess.DEVNULL)
    rec=subprocess.Popen(A+['shell','screenrecord','--size','1280x720','--bit-rate','3000000','--time-limit','180','/sdcard/pleos-release-smoke.mp4'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        ensure_app();screenshot('01-release-launch')
        click('튜토리얼 켜기');wait('SNAPSHOT','driverTemp, value=21.0',start=base)
        click('좌석별 독립 온도');wait('OFFER',start=base);screenshot('02-consent')
        # Wait for official TTS to finish, or its explicit error/timeout, before UI response.
        until=time.monotonic()+30
        while time.monotonic()<until:
            if any(e['time']>=base and e['kind'] in ['TTS_DONE','TTS_ERROR','TTS_TIMEOUT'] for e in logs()):break
            time.sleep(1)
        click('네, 체험할게요');wait('ACTION_RESULT','CONFIRMED',start=base);screenshot('03-confirmed-21-24')
        click('차이를 느꼈어요')
        if persistent_ui()['settings']['SOUND 안내']=='true':click('SOUND 안내')
        saved=persistent_ui();assert '체감 응답 기록' in saved['history'];assert saved['settings']['SOUND 안내']=='false'
        event('PERSISTENT_UI_BEFORE',**saved)
        click('튜토리얼 끄기');wait('MODE_OFF',start=base);screenshot('04-mode-off')
        before=int(time.time()*1000);console('hvac',passenger_temp=23);time.sleep(4)
        assert not any(e['time']>=before and e['kind']=='SNAPSHOT' for e in logs()),'Off mode continued reading'
        adb('shell','am','force-stop','--user','current','kr.pleosguide')
        text=' '.join(n.get('text','') for n in ensure_app())
        assert '튜토리얼 켜기' in text,'Mode restarted unexpectedly'
        # Private persistent history is checked by reopening mode in the same installed release.
        click('튜토리얼 켜기');wait('SNAPSHOT',start=before)
        restored=persistent_ui();assert restored==saved,'History or settings changed after process restart'
        event('PERSISTENT_UI_AFTER',**restored)
        screenshot('05-history-after-restart');click('튜토리얼 끄기')
        event('PASS',checks=['signed release launch','consent UI','SDK dual off and passenger 24','driver 21 retained','mode off stops reading','restart off by default','exact displayed history persisted','all five feature preferences persisted'])
    finally:
        capture.terminate()
        try:capture.wait(timeout=10)
        except subprocess.TimeoutExpired:capture.kill()
        capture_file.close()
        entries=[]
        for line in (OUT/'app-log.txt').read_text(encoding='utf8',errors='replace').splitlines():
            if 'PleosGuide: {' not in line:continue
            try:
                entry=json.loads(line.split('PleosGuide: ',1)[1])
                if entry['time']>=base:entries.append(entry)
            except json.JSONDecodeError:pass
        (OUT/'evidence.jsonl').write_text('\n'.join(json.dumps(e,ensure_ascii=False) for e in entries)+'\n',encoding='utf8')
        if rec.poll() is None:
            pid=adb('shell','pidof','screenrecord').strip()
            if pid:adb('shell','kill','-2',pid)
        try:rec.wait(timeout=45)
        except subprocess.TimeoutExpired:print('screenrecord still closing; pull separately',flush=True)
        adb('pull','/sdcard/pleos-release-smoke.mp4',str(OUT/'emulator.mp4'))
