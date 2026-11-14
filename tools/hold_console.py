"""Mirror the documented-in-console-source browser heartbeat during SDK trials.
Uses /browser/session and /vehicle/catalog observed in the installed console HTML.
This is a test-console connection, not a live-vehicle input.
"""
import pathlib, time, requests
stop=pathlib.Path(__file__).resolve().parents[1]/'.local'/'stop-console'
base='http://127.0.0.1:18088'
with requests.Session() as s:
    s.get(base+'/vehicle/catalog',timeout=20).raise_for_status()
    print('Virtual Console test heartbeat active',flush=True)
    try:
        while not stop.exists():
            s.post(base+'/browser/session',params={'client':'pleos_tutorial_sdk_trial'},timeout=10).raise_for_status()
            time.sleep(1)
    finally: s.post(base+'/browser/session',params={'client':'pleos_tutorial_sdk_trial','closing':1},timeout=10)
