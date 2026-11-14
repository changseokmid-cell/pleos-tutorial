"""Wait for the actual Pleos vehicle transport, not just Android boot/HTTP 200.

Connect 2.1.0 pins DDS to 10.0.2.15. The emulator radio assigns that
address after Android has booted. Keep hold_console.py running afterwards.
This tool changes no vendor XML, privileges, SELinux policy, or vehicle values.
"""
import argparse, json, os, pathlib, subprocess, time
import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
ADB = pathlib.Path(os.environ['LOCALAPPDATA'])/'PleosSyncLab/sdk/platform-tools/adb.exe'
BASE = 'http://127.0.0.1:18088'

def wait_ready(out, timeout=600):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    samples, streak = [], 0
    started = time.monotonic()
    subprocess.run([str(ADB), '-s', 'emulator-5572', 'forward', 'tcp:18088', 'tcp:8088'], check=True)
    while time.monotonic()-started < timeout:
        sample = dict(time=time.time(), elapsedSeconds=round(time.monotonic()-started, 1))
        try:
            ip = subprocess.check_output([str(ADB), '-s', 'emulator-5572', 'shell', 'ip', '-4', 'addr', 'show', 'eth0'], timeout=15).decode()
            sample['ddsAddressPresent'] = 'inet 10.0.2.15/' in ip
            session = requests.post(BASE+'/browser/session', params={'client':'pleos_ready_check'}, timeout=15)
            session.raise_for_status()
            sample['active'] = session.json().get('active') is True
            state = requests.get(BASE+'/vehicle/state', timeout=15); state.raise_for_status()
            state = state.json()
            sample['bridgeReady'] = state.get('gear',{}).get('bridge_ready') is True
            hvac = state.get('hvac',{})
            sample['hvacPublishReady'] = hvac.get('selected_core_publisher_ready',{}).get('all') is True
            sample['hvacSubscribeReady'] = hvac.get('selected_core_subscription_ready',{}).get('all') is True
            sample['ready'] = all(sample.get(k) is True for k in ('ddsAddressPresent','active','bridgeReady','hvacPublishReady','hvacSubscribeReady'))
            if sample['ready']:
                (out/'vehicle-state.json').write_text(json.dumps(state, indent=2), encoding='utf8')
        except (requests.RequestException, subprocess.SubprocessError, ValueError) as e:
            sample.update(ready=False, error=type(e).__name__)
        samples.append(sample)
        (out/'readiness.json').write_text(json.dumps(samples, indent=2), encoding='utf8')
        print(json.dumps(sample), flush=True)
        streak = streak+1 if sample['ready'] else 0
        if streak >= 3:
            return samples[-1]
        time.sleep(2)
    raise TimeoutError('DDS/vehicle transport did not become ready; inspect readiness.json')

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('--out', default=str(ROOT/'evidence/dds-recovery'))
    p.add_argument('--timeout', type=int, default=600); a=p.parse_args()
    wait_ready(a.out, a.timeout)
