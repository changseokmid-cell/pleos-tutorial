"""Read the separate production workspace; never edit customer-experience originals."""
from pathlib import Path
import os,json,hashlib,subprocess,shutil,datetime
ROOT=Path(__file__).resolve().parents[1];WORKSPACE=ROOT.parent
ff=shutil.which('ffprobe')
if not ff:ff=next((Path(os.environ['LOCALAPPDATA'])/'Microsoft/WinGet/Packages').glob('Gyan.FFmpeg*/**/ffprobe.exe'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
items=[
 ('SYNC','outputs/20261113-sync-verbatim/SYNC_ChatLog.mp4','user_approved_2026-11-13','docs/production/SYNC_확정본과_후속영상_제작법.md'),
 ('ERGO','outputs/20261114-ergo-film/full-rebuild-20261114/final.mp4','review_copy_user_approval_unconfirmed','outputs/20261114-ergo-film/full-rebuild-20261114/DELIVERY.json'),
 ('SOUND','outputs/20261114-sound-film/full-rebuild-20261114/final.mp4','review_copy_user_approval_unconfirmed','outputs/20261114-sound-film/full-rebuild-20261114/validation.json'),
 ('SPREAD','outputs/20261114-spread-film/sync-verified-20261114/final.mp4','review_copy_user_approval_unconfirmed','outputs/20261114-spread-film/sync-verified-20261114/검수결과.md'),
 ('GLEO','outputs/20261114-gleo-film/full-rebuild-20261114/final.mp4','review_copy_user_approval_unconfirmed','outputs/20261114-gleo-film/full-rebuild-20261114/production-state.json')]
data=[]
for feature,path,status,provenance in items:
    p=WORKSPACE/path
    meta=json.loads(subprocess.check_output([str(ff),'-v','error','-show_streams','-show_format','-of','json',str(p)],timeout=30))
    v=next(s for s in meta['streams'] if s['codec_type']=='video')
    data.append(dict(feature=feature,kind='customer_experience_concept',workspaceSource=path,approvalStatus=status,productionRecord=provenance,bytes=p.stat().st_size,sha256=sha(p),durationSeconds=float(meta['format']['duration']),width=v['width'],height=v['height'],publicUrl=None,apkExecutionEvidence=False,redistributionReview='Production sources include manufacturer imagery and generated media; public release rights not independently audited here.'))
out=ROOT/'demos';out.mkdir(exist_ok=True)
(out/'media-manifest.json').write_text(json.dumps({'date':'2026-11-14','cataloguedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'items':data},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
lines=['# 영상 목록','', '고객 경험 영화와 실제 APK 녹화를 구분한다. 아래 원본은 이 Git 저장소 밖의 제작 보관소에 있고, 해시·버전·승인 상태는 [media-manifest.json](media-manifest.json)에 고정했다. 공개 Release URL은 아직 없다.','', '| 기능 | 현재 연결본 | 길이 | 상태 |','|---|---|---|---|']
for x in data:
    lines.append(f"| {x['feature']} | [로컬 제작본](../../{x['workspaceSource']}) | {x['durationSeconds']:.2f}초 | {'사용자 승인본' if x['feature']=='SYNC' else '신규 검토본, 최종 승인 미확인'} |")
lines+=['','이 표의 로컬 제작본 링크는 공유 프로젝트 안에서만 열린다. 제출용 공개 저장소에서는 승인된 MP4를 Release에 업로드하고 실제 다운로드 URL로 바꾼 뒤 접근성을 검사한다. 후속 네 편의 이전 revision-2는 현재 목록의 최신본으로 사용하지 않는다.','', '## 실제 앱 녹화','', '[Release_Emulator.mp4](Release_Emulator.mp4)는 검증 묶음 ZIP에 포함하는 실제 에뮬레이터 화면 녹화다. Android screenrecord는 오디오를 녹음하지 않는다. UI 수락과 체감 버튼은 자동화 입력이며 실제 사람 음성·만족·학습을 입증하지 않는다. 새 설치, P 상태, SYNC 실제 제어와 종료·재시작 결과는 [시험 기록](../evidence/release-smoke/run.json) 및 [재현 문서](../docs/testing.md)와 함께 확인한다.','', '## 제작과 구현 경계','', '고객 경험 영화의 그랜저·배역·차량 UI는 제작 자료이며 실차 앱 동작 촬영이 아니다. 영화에 나오는 주행 중 안내, 스트레칭·음장·SPREAD 자동 실행은 이번 APK의 검증 범위와 다르다. APK는 세 기능의 순정 조작 안내를 제공한다. SYNC 영화의 음성은 Gleo를 연기한 합성 보이스이며 실제 순정 Gleo 음성 증거가 아니다.','', '원본 Blender ZIP과 중간 미디어는 제작 폴더에 보존한다. 이번 검증 묶음에는 권리·최종 선택이 정리되지 않은 고객 경험 영화를 일괄 복사하지 않았다.']
if (ROOT/'evidence/release-smoke-first/failure-note.json').exists():
    lines=[line.replace('새 설치, P 상태, SYNC 실제 제어와 종료·재시작 결과는 [시험 기록](../evidence/release-smoke/run.json)','새 설치, P 상태, SYNC 실제 제어와 Off까지의 부분 결과는 [시험 기록](../evidence/release-smoke-first/run.json)') for line in lines]
    lines+=['','릴리스 재시작·이력 유지 검사는 에뮬레이터 장애로 중단됐다. 녹화는 102.508초이며 전체 release PASS를 의미하지 않는다.']
(out/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
print(json.dumps([{k:x[k] for k in ['feature','durationSeconds','sha256','approvalStatus']} for x in data],ensure_ascii=False,indent=2))
