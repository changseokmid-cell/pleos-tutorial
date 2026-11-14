import pathlib, subprocess, time, requests, os, json
root=pathlib.Path(__file__).resolve().parents[1]
out=root/'evidence'/'baseline-reproduction'
a=[str(pathlib.Path(os.environ['LOCALAPPDATA'])/'PleosSyncLab/sdk/platform-tools/adb.exe'),'-s','emulator-5572']
def adb(*args): return subprocess.check_output(a+list(args),timeout=90).decode('utf8','replace')
def setc(path,**kw):
    r=requests.put('http://127.0.0.1:18088/vehicle/'+path,params=kw,timeout=30);r.raise_for_status()
    print('Console input',path,kw,flush=True)
def waitfor(text):
    for _ in range(30):
        log=adb('logcat','-d','-s','SyncTutorial:I','SyncVehicle:D')
        (out/'app-log.txt').write_text(log,encoding='utf8')
        if text in log: print('OBSERVED',text,flush=True); return
        time.sleep(2)
    raise RuntimeError(text+' missing')
waitfor('parked=true, occupied=false, power=true, synced=true, driver=22.0, passenger=22.0')
setc('seat',kind='occupied',area='passenger',value='true')
waitfor('CUE INTRO')
adb('shell','am','start','--user','current','-a','android.settings.SETTINGS')
setc('hvac',dual='false');setc('hvac',passenger_temp=24)
waitfor('CUE RESULT')
print(adb('shell','am','force-stop','--user','current','kr.syncguide'))
(out/'continued-result.json').write_text(json.dumps({'passed':True,'basis':'LIVE SDK from baseline app; console manual changes','claim':'Read/guide/manual-change confirmation only'},indent=2),encoding='utf8')
