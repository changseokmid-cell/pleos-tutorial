# 내 차 사용 안내

**차량 기능을 몰라 겪는 불편을 짧은 체험으로 바꾸는 Pleos Connect 차량용 Android 앱입니다.** 사용자가 튜토리얼을 켜고 요청하면 차량 상태를 확인하고 기능을 제안합니다. 동의를 받아 체험을 돕고, 차량 결과와 체감 응답을 따로 남겨 다음 사용으로 이어갑니다.

예를 들어 동승자가 춥다고 할 때 운전석 설정을 유지하며 동승석 온도만 높이는 방법을 안내합니다. 실제 Vehicle SDK로 SYNC를 끄고 **21/21°C → 21/24°C** 변화를 재조회했습니다. 조작과 함께 좌석별 독립 조절을 익히도록 안내와 체감 기록을 연결합니다.

![서명 APK에서 좌우 독립 온도를 확인한 화면](evidence/release-smoke-verified/03-confirmed-21-24.png)

## 심사위원께 권하는 읽는 순서

| 순서 | 자료 | 확인할 내용 |
|---|---|---|
| 1 · 제품 이해 | [3쪽 작품 소개 PDF](docs/proposal-public.pdf) / [심사 안내](docs/reviewer-guide.md) | 누구의 어떤 불편을 해결하는가 |
| 2 · 실제 실행 | [검증 Release](https://github.com/changseokmid-cell/pleos-tutorial/releases/tag/contest-round1-verified-20261114) | 서명 APK, 제출 ZIP, 실제 화면 녹화 |
| 3 · 코드 이해 | [구조와 코드 읽기](docs/architecture.md) | 입력 → 세션 → 차량 명령 → 재조회 → 이력 |
| 4 · 재현·한계 | [시험 결과](docs/testing.md) / [구현표](docs/implementation.md) | 성공 근거, 자동화 입력, 미검증 범위 |

저장소는 **비공개**이며 자료를 받으려면 접근 권한이 있는 GitHub 로그인이 필요합니다. 고객 경험 영화는 제품 의도를 보여 주는 연출입니다. APK 실구동 녹화와 구별해 [영상 목록](demos/README.md)에 표시했습니다. GitHub 보관은 공식 접수 완료를 뜻하지 않습니다.

## 현재 구현한 다섯 체험

공통 흐름은 **발견 → 제안·수락 → 체험 → 결과 확인 → 체감 기록**입니다. 상세 체험과 자동 공조 명령은 P 및 차량 UX 허용 상태에서 제공합니다.

| 체험 | APK가 하는 일 | 확인 범위 |
|---|---|---|
| 좌석별 독립 온도 · SYNC | 연동 해제, 동승석 온도 설정, 좌우 독립 재조회 | 실제 SDK 제어 성공. 운전석 21°C 유지 / 동승석 24°C |
| 에르고 스트레칭 | 장착 차량의 시트 버튼·모드 순서 안내 | 안내 흐름 시험. 스트레칭 모터 직접 제어 없음 |
| 사운드 위치·음장 | 위치 체험 → 가운데 복원 응답 → 음장 비교 | 단계 분리 시험. 순정 스피커·음장 직접 제어 없음 |
| 직풍 피하기 · SPREAD | 순정 메뉴 안내, 목표온도 유지 관측 | 안내와 온도 관측 시험. 전동 벤트 제어·모드 확인 없음 |
| Gleo 복합 요청 학습 | 복합 요청 문장, 마이크 양보, Schema 3개 action | ADB 수신부·callback 시험. 실제 자연어 왕복 미검증 |

공식 ON_DEVICE STT/TTS 3.3.1을 연결했고 한국어 TTS 완료를 관측했습니다. 시간 초과도 남아 있습니다. **사람의 마이크 발화와 순정 Gleo 실사용 시험은 사용자 요청으로 추후 진행합니다.** 자동화 수락·체감 버튼은 사용자 연구나 학습 효과의 증거가 아닙니다.

## 코드의 핵심

- [TutorialCoordinator.kt](android/app/src/main/java/kr/pleosguide/TutorialCoordinator.kt): 한 번에 한 체험, 제안·수락·실행·피드백·취소를 조정합니다.
- [VehicleContextRepository.kt](android/app/src/main/java/kr/pleosguide/VehicleContextRepository.kt): 지원성과 최신 차량 값을 읽고 명령 접수와 결과 재조회를 구별합니다.
- [Models.kt](android/app/src/main/java/kr/pleosguide/Models.kt): 값의 출처·시각·지원성, 안전 조건과 세션 상태를 정의합니다.
- [Stores.kt](android/app/src/main/java/kr/pleosguide/Stores.kt): 초기화할 실행 상태와 보존할 설정·체험 기록을 분리합니다.

화면·서비스·음성·Gleo의 역할과 읽을 함수는 [코드 안내](docs/architecture.md)에서 이어집니다. 검증한 Android 소스와 APK를 유지하면서 문서의 설명 순서와 코드 탐색 경로를 재구성했습니다.

## 빌드와 실행

패키지 `kr.pleosguide`, 버전 `1.0.0`. JDK 17, Android SDK Platform 35 / Build Tools 35.0.0 및 Maven 접근이 필요합니다. Gradle 8.9 Wrapper를 포함하고 SDK AAR·서명키는 포함하지 않습니다.

```powershell
$env:JAVA_HOME = 'C:/path/to/jdk-17'
$env:ANDROID_HOME = 'C:/path/to/android-sdk'
./tools/build.ps1
```

Windows 출력은 `%LOCALAPPDATA%/PleosSyncLab/tutorial-build/outputs/apk/debug/app-debug.apk`입니다. 한글 경로의 JUnit 클래스 로딩 문제를 피하도록 빌드 출력만 ASCII 경로에 둡니다. Linux/macOS는 `android/`에서 `bash ./gradlew :app:assembleDebug :app:testDebugUnitTest`를 사용할 수 있으나 이번 실행 검증은 Windows에서 했습니다.

서명 빌드는 외부 keystore alias `submission`과 `PLEOS_KEYSTORE`, `PLEOS_STORE_PASSWORD`, `PLEOS_KEY_PASSWORD` 환경 변수를 설정해 `./tools/build.ps1 -Release`로 실행합니다. 키·암호는 저장소에 넣지 않습니다.

```text
adb -s emulator-5572 install apk/PleosTutorial-1.0.0.apk
adb -s emulator-5572 shell am start --user current -n kr.pleosguide/.MainActivity
```

검증 환경은 Pleos Connect 2.1.0 / API 34입니다. 일반 휴대전화에는 차량 서비스가 없습니다. 앱에서 튜토리얼을 켜고 P 상태에서 체험을 선택합니다. [DDS 준비 확인과 재현 명령](docs/testing.md)을 먼저 읽어 주세요. Android 부팅 완료와 차량 서비스 준비 완료는 다른 시점일 수 있습니다.

## 증거·버전·후속 과제

[서명 release 실행 기록](evidence/release-smoke-verified/run.json), [재시작 검사](evidence/restart-persistence/run.json), [DDS 복구 기록](docs/dds-recovery.md)이 이번 검증을 설명합니다. 이전 실패와 [첫 후보 Release](https://github.com/changseokmid-cell/pleos-tutorial/releases/tag/contest-round1-candidate-20261114)는 보존합니다.

APK Android 소스 기준은 `4fe8a913b52770218757791bf1749c2fb8b35ef9`이며 [빌드 검증 기록](evidence/build/release-audit.json)에 연결됩니다. 검증 Release의 `submission-manifest.json`은 문서·도구·증거를 포함한 최종 commit과 APK·ZIP·영상 해시를 연결합니다.

실제 음성/Gleo, 장시간 주행 후 제안, 실차 사양별 지원, 사용자 학습·재사용 효과는 후속 검증입니다. [현재 상태](DEV_STATE.md), [제출 절차](docs/submission.md), [개발 계획](docs/proposal-public.md)을 참고하세요.
