# 제출 후보와 남은 절차

이 폴더는 실제 구현·실행 근거를 담은 1차 제출 후보다. 사용자 요청으로 [비공개 저장소](https://github.com/changseokmid-cell/pleos-tutorial)와 [후보 Release](https://github.com/changseokmid-cell/pleos-tutorial/releases/tag/contest-round1-candidate-20261114)에 보관했다. 공식 신청서·개인정보 동의·서명·참가자 정보·메일 발송은 별도다. 로그인 없는 공개 다운로드는 아직 제공하지 않는다.

## 버전 연결

- 앱 소스 빌드 기준: `4fe8a913b52770218757791bf1749c2fb8b35ef9`.
- release: `kr.pleosguide` 1.0.0 (1), 개인 제출용 키로 서명. 키와 암호는 공개 파일에 포함하지 않는다.
- 문서/시험 증거를 포함한 최종 Git commit, APK·영상 SHA-256은 로컬 `dist/submission-manifest.json`에 기록한다. manifest를 포함한 제출 ZIP 자체 해시는 `dist/SHA256SUMS.txt`에 별도 기록한다.
- Android 소스가 빌드 기준 commit 이후 달라지지 않았는지 패키징 단계에서 대조한다. APK 파일은 Git 일반 이력에서 제외하고 Release 첨부파일 또는 다운로드 ZIP으로 제공한다.

## 구분하여 제출할 것

1. 소스 ZIP: Gradle Wrapper, Android 소스, 문서, 선별 실행 증거. 서명키·SDK AAR·캐시·원본 영상·개인정보 제외.
2. 검증 묶음 ZIP: 소스 ZIP, 서명 APK, 공개 소개 PDF, 실제 release 실행 녹화, manifest, 해시. 고객 경험 영화는 별도 선택 자산으로 관리한다.
3. 고객 경험 영상: SYNC는 사용자 승인본. 에르고·사운드·SPREAD·Gleo는 새 검토본의 hash·출처를 목록화하되 최종 승인으로 표시하지 않는다. 영화의 자동 실행 장면과 APK 실제 지원 표를 함께 제공한다.

## GitHub 보관과 제출 전 공개 확인

별도 Git 저장소와 `contest-round1-candidate-20261114` 태그를 push하고 Release 14개 첨부파일을 보관했다. 고정 후보 commit은 `35c4f74a2c5a0cbcfe8755c226d2f7b371ef4706`이다. [보관 검증 기록](github-storage.json)에 GitHub 서버 해시와 APK·제출 ZIP 재다운로드 대조를 남겼다. 현재는 비공개 로그인 상태에서 확인한 결과다. 실제 접수용 공개 상태로 전환할 때 로그인 없이 소스·APK·영상을 열어 다시 검사한다.

원래 제출 묶음의 remoteUrl=null은 업로드 전 작성 시점의 기록이며 고정 ZIP을 덮어쓰지 않는다. 이 문서와 Release가 보관 위치를 연결한다. 기본 브랜치의 후속 보관 문서 commit을 고정 후보 commit과 혼동하지 않는다.

## 공식 접수 체크

2026-11-14 확인한 [공식 제출 안내](https://appdevchallenge.auto-hmg.io/guide/submission)와 [추가 공지](https://appdevchallenge.auto-hmg.io/notice/c0a1a000-2026-4923-8000-000000000007)에 따르면 1차 마감은 2026-11-15 23:59 KST다. 기획서·동의가 필수이며 개발/영상 자료는 선택이다. 비공개 저장소 접수 시 개발 가산점의 공개 일정은 11/16까지 공개 후 11/23까지 유지다. 공개가 어려운 경우 소스와 APK ZIP 다운로드 링크 대안을 안내한다. 공식 공지의 변경 여부를 실제 접수 전에 다시 확인한다.

메일에 저장소 URL, 최종 commit hash, APK 경로/Release URL, 영상 링크를 적고 공식 요구 참가 정보를 채운다. GitHub 업로드만으로 접수되는 것은 아니다. 이 개발 작업에서는 이메일을 발송하지 않았다.

## 2차 개선

실제 음성/Gleo 왕복과 음성 지연 해결, 2시간 자동 제안, 실차 사양별 제어 권한·메뉴 검증, 주행 중 짧은 제안, 목표 고객의 기능 발견·재사용 관찰을 진행한다. 1차 제출본의 태그/첨부물을 덮어쓰지 않고 별도 버전으로 기록한다.
