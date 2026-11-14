"""Create a local, hash-linked submission bundle after committing source/evidence.
This tool does not create a remote repository, upload files, or submit mail.
"""
from pathlib import Path
import subprocess,json,hashlib,zipfile,shutil,datetime,argparse
ROOT=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args]).decode().strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--allow-partial',action='store_true')
parser.add_argument('--trial',default='release-smoke-verified')
parser.add_argument('--output',default='dist/verified-20261114');args=parser.parse_args()
assert not git('status','--porcelain'),'Commit selected source, documentation and evidence first'
audit=json.loads((ROOT/'evidence/build/release-audit.json').read_text(encoding='utf8'))
assert not git('diff',audit['sourceCommit'],'--','android'),'APK Android source mismatch'
head=git('rev-parse','HEAD');short=head[:12]
release_run=ROOT/'evidence'/args.trial/'run.json'
passed=release_run.exists() and any(e.get('kind')=='PASS' for e in json.loads(release_run.read_text(encoding='utf8')))
assert passed or args.allow_partial,'Release smoke is incomplete; explicitly label partial verification if packaging'
restart_run=ROOT/'evidence/restart-persistence/run.json'
restart_passed=restart_run.exists() and any(e.get('kind')=='PASS' for e in json.loads(restart_run.read_text(encoding='utf8')))
assert restart_passed or args.allow_partial,'Restart persistence test must pass'
video=ROOT/'evidence'/(args.trial if passed else 'release-smoke-first')/'emulator.mp4'
assert video.exists()
apk=ROOT/'apk/PleosTutorial-1.0.0.apk';assert sha(apk)==audit['apkSha256']
out=ROOT/args.output;out.mkdir(parents=True,exist_ok=True)
source=out/f'PleosTutorial-source-{short}.zip'
subprocess.run(['git','-C',str(ROOT),'archive','--format=zip','--prefix=pleos-tutorial/',f'--output={source}',head],check=True)
demo=ROOT/'demos/Release_Emulator.mp4';shutil.copy2(video,demo)
assets=[(source,'source/'+source.name),(apk,'apk/PleosTutorial-1.0.0.apk'),(ROOT/'docs/proposal-public.pdf','docs/proposal-public.pdf'),(ROOT/'docs/proposal-public.md','docs/proposal-public.md'),(ROOT/'docs/testing.md','docs/testing.md'),(ROOT/'docs/implementation.md','docs/implementation.md'),(ROOT/'demos/media-manifest.json','demos/media-manifest.json'),(demo,'demos/Release_Emulator.mp4')]
assets.extend((ROOT/'docs'/name,'docs/'+name) for name in ['reviewer-guide.md','architecture.md','dds-recovery.md'])
manifest=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),appId='kr.pleosguide',version='1.0.0',finalSubmissionCommit=head,apkSourceCommit=audit['sourceCommit'],androidDiff='empty',releaseSmoke='passed' if passed else 'partial',restartPersistence='passed' if restart_passed else 'partial',voiceHumanTrial='deferred_by_user',naturalGleoTrial='unverified',remoteUrl='https://github.com/changseokmid-cell/pleos-tutorial',emailSubmitted=False,assets=[dict(path=name,bytes=p.stat().st_size,sha256=sha(p)) for p,name in assets])
mp=out/'submission-manifest.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
readme=out/'READ_ME_FIRST.md'
readme.write_text(f'''# 내 차 사용 안내 - 검증 제출 후보

앱: kr.pleosguide 1.0.0
최종 소스·문서 commit: {head}
APK Android 소스 commit: {audit['sourceCommit']}
release 시험: {manifest['releaseSmoke']}
콜드 부팅·모드 On 강제 종료 후 이력·설정 유지: {manifest['restartPersistence']}

- source/의 ZIP을 풀면 Gradle Wrapper·소스·문서·실행 증거가 있습니다.
- apk/PleosTutorial-1.0.0.apk는 서명한 release입니다.
- docs/proposal-public.pdf는 개인정보 없는 공개 소개·구현표입니다.
- docs/reviewer-guide.md → architecture.md → testing.md 순서로 제품·코드·증거를 읽을 수 있습니다.
- demos/Release_Emulator.mp4는 실제 화면 녹화이며 오디오는 없습니다. UI 수락과 체감 응답은 자동화 입력입니다.
- submission-manifest.json이 파일 hash와 commit을 연결합니다.

실제 사람 음성 시험은 사용자 요청에 따라 나중으로 남겼습니다. 실제 Gleo 자연어 왕복, 에르고·음장·SPREAD 전용 자동 제어 및 실차·사용자 학습 효과는 검증하지 않았습니다.
고객 경험 영화는 이 묶음에 포함하지 않았습니다. media-manifest.json에서 승인 SYNC와 후속 검토본을 구분합니다.
비공개 GitHub: https://github.com/changseokmid-cell/pleos-tutorial
Release: https://github.com/changseokmid-cell/pleos-tutorial/releases/tag/contest-round1-verified-20261114
접근 권한이 있는 GitHub 로그인이 필요합니다. 공식 참가 정보·동의·서명·메일 제출은 별도이며 접수 완료를 뜻하지 않습니다.
''',encoding='utf8')
bundle=out/f'PleosTutorial-submission-{short}.zip'
with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p,name in assets:z.write(p,name)
    z.write(mp,'submission-manifest.json');z.write(readme,'READ_ME_FIRST.md')
with zipfile.ZipFile(bundle) as z:
    assert z.testzip() is None
    for record in manifest['assets']:
        assert hashlib.sha256(z.read(record['path'])).hexdigest()==record['sha256']
with zipfile.ZipFile(source) as z:
    assert z.testzip() is None
    names=z.namelist()
    assert 'pleos-tutorial/android/gradle/wrapper/gradle-wrapper.jar' in names
    assert not any(n.endswith(('.jks','.keystore','.apk','.aar','.mp4')) for n in names)
checks=out/'SHA256SUMS.txt'
checks.write_text('\n'.join(f'{sha(p)}  {p.name}' for p in [source,bundle,mp])+'\n',encoding='utf8')
print(json.dumps(dict(bundle=str(bundle),source=str(source),commit=head,bytes=bundle.stat().st_size,sha256=sha(bundle),zipIntegrity='PASS',assetHashCheck='PASS'),ensure_ascii=False,indent=2))
