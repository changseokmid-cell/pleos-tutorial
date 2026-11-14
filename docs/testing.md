# 실행 시험과 재현

시험일: 2026-11-14 KST. AVD의 logcat 표시 날짜/시간대는 호스트와 다르므로 JSON의 Unix 밀리초 `time`을 기준으로 대조한다.

## 최신 판정

서명 APK에서 SYNC 21/21→21/24 재조회, Off 이후 변경 수신 중단, 앱 재실행 기본 Off, 표시 이력과 다섯 기능별 설정 유지가 통과했다. AVD 콜드 부팅 및 모드 On 강제 종료 후에도 이력·설정 일치를 확인했다. Android 소스와 APK는 변경하지 않았다.

[DDS 복구 설명](dds-recovery.md), [release 실행](../evidence/release-smoke-verified/run.json), [재시작 전후 비교](../evidence/restart-persistence/run.json)를 먼저 읽는다. 과거 실패와 중간 재시도는 지우지 않고 아래에서 구별한다.

## 환경

| 항목 | 값 |
|---|---|
| 앱 | `kr.pleosguide` 1.0.0 / versionCode 1 / target 33 / min 28 |
| AVD | PleosSync210, Pleos Connect 2.1.0, Android 14 API 34, x86_64 |
| fingerprint | `Pleos/crp_avd/crp_avd_x86_64:14/RELEASE.release_connect_v2.1.0/release_connect_v2.1.0:user/test-keys` |
| 화면 | 2560×1440, mdpi; 녹화는 1280×720 |
| 호스트 | Windows, JDK 17.0.21, compile SDK 35 / Build Tools 35.0.0 |
| 의존성 | Vehicle 2.3.2, SpeechToText/TextToSpeech 3.3.1 ON_DEVICE, coroutines 1.6.3 |
| 빌드 | Gradle 8.9, AGP 8.7.3, Kotlin 1.9.25 |
| 서비스 | CAAS 4.2.10-coral-aosp (4002010), 순정 Gleo `ai.umos.ambientai` |
| 초기 자원 제약 | 2 cores, 시작 명령에 -memory 2048을 지정했으나 실제 emulator 로그는 4096MB로 자동 상향. 첫 구성에서 host commit memory 부족으로 시작 실패. 음성 준비 지연/시간 초과의 전체 원인은 미확정 |

복구·최종 재검사는 4 cores / 4096MB / host GPU / no-window / no-snapshot으로 실행했다. 실제 게스트 메모리는 약 4GB다.

## 실제 capability

| 관측 | 결과 |
|---|---|
| HVAC power / dual / A/C | READ_WRITE 읽기. 이 앱이 자동 쓰는 항목은 dual과 동승석 목표온도뿐 |
| 동승석 온도 | 15~30°C, 0.5°C 간격; 24°C 명령 및 재조회 성공 |
| SYNC | `setHvacDual(false)` → 별도 읽기 false 확인 → 동승석 온도 명령 |
| 동승석 착좌 | 해당 fingerprint에서 콘솔 occupied=true ↔ SDK raw=false. 이 정확한 이미지에만 반전 매핑 적용 |
| 운전석/후석 착좌 | raw 읽기 기록. 의미 매핑 미확정이므로 의미 값 UNKNOWN |
| 현재 trip 주행 시간 | `ERROR_NOT_SUPPORTED_PROPERTY`; 누적 usage_time을 현재 trip으로 대체하지 않음 |
| CarUxRestrictions | P에서 requiresDO=false/restrictions=0, D에서 true/80 관측 |
| CarAudioManager | manager 획득 가능, `CAR_CONTROL_AUDIO_SETTINGS` 권한 -1. 전용 위치/음장 쓰기 없음 |
| 에르고 / SPREAD | 공개 전용 제어·결과 신호 미확인, 수동 안내와 응답만 제공 |

## 재현 절차

