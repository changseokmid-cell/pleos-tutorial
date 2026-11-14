"""Resume the preserved cold-boot run after fixing launcher navigation.
Requires its actual cold-boot history match; does not synthesize missing checks.
"""
import os,json,time
os.environ['PLEOS_TRIAL']='restart-persistence'
import release_smoke as ui
ui.run.extend(json.loads((ui.OUT/'run.json').read_text(encoding='utf8')))
cold=next(e for e in ui.run if e['kind']=='PERSISTENCE_MATCH' and e['cycle']=='01-cold-boot')
expected={k:cold[k] for k in ('history','settings')}
found=ui.ensure_app()
if any(n.get('text')=='튜토리얼 켜기' for n in found):
    begin=int(time.time()*1000);ui.click('튜토리얼 켜기');ui.wait('SNAPSHOT',start=begin)
assert any(n.get('text')=='튜토리얼 끄기' for n in ui.nodes()), 'Mode must be On before this forced termination'
ui.event('RETRY_AFTER_LAUNCHER_RECOVERY',reason='Prior navigation/focus interrupted On tap; use MAIN/LAUNCHER, wait for transition, and focus the right pane before each UI query')
ui.adb('shell','am','force-stop','--user','current','kr.pleosguide')
start=int(time.time()*1000)
found=ui.ensure_app()
assert any(n.get('text')=='튜토리얼 켜기' for n in found)
assert not any(e['time']>=start and e['kind']=='MODE_ON' for e in ui.logs())
ui.event('DEFAULT_OFF',cycle='04-killed-while-on-focus')
ui.screenshot('04-killed-while-on-off')
ui.click('튜토리얼 켜기');ui.wait('SNAPSHOT',start=start)
actual=ui.persistent_ui();assert actual==expected
ui.event('PERSISTENCE_MATCH',cycle='04-killed-while-on-focus',**actual)
ui.screenshot('04-killed-while-on-history')
ui.click('튜토리얼 끄기')
ui.event('PASS',checks=['cold boot DDS ready','cold boot default Off','cold boot history and five preferences equal','force-stop while On defaults Off','force-stop while On preserves history and preferences'],launcher='MAIN/LAUNCHER; five-second transition wait; right-pane focus')
