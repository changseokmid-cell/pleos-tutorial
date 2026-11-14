# 다섯 영상에서 코드·실구동 증거까지

[README 썸네일로 돌아가기](../README.md#다섯-가지-고객-경험) · [최신 영상 Release](https://github.com/changseokmid-cell/pleos-tutorial/releases/tag/contest-five-feature-videos-20261115) · [실제 APK 녹화](https://github.com/changseokmid-cell/pleos-tutorial/releases/download/contest-round1-verified-20261114/Release_Emulator.mp4)

영상은 제품 경험 시나리오이고, 실행 로그는 현재 APK의 검증입니다. 아래에서 **불편 → 배울 기능 → 관련 코드 → 확인한 결과** 순서로 이어집니다. 시청 순서는 SYNC → SPREAD → 사운드 위치 → 에르고 시트 → Gleo 복합 요청입니다. SYNC는 확정본의 재생 호환성을 보완한 버전이고, 나머지는 기존 선택본과 동일한 영상입니다.

<a name="sync"></a>

## 01. 좌석별 독립 온도 · SYNC — 운전자는 더운데, 동승자는 춥다면?

[▶ 영상 열기 · 0:48](https://github.com/changseokmid-cell/pleos-tutorial/releases/download/contest-five-feature-videos-20261115/01_SYNC_17e9fe22.mp4)

전체 온도를 함께 바꾸던 사용자가 좌석마다 따로 조절할 수 있음을 이해하는 장면입니다.

2026-11-15 화면 재생 호환성을 위해 H.264 High 형식으로 변환했습니다. 1920×1080, 24fps, 1,150프레임, 47.936초와 원래 AAC 음성은 유지했습니다. [재생 확인 기록](sync-playback-20261115.json)에서 원본과 변환본의 대조 결과를 확인할 수 있습니다.

**코드에서 읽을 부분:** [VehicleContextRepository.kt · independentTemperature](https://github.com/changseokmid-cell/pleos-tutorial/blob/4fe8a913b52770218757791bf1749c2fb8b35ef9/android/app/src/main/java/kr/pleosguide/VehicleContextRepository.kt#L147). 수락 뒤 지원성을 확인하고, 연동 해제와 동승석 온도 요청 각각의 결과를 다시 읽습니다.

<a name="sync-evidence"></a>

**현재 APK에서 확인한 것:** 실제 SDK 제어·재조회 확인: 운전석 21°C 유지 / 동승석 24°C. COMMAND_REQUESTED → COMMAND_ACK → INDEPENDENT_READ → ACTION_RESULT: CONFIRMED

[서명 release 실행 로그](../evidence/release-smoke-verified/evidence.jsonl) · [UI 시험 순서와 PASS](../evidence/release-smoke-verified/run.json) · [실제 21/24°C 화면](../evidence/release-smoke-verified/03-confirmed-21-24.png)

영화의 주행·음성 장면은 제품 경험 연출입니다. 실제 APK 제어는 P 및 차량 UX 허용 조건에서 자동 UI 수락으로 시험했습니다.

<a name="spread"></a>

## 02. 직풍 피하기 · SPREAD — 시원한 온도는 좋은데, 얼굴에 바람이 직접 닿는다면?

[▶ 영상 열기 · 1:01](https://github.com/changseokmid-cell/pleos-tutorial/releases/download/contest-five-feature-videos-20261115/02_SPREAD_abd18197.mp4)

직접풍의 불편을 더위와 구별하고, 좌우 목표온도를 유지한 채 승객 회피 모드를 발견하는 장면입니다.

**코드에서 읽을 부분:** [TutorialCoordinator.kt · Feature.SPREAD](https://github.com/changseokmid-cell/pleos-tutorial/blob/4fe8a913b52770218757791bf1749c2fb8b35ef9/android/app/src/main/java/kr/pleosguide/TutorialCoordinator.kt#L153). [목표온도 유지 관측](https://github.com/changseokmid-cell/pleos-tutorial/blob/4fe8a913b52770218757791bf1749c2fb8b35ef9/android/app/src/main/java/kr/pleosguide/TutorialCoordinator.kt#L119)은 SPREAD 모드 신호와 구별합니다.

<a name="spread-evidence"></a>

**현재 APK에서 확인한 것:** 순정 메뉴 안내와 목표온도 유지 관측. 전동 벤트 제어·모드 확인 없음. TEMPERATURE_OBSERVATION의 unchanged=true와 SPREAD mode UNKNOWN을 함께 읽습니다.

[안내·응답 원본 로그](../evidence/debug-trial/evidence.jsonl) · [앱 안내 화면](../evidence/debug-trial/04-SPREAD.png) · [전체 시험 설명](../docs/testing.md)

온도 유지 관측은 벤트의 SPREAD 작동 성공을 의미하지 않습니다. 영화의 기류·벤트 표현은 개념 재현입니다.

<a name="sound"></a>

## 03. 사운드 위치 — 뒷자리에서는 음악이 너무 크게 들린다면?

[▶ 영상 열기 · 1:21](https://github.com/changseokmid-cell/pleos-tutorial/releases/download/contest-five-feature-videos-20261115/03_SOUND_9fc8ab12.mp4)

자녀의 요청 → 아버지의 기능 발견 → 위치 체험 → 가족 휴식 → 직접 가운데 설정으로 마무리합니다. 속마음은 관객용 연출이며 Gleo 입력이 아닙니다.

**코드에서 읽을 부분:** [TutorialCoordinator.kt · Feature.SOUND](https://github.com/changseokmid-cell/pleos-tutorial/blob/4fe8a913b52770218757791bf1749c2fb8b35ef9/android/app/src/main/java/kr/pleosguide/TutorialCoordinator.kt#L152). [위치 체감 → 가운데 복원 응답](https://github.com/changseokmid-cell/pleos-tutorial/blob/4fe8a913b52770218757791bf1749c2fb8b35ef9/android/app/src/main/java/kr/pleosguide/TutorialCoordinator.kt#L104)의 단계가 핵심입니다.

<a name="sound-evidence"></a>

**현재 APK에서 확인한 것:** 순정 위치 설정 안내와 복원 응답 기록. 스피커 직접 제어 없음. POSITION_REPORT와 CENTER_RESTORED_REPORT는 사용자가 보고한 단계이며 차량 음장 센서 확인이 아닙니다.

[안내·응답 원본 로그](../evidence/debug-trial/evidence.jsonl) · [앱 안내 화면](../evidence/debug-trial/04-SOUND.png) · [전체 시험 설명](../docs/testing.md)

최신 v5 영상에서는 음장 비교를 제외했습니다. 현재 APK에는 위치 체험 뒤 별도 음장 안내 단계도 남아 있습니다. 이번 변경은 영상·설명의 연결이며 Android 코드는 변경하지 않았습니다.

<a name="ergo"></a>

## 04. 에르고 시트 스트레칭 — 오래 앉아 뻐근할 때, 몰랐던 시트 버튼을 발견합니다.

[▶ 영상 열기 · 2:01](https://github.com/changseokmid-cell/pleos-tutorial/releases/download/contest-five-feature-videos-20261115/04_ERGO_c248edc4.mp4)

긴 주행 뒤 정차 → 버튼 위치 발견 → 전신 체험 → 허리·골반·꺼짐 순서 → 다음 휴게소에서 재사용으로 이어집니다.

**코드에서 읽을 부분:** [TutorialCoordinator.kt · Feature.ERGO](https://github.com/changseokmid-cell/pleos-tutorial/blob/4fe8a913b52770218757791bf1749c2fb8b35ef9/android/app/src/main/java/kr/pleosguide/TutorialCoordinator.kt#L151). [장시간 주행 후 P 전환 조건](https://github.com/changseokmid-cell/pleos-tutorial/blob/4fe8a913b52770218757791bf1749c2fb8b35ef9/android/app/src/main/java/kr/pleosguide/TutorialCoordinator.kt#L59)과 시트 버튼 안내를 분리해서 읽습니다.

<a name="ergo-evidence"></a>

**현재 APK에서 확인한 것:** 시트 버튼·모드 안내와 응답 기록. 스트레칭 모터 직접 제어 없음. GUIDANCE의 시트 버튼 안내와 MANUAL_OPERATION_REPORT를 확인합니다.

[안내·응답 원본 로그](../evidence/debug-trial/evidence.jsonl) · [앱 안내 화면](../evidence/debug-trial/04-ERGO.png) · [전체 시험 설명](../docs/testing.md)

실제 스트레칭 동작·체감은 영화의 재현입니다. APK 시험은 안내 흐름과 자동 응답 기록이며, 2시간 실시간 주행 후 자동 제안은 미검증입니다.

<a name="gleo"></a>

## 05. Gleo 복합 요청 — 에어컨과 라디오를 각각 조작하고 있었다면?

[▶ 영상 열기 · 1:10](https://github.com/changseokmid-cell/pleos-tutorial/releases/download/contest-five-feature-videos-20261115/05_GLEO_9aca15d5.mp4)

기능을 몰라 따로 조작하던 사용자가 “에어컨 끄고 라디오 켜줘”라는 복합 요청을 배워 직접 사용합니다.

**코드에서 읽을 부분:** [GleoReceiver.kt · onReceive](https://github.com/changseokmid-cell/pleos-tutorial/blob/4fe8a913b52770218757791bf1749c2fb8b35ef9/android/app/src/main/java/kr/pleosguide/GleoReceiver.kt#L10). [App Schema](https://github.com/changseokmid-cell/pleos-tutorial/blob/4fe8a913b52770218757791bf1749c2fb8b35ef9/android/app/src/main/assets/schema.json)와 [마이크 양보 안내](https://github.com/changseokmid-cell/pleos-tutorial/blob/4fe8a913b52770218757791bf1749c2fb8b35ef9/android/app/src/main/java/kr/pleosguide/TutorialCoordinator.kt#L154)를 함께 봅니다.

<a name="gleo-evidence"></a>

**현재 APK에서 확인한 것:** App Schema 3개 action·callback 전송 확인. 실제 Gleo 음성 왕복은 추후 시험. GLEO_ACTION_RECEIVED와 GLEO_CALLBACK_SENT의 success / asking / fail을 확인합니다. 출처는 UNVERIFIED_INTENT입니다.

[action·callback 원본 로그](../evidence/exception-trial/all-debug-history.jsonl) · [시험 순서](../evidence/exception-trial/run.json) · [앱 안내 화면](../evidence/debug-trial/04-GLEO.png)

ADB action 수신과 callback 전송을 시험했습니다. 실제 Gleo 수신·음성 왕복 및 에어컨+라디오 복합 실행 성공은 입증하지 않았습니다.

## 영상과 코드 버전을 고정하는 방식

코드 링크는 실제 APK Android 소스 commit `4fe8a913b52770218757791bf1749c2fb8b35ef9`를 가리킵니다. 썸네일은 선택한 MP4에서 직접 추출한 장면이며 새로운 합성 이미지가 아닙니다. 파일별 원본 경로·SHA-256·길이·썸네일 시각은 [media-manifest.json](media-manifest.json)에 기록했습니다.

2026-11-15 영상 묶음은 SYNC 호환본과 새 시청 순서를 반영합니다. 이전 업로드 검증은 [2026-11-14 기록](github-video-storage.json)에 보존하며, 이번 재생 확인은 [SYNC 대조 기록](sync-playback-20261115.json)을 따릅니다.

| 영상 | 현재 선택본 | 길이 | MP4 SHA-256 앞 12자리 |
|---|---|---|---|
| SYNC | SYNC_ChatLog · 재생 호환본 | 47.936초 | `17e9fe22c7b2` |
| SPREAD | SPREAD sync-verified | 61.269초 | `abd18197f772` |
| SOUND | 사운드 위치 v5 · 음장 제외 | 81.258초 | `9fc8ab123c18` |
| ERGO | 에르고 revision-3 | 121.258초 | `c248edc464d7` |
| GLEO | Gleo full-rebuild | 69.504초 | `9aca15d5b916` |

[2026-11-14 영상 명세](archive/media-manifest-20261114.json)와 [당시 원본 Release](https://github.com/changseokmid-cell/pleos-tutorial/releases/tag/contest-five-feature-videos-20261114), [첫 후보의 영상 목록](archive/media-manifest-first-candidate.json)과 [이전 Release](https://github.com/changseokmid-cell/pleos-tutorial/releases/tag/contest-round1-candidate-20261114)는 보존합니다. 이번 사용자의 최신 5편 연결 요청은 README 등록 기준에 기록했으며, 제작 기록에 있는 과거 검토·승인 상태를 소급 변경하지 않았습니다. 현재 저장소는 비공개이며 로그인·접근 권한이 필요합니다.

## 썸네일 다시 만들기

FFmpeg를 설치하고 이 저장소의 `tools/build_video_thumbnails.py`를 실행합니다. 원래 작업공간에서는 manifest의 원본 경로를 읽습니다. 다른 PC에서는 영상 Release의 MP4 5개를 내려받은 폴더를 `--video-dir`로 지정합니다. 원본 해시를 먼저 확인하며 MP4를 수정하지 않습니다.