1. 공식 Pleos AVD를 콜드 부팅한다. Android boot_completed=1 이후에도 차량 DDS 주소와 브리지 준비를 별도로 확인한다. ADB serial은 이 환경에서 `emulator-5572`다. 다른 serial이면 시험 스크립트의 값을 바꾼다.
2. `adb -s emulator-5572 forward tcp:18088 tcp:8088`로 콘솔을 연결한다. `python tools/hold_console.py`가 실제 콘솔의 `/browser/session` heartbeat를 유지한다. `/vehicle/catalog`가 준비되지 않았거나 503/emulator_inactive면 차량 명령을 진행하지 않는다. `.local/stop-console` 파일로 heartbeat를 종료할 수 있다.
3. `python tools/wait_vehicle_ready.py --out evidence/my-dds-check`로 eth0 주소·활성 세션·브리지·공조 송수신을 세 번 연속 확인한 뒤, 콘솔에서 Park, 동승석 occupied=true, 공조 power=true, dual=true, 운전석/동승석 목표온도 21°C로 설정한다. 이는 시험 상황 생성이며 실차 센서 입력이 아니다.
4. release APK를 새로 설치한다. 이 프로젝트의 debug 설치본과 서명이 다르면 `kr.pleosguide`만 삭제한 뒤 설치한다. 앱 데이터 삭제로 이력도 지워지므로 필요한 로그를 먼저 보존한다. 이전 기준 앱 `kr.syncguide`는 삭제하지 않는다.
5. 앱을 열어 튜토리얼 켜기 → 좌석별 독립 온도 → 제안 확인 → 네, 체험할게요를 선택한다. 기대 결과는 운전석 21°C 유지, 동승석 24°C, SYNC 꺼짐이다.
6. `PleosGuide` logcat에서 `COMMAND_REQUESTED`/명령 관련 기록과 최종 `ACTION_RESULT:CONFIRMED`를 확인한다. ACK만 확인하고 통과로 판정하지 않는다.
7. 체감 버튼은 시험 입력임을 기록한다. Off → 앱 강제 종료 → 다시 열기에서 모드는 Off이고 학습 이력만 유지되는지 확인한다.

`tools/release_smoke.py`는 위 UI 절차를 자동 탭하고 녹화한다. `PLEOS_TRIAL`을 새 이름으로 지정해 기존 증거를 보존한다. `tools/restart_persistence.py`는 같은 설치본을 콜드 부팅한 뒤 기본 Off·이력·설정을 비교한다. 이번 런처 포커스 재시도는 `tools/resume_restart_check.py`와 run.json에 남겼다. 시험은 마이크·알림 권한을 ADB로 미리 부여하므로 권한 대화상자 사용자 선택 흐름의 검증을 포함하지 않는다. `tools/emulator_test.py`와 `tools/exception_trial.py`는 debug 전용 TestReceiver 및 ADB action을 사용한다. TestReceiver와 TEST_PCM 파일은 release에 포함하지 않는다.

## 결과와 증거

| 시험 | 결과 | 증거 |
|---|---|---|
| 안전 조건 단위 시험 | 9개 통과. 오래된 샘플/기어·UX 미확인/미지원 값/의도 구분/취소/온도 | `android/app/src/test/.../GuideSafetyTest.kt` |
| 통합 debug SYNC | 실제 SDK 21/21→21/24, dual=false, driver=21 CONFIRMED | `evidence/debug-trial/evidence.jsonl`, `03-sync-result.png` |
| 5개 모듈 흐름 | 자동 입력으로 제안·수락·안내·기록 확인. 위치/음장 분리 및 SPREAD 온도 유지 관측 | `evidence/debug-trial/` |
| 빈 좌석·중복·거절·D 전환 | 빈 좌석 SYNC 차단, 중복 세션 실패, 거절/주행 시 취소 확인 | `evidence/exception-trial/run.json` |
| 백그라운드·무응답 | Home 뒤 90초 만료 및 SDK 온도 변화 수신 확인 | 동일 |
| Gleo action 수신부 | foreground에서 SET/START/RESPOND와 callback success; 누락 asking, 잘못된 값/만료/중복 fail | 두 debug 시험 로그. source=UNVERIFIED_INTENT |
| Gleo background 모드 시작 | ADB 방송에서 ForegroundServiceStartNotAllowedException → fail callback | `evidence/exception-trial/all-debug-history.jsonl` |
| 공식 음성 | Locale.KOREAN의 ko- 오류 수정 후 Locale.KOREA/ko-KR TTS_DONE 관측. 반복 timeout도 관측 | `evidence/exception-trial/all-debug-history.jsonl` |
| 마이크 / TEST_PCM | 실제 사람 최종 인식 없음. 합성 PCM 별도 경로도 timeout; 제어로 전달 안 함 | `evidence/speech-trial/evidence.jsonl` |
| 기준 SYNC 앱 재현 | 이번 환경에서는 상태 읽기 후 초기화 ANR로 전체 절차 실패 | `evidence/baseline-reproduction/`; 과거 성공과 구분 |
| 최초 signed release 새 설치 | 21/21→21/24 실제 제어·재조회와 Off까지 부분 통과. 재시작 UI 검사는 중단, 이후 에뮬레이터 DDS 복구 실패로 전체 PASS 아님 | `evidence/release-smoke-first/run.json`, 스크린샷, `demos/Release_Emulator.mp4` |

