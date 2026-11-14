"""Mirror the documented-in-console-source browser heartbeat during SDK trials.
Uses /browser/session and /vehicle/catalog observed in the installed console HTML.
This is a test-console connection, not a live-vehicle input.
"""
import pathlib, time, requests
stop=pathlib.Path(__file__).resolve().parents[1]/'.local'/'stop-console'
base='http://127.0.0.1:18088'
with requests.Session() as s:
    s.get(base+'/vehicle/catalog',timeout=30).raise_for_status()
    print('Virtual Console heartbeat connecting',flush=True)
    ready=False
    try:
        while not stop.exists():
            try:
                requests.post(base+'/browser/session',params={'client':'pleos_tutorial_sdk_trial'},timeout=20).raise_for_status()
                if not ready: print('Virtual Console test heartbeat active',flush=True); ready=True
            except requests.RequestException as e:
                print('Heartbeat reconnecting: '+type(e).__name__,flush=True)
            time.sleep(1)
    finally:
        try: requests.post(base+'/browser/session',params={'client':'pleos_tutorial_sdk_trial','closing':1},timeout=10)
        except requests.RequestException: pass
