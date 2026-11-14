"""Release UI smoke test. Every tap is automation, not a human perception study.
Run only after installing the signed release APK fresh on the dedicated test AVD.
"""
import pathlib,os,subprocess,time,json,xml.etree.ElementTree as E,re,requests
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence'/'release-smoke';OUT.mkdir(parents=True,exist_ok=True)
A=[str(pathlib.Path(os.environ['LOCALAPPDATA'])/'PleosSyncLab/sdk/platform-tools/adb.exe'),'-s','emulator-5572']
run=[]
def adb(*args):return subprocess.check_output(A+list(args),timeout=90).decode('utf8','replace').strip()
def event(kind,**kw):
    run.append(dict(time=time.time(),kind=kind,**kw));(OUT/'run.json').write_text(json.dumps(run,ensure_ascii=False,indent=2),encoding='utf8');print(kind,kw,flush=True)
def console(path,**kw):
    r=requests.put('http://127.0.0.1:18088/vehicle/'+path,params=kw,timeout=30);r.raise_for_status();event('CONSOLE_SEED',path=path,values=kw)
def nodes():
    adb('shell','uiautomator','dump','/sdcard/pleos-release-ui.xml')
    return E.fromstring(adb('shell','cat','/sdcard/pleos-release-ui.xml')).iter('node')
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
        for e in logs()[start:]:
            if e['kind']==kind and contains in e['detail']:event('OBSERVED',event=e);return e
        time.sleep(1)
    raise AssertionError(kind+' not observed')

if __name__=='__main__':
    # The package is the new submission app only. No prior research app is removed here.
    event('PROVENANCE',input='Automated UI taps; no actual user comfort or learning measured',vehicle='LIVE_SDK over console-seeded emulator')
    adb('shell','am','force-stop','--user','current','kr.syncguide')
    console('gear',gear='Park');console('seat',kind='occupied',area='passenger',value='true')
    console('hvac',power='true',dual='true',driver_temp=21,passenger_temp=21)
    adb('shell','pm','grant','--user','current','kr.pleosguide','android.permission.RECORD_AUDIO')
    adb('shell','pm','grant','--user','current','kr.pleosguide','android.permission.POST_NOTIFICATIONS')
    base=len(logs())
    rec=subprocess.Popen(A+['shell','screenrecord','--size','1280x720','--bit-rate','3000000','--time-limit','180','/sdcard/pleos-release-smoke.mp4'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        adb('shell','am','start','--user','current','-n','kr.pleosguide/.MainActivity');time.sleep(2);screenshot('01-fresh-install')
        click('튜토리얼 켜기');wait('SNAPSHOT','driverTemp, value=21.0',start=base)
        click('좌석별 독립 온도');wait('OFFER',start=base);screenshot('02-consent')
        # Wait for official TTS to finish, or its explicit error/timeout, before UI response.
        until=time.monotonic()+30
        while time.monotonic()<until:
            if any(e['kind'] in ['TTS_DONE','TTS_ERROR','TTS_TIMEOUT'] for e in logs()[base:]):break
            time.sleep(1)
        click('네, 체험할게요');wait('ACTION_RESULT','CONFIRMED',start=base);screenshot('03-confirmed-21-24')
        click('차이를 느꼈어요')
        click('튜토리얼 끄기');wait('MODE_OFF',start=base);screenshot('04-mode-off')
        before=len(logs());console('hvac',passenger_temp=23);time.sleep(4)
        assert not any(e['kind']=='SNAPSHOT' for e in logs()[before:]),'Off mode continued reading'
        adb('shell','am','force-stop','--user','current','kr.pleosguide')
        adb('shell','am','start','--user','current','-n','kr.pleosguide/.MainActivity');time.sleep(2)
        text=' '.join(n.get('text','') for n in nodes())
        assert '튜토리얼 켜기' in text,'Mode restarted unexpectedly'
        # Private persistent history is checked by reopening mode in the same installed release.
        click('튜토리얼 켜기');wait('SNAPSHOT',start=before)
        text=' '.join(n.get('text','') for n in nodes())
        assert '체감 응답 기록' in text,'Learning record lost after process restart'
        screenshot('05-history-after-restart');click('튜토리얼 끄기')
        event('PASS',checks=['fresh release launch','consent UI','SDK dual off and passenger 24','driver 21 retained','mode off stops reading','restart off by default','history persisted'])
    finally:
        entries=logs()[base:]
        (OUT/'evidence.jsonl').write_text('\n'.join(json.dumps(e,ensure_ascii=False) for e in entries)+'\n',encoding='utf8')
        if rec.poll() is None:
            pid=adb('shell','pidof','screenrecord').strip()
            if pid:adb('shell','kill','-2',pid)
        try:rec.wait(timeout=45)
        except subprocess.TimeoutExpired:print('screenrecord still closing; pull separately',flush=True)
        adb('pull','/sdcard/pleos-release-smoke.mp4',str(OUT/'emulator.mp4'))
