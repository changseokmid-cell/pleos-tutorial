"""Debug integration trials against a running PleosSync210 emulator.
Console seeds vehicle values; user responses are explicitly MOCK_EVENT.
Does not establish live microphone recognition or natural Gleo invocation.
"""
import json, os, pathlib, shlex, subprocess, time, requests, sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence'/'debug-trial'; OUT.mkdir(parents=True,exist_ok=True)
ADB=pathlib.Path(os.environ['LOCALAPPDATA'])/'PleosSyncLab/sdk/platform-tools/adb.exe'
A=[str(ADB),'-s','emulator-5572']
events=[]
def adb(*args):
    return subprocess.check_output(A+list(args),timeout=60).decode('utf8','replace').strip()
def shell(*args): return adb('shell',' '.join(shlex.quote(str(a)) for a in args))
def record(kind, **values):
    entry=dict(time=time.time(),kind=kind,**values); events.append(entry)
    (OUT/'run.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf8')
    print(kind,values,flush=True)
def console(path,**params):
    response=requests.put('http://127.0.0.1:18088/vehicle/'+path,params=params,timeout=20)
    response.raise_for_status(); record('MANUAL_CONSOLE_SEED',path=path,params=params)
def logs():
    raw=shell('run-as','kr.pleosguide','cat','files/evidence.jsonl')
    return [json.loads(line) for line in raw.splitlines() if line.startswith('{')]
def wait(kind, contains='', start=0, timeout=50):
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        entries=logs()
        for event in entries[start:]:
            if event['kind']==kind and contains in event['detail']:
                record('OBSERVED',event=event); return event
        time.sleep(1)
    raise AssertionError(f'{kind}/{contains} missing: {entries[-3:]}')
def test(**extras):
    args=['am','broadcast','--user','current','-n','kr.pleosguide/.TestReceiver','-a','kr.pleosguide.TEST']
    for k,v in extras.items(): args+=['--es',k,v]
    shell(*args)
def shot(name):
    (OUT/(name+'.png')).write_bytes(subprocess.check_output(A+['exec-out','screencap','-p'],timeout=60))

if __name__=='__main__':
    shell('am','force-stop','--user','current','kr.syncguide')
    shell('am','start','--user','current','-n','kr.pleosguide/.MainActivity')
    shell('pm','grant','--user','current','kr.pleosguide','android.permission.RECORD_AUDIO')
    console('gear',gear='Park')
    console('seat',kind='occupied',area='passenger',value='true')
    console('hvac',power='true',dual='true',driver_temp=21,passenger_temp=21)
    test(command='START')
    wait('SNAPSHOT','driverTemp, value=21.0')
    shot('01-initial')
    test(command='SPEAK_TEST')
    time.sleep(3)
    test(command='LISTEN')
    time.sleep(14)
    mark=len(logs()); test(feature='SYNC'); wait('OFFER',start=mark)
    shot('02-proposal')
    mark=len(logs()); test(text='네, 해 봐'); wait('ACTION_RESULT',start=mark,timeout=60)
    shot('03-sync-result')
    test(text='차이를 느꼈어요'); time.sleep(1)
    for feature in ['ERGO','SOUND','SPREAD','GLEO']:
        mark=len(logs()); test(feature=feature); wait('OFFER',start=mark)
        test(text='네, 해 봐'); time.sleep(2)
        if feature=='SOUND':
            test(text='앞은 잘 들리고 뒤는 작아졌어요'); time.sleep(1)
            test(text='가운데로 복원했어요'); time.sleep(1)
        elif feature!='GLEO': test(text='조작했어요'); time.sleep(1)
        shot('04-'+feature)
        test(text='다음에 혼자 다시 써 볼게요'); time.sleep(1)
    # Gleo receiver is tested by ADB only. Source remains UNVERIFIED_INTENT.
    for action,params in [('START_FEATURE_GUIDE',{}),('START_FEATURE_GUIDE',{'feature':'INVALID'}),('RESPOND_TO_GUIDE',{'sessionId':'expired','response':'네'})]:
        shell('am','broadcast','--user','current','-n','kr.pleosguide/.GleoReceiver','-a',action,'--es','ACTION_PARAM',json.dumps(params,ensure_ascii=False))
    # State exit and rejection.
    test(feature='ERGO'); test(text='취소'); time.sleep(1)
    test(feature='SPREAD'); console('gear',gear='Drive'); time.sleep(5)
    console('gear',gear='Park'); time.sleep(3)
    test(command='STOP'); time.sleep(2)
    shot('05-off')
    (OUT/'evidence.jsonl').write_text('\n'.join(json.dumps(e,ensure_ascii=False) for e in logs())+'\n',encoding='utf8')
    record('HARNESS_FINISHED',claim='Receiver and mock-input integration trial; inspect individual outcomes, not a blanket success.')
