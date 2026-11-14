"""Cold-boot the dedicated AVD and check the installed signed app's visible data.

No uninstall, pm clear, run-as, preference injection, or vendor modification.
Run after release_smoke.py, with hold_console.py still running.
"""
import argparse, json, os, pathlib, subprocess, time
os.environ['PLEOS_TRIAL']='restart-persistence'
import release_smoke as ui
from wait_vehicle_ready import wait_ready

LAB=pathlib.Path(os.environ['LOCALAPPDATA'])/'PleosSyncLab'
saved=next(e for e in json.loads((ui.ROOT/'evidence/release-smoke-verified/run.json').read_text(encoding='utf8')) if e['kind']=='PERSISTENT_UI_BEFORE')
expected={k:saved[k] for k in ('history','settings')}

def check_restart(label):
    start=int(time.time()*1000)
    found=ui.ensure_app()
    assert any(n.get('text')=='튜토리얼 켜기' for n in found), 'Unexpected active mode after restart'
    assert not any(e['time']>=start and e['kind']=='MODE_ON' for e in ui.logs()), 'Unexpected automatic mode start'
    ui.screenshot(label+'-off')
    ui.event('DEFAULT_OFF',cycle=label)
    ui.click('튜토리얼 켜기'); ui.wait('SNAPSHOT',start=start)
    actual=ui.persistent_ui(); assert actual==expected, (actual,expected)
    ui.event('PERSISTENCE_MATCH',cycle=label,**actual)
    ui.screenshot(label+'-history')

ui.event('PROVENANCE',input='Automated UI; exact displayed history and all five preferences compared',apkUnchanged=True,dataCleared=False)
p=argparse.ArgumentParser();p.add_argument('--use-running',action='store_true',help='Use an externally cold-booted AVD; retain its startup evidence separately');args=p.parse_args()
proc=None;stdout=None;stderr=None
if not args.use_running:
    ui.adb('emu','kill')
    time.sleep(12)
    stdout=(ui.OUT/'emulator-start.txt').open('wb');stderr=(ui.OUT/'emulator-error.txt').open('wb')
    proc=subprocess.Popen([str(LAB/'sdk/emulator/emulator.exe'),'-avd','PleosSync210','-port','5572','-no-snapshot','-no-boot-anim','-memory','4096','-cores','4','-gpu','host','-no-window'],stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
    ui.event('COLD_BOOT_STARTED',pid=proc.pid,flags='no-snapshot; memory4096; cores4; gpu host; no-window')
else:
    ui.event('EXTERNAL_COLD_BOOT',note='See dds-recovery.md and emulator startup evidence')
started=time.monotonic()
while time.monotonic()-started<360:
    if proc and proc.poll() is not None:raise RuntimeError('Emulator exited; inspect startup logs and stale AVD locks')
    try:
        if ui.adb('shell','getprop','sys.boot_completed')=='1':break
    except subprocess.SubprocessError:pass
    time.sleep(3)
else:raise TimeoutError('Android boot')
ui.event('ANDROID_BOOT_COMPLETED',elapsedSeconds=round(time.monotonic()-started,1))
wait_ready(ui.OUT/'readiness')
ui.event('VEHICLE_READY',elapsedSeconds=round(time.monotonic()-started,1))
ui.console('gear',gear='Park')
check_restart('01-cold-boot')
# Kill while mode is ON: a fresh process must not resume a live session.
ui.adb('shell','am','force-stop','--user','current','kr.pleosguide')
check_restart('02-killed-while-on')
ui.click('튜토리얼 끄기')
ui.event('PASS',checks=['cold boot DDS ready','cold boot default Off','cold boot history and five preferences equal','force-stop while On defaults Off','force-stop while On preserves history and preferences'])
if stdout:stdout.close()
if stderr:stderr.close()