최종 서명 release 검사는 `evidence/release-smoke-verified`에 PASS와 SDK 로그·화면·녹화를 보존했다. Off 후 콘솔 온도를 바꿔 새 SNAPSHOT이 없는지 확인하고, 강제 종료 전후의 전체 표시 이력과 다섯 체크박스 값을 비교했다. SOUND 안내를 false로 두어 기본값과 구별했다.

`evidence/restart-persistence`는 데이터 삭제 없이 AVD 콜드 부팅과 모드 On 강제 종료를 검사했다. 콜드 부팅 뒤 모드 Off, 다시 켠 뒤 이력·다섯 설정의 동일성을 확인했다. 직접 component 실행/런처 포커스 때문에 중단된 자동 탭과 수정 후 통과를 같은 run.json에 구별했다. 내부 SharedPreferences의 모든 timestamp 바이트를 추출한 시험은 아니며 화면에서 제공하는 기록을 정확히 비교했다.

첫 102.508초 부분 시험은 `evidence/release-smoke-first`, 과거 DDS 실패는 `evidence/release-smoke`, 종료 후 잠금 때문에 시작하지 못한 시험은 `evidence/restart-launch-lock`에 남아 있다. DDS 복구 직후 중간 시험은 `evidence/release-smoke-dds-first`에 보존했다. 최종 판정은 verified 폴더를 따른다. [DDS 복구 문서](dds-recovery.md)는 고정 IPv4의 준비 지연, 연속 준비 확인, 오래된 잠금의 비파괴 보관, 런처 포커스 대응을 설명한다. SELinux는 Enforcing이며 앱에 추가 특권을 부여하지 않았다.

콘솔의 차량 초기 상태 변경은 `CONSOLE_SEED`/`MANUAL_CONSOLE_SEED`, 실제 SDK 재조회는 `LIVE_SDK`, debug 입력은 `MOCK_EVENT`, action 주입은 `UNVERIFIED_INTENT`, PCM은 `TEST_PCM`이다. release UI의 앱 내부 `USER_REPORT` 기록도 `run.json`의 `AUTOMATED_UI`와 함께 해석해야 한다. `GUIDANCE` 등 앱 안내 이벤트에 쓰인 LIVE_SDK 표기만으로 물리 실행을 입증할 수 없다. `COMMAND_*`, 결과 재조회, `ACTION_RESULT`를 함께 확인한다.

## 남은 검증

- 사람이 PC/에뮬레이터 마이크에 발화한 STT 최종 인식, 실제 Gleo의 스키마 발견·인자 전달·callback 수신. 사용자가 2026-11-14에 음성 실사용 시험을 나중에 하기로 선택했다.
- 실제 Gleo A/C+라디오 복합 실행. 앱의 A/C OFF 관측은 인과 관계나 라디오 성공까지 입증하지 않는다.
- 정상 자원 조건의 음성 반복 안정성, 전화/내비/미디어와의 focus 충돌. 현재 시험은 stop/yield 호출과 타임아웃 로그까지다.
- 2시간 실시간 주행 관측 후 P 전환 제안 및 24시간 재안내 제한. 해당 로직 구현과 실제 경과 시간 검증을 구분한다.
- 실차 사양별 센서·권한·조작 메뉴, 주행 중 안전한 짧은 안내, 사용자 기능 발견·체감·재사용.

raw 후석/운전석 착좌의 의미, 전용 스트레칭·전동 벤트·음장 상태가 확인되기 전에는 이를 자동 성공/트리거로 해석하지 않는다.
