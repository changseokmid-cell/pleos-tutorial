# 내 차 사용 안내

비공개 GitHub 보관본입니다. [고정 제출 후보 Release](https://github.com/changseokmid-cell/pleos-tutorial/releases/tag/contest-round1-candidate-20261114)에서 [제출 ZIP](https://github.com/changseokmid-cell/pleos-tutorial/releases/download/contest-round1-candidate-20261114/PleosTutorial-submission-35c4f74a2c5a.zip), [서명 APK](https://github.com/changseokmid-cell/pleos-tutorial/releases/download/contest-round1-candidate-20261114/PleosTutorial-1.0.0.apk), [공개 소개 PDF](https://github.com/changseokmid-cell/pleos-tutorial/releases/download/contest-round1-candidate-20261114/proposal-public.pdf), [실구동 녹화](https://github.com/changseokmid-cell/pleos-tutorial/releases/download/contest-round1-candidate-20261114/Release_Emulator.mp4)를 받을 수 있습니다. 저장소 접근 권한이 있는 GitHub 로그인이 필요합니다.

고정 후보 commit은 `35c4f74a2c5a0cbcfe8755c226d2f7b371ef4706`입니다. 이후 기본 브랜치의 변경은 보관 위치·검증 기록을 연결하는 문서 변경입니다. [업로드·해시 검증 기록](docs/github-storage.json)

Pleos Connect 차량에서 몰랐던 기능을 필요한 순간에 체험하며 익히는 Android 앱입니다. 사용자가 튜토리얼 모드를 켜고 명시적으로 요청하면 차량 상태와 연결해 안내합니다. 패키지 `kr.pleosguide`, 버전 `1.0.0`.

현재 제출 후보에는 SYNC, 에르고 스트레칭, 사운드 위치·음장, SPREAD, Gleo 복합 요청 학습을 하나의 세션·음성·차량 입력·이력으로 통합했습니다. 상세 체험과 공조 명령은 P 및 차량 UX 허용 상태에서 제공합니다. 주행 중 선제 안내는 후속 검증 대상입니다.

| 기능 | 현재 동작 | 실행 증거 범위 |
|---|---|---|
| SYNC | 수락 후 연동 해제, 동승석 목표온도 설정, 좌우 독립 재조회 | Pleos 에뮬레이터 실제 SDK에서 21/21°C → 21/24°C, 운전석 21°C 유지 확인 |
| 에르고 | 장착 차량의 시트 버튼·모드 안내, 체감·재사용 응답 기록 | 안내 세션 시험. 스트레칭 모터 제어 및 2시간 자동 제안 실시간 시험 미완료 |
| 사운드 | 소리 위치 체험 → 가운데 복원 응답 → 별도 음장 비교 | 단계 분리 시험. 앞뒤 스피커·음장 직접 제어 없음 |
| SPREAD | 직풍 불편 구별, 순정 메뉴 안내, 목표온도 유지 관측 | 안내 및 온도 관측 시험. 전동 벤트 SPREAD 제어·상태 확인 없음 |
| Gleo | App Schema 3개 action/질문·실패·성공 callback, 복합 요청 학습 | ADB 수신부 시험. 실제 Gleo 음성 → 앱 → 응답 왕복 미검증 |

음성은 공식 ON_DEVICE STT/TTS 3.3.1을 사용합니다. 한국어 TTS 완료를 관측했지만 반복 시간 초과도 있었습니다. 실제 사람 음성의 STT 성공, 순정 Gleo 복합 요청 성공, 사용자 체감·학습 효과는 입증하지 않았습니다. 자동화된 수락과 체감 응답은 사용자 연구 결과가 아닙니다.

## 읽는 순서

- [공개 작품 소개 PDF](docs/proposal-public.pdf), [공식 양식에 반영할 개발 계획](docs/proposal-public.md)
- [구현·지원 범위](docs/implementation.md), [시험 환경·재현·결과](docs/testing.md)
- [고객 경험 영상과 실구동 녹화](demos/README.md), [APK 안내](apk/README.md)
- [현재 개발 상태](DEV_STATE.md), [제출 절차와 남은 외부 항목](docs/submission.md)

## 빌드

JDK 17, Android SDK Platform 35 / Build Tools 35.0.0, 인터넷 Maven 접근이 필요합니다. Gradle 8.9 Wrapper를 포함합니다. SDK AAR와 서명키는 포함하지 않습니다.

```powershell
$env:JAVA_HOME = 'C:/path/to/jdk-17'
$env:ANDROID_HOME = 'C:/path/to/android-sdk'
./tools/build.ps1
```

기본 출력은 `%LOCALAPPDATA%/PleosSyncLab/tutorial-build/outputs/apk/debug/app-debug.apk`입니다. 한글 Windows 경로에서 JUnit 클래스 로딩 실패가 발생해 빌드 출력만 ASCII 경로로 분리했습니다. Linux/macOS 환경은 `android/`에서 `bash ./gradlew :app:assembleDebug :app:testDebugUnitTest`로 빌드할 수 있습니다. Windows만 실제 빌드 검증했습니다.

릴리스는 외부 개인 keystore의 alias `submission`과 환경 변수 `PLEOS_KEYSTORE`, `PLEOS_STORE_PASSWORD`, `PLEOS_KEY_PASSWORD`를 지정한 뒤 `./tools/build.ps1 -Release`로 만듭니다. 암호나 키를 커밋하지 마세요. 재빌드 APK는 서명과 ZIP 생성 시각에 따라 제출 APK와 바이트 해시가 달라질 수 있습니다.

## 설치와 실행

Pleos Connect 2.1.0 / Android 14 API 34 AVD에서 검증했습니다. 일반 휴대전화에서는 차량 서비스가 없어 동일하게 동작하지 않습니다.

```text
adb -s emulator-5572 install apk/PleosTutorial-1.0.0.apk
adb -s emulator-5572 shell am start --user current -n kr.pleosguide/.MainActivity
```

앱에서 튜토리얼을 켜고 마이크 권한을 선택합니다. P 상태에서 차량 신호가 준비되면 다섯 체험을 선택할 수 있습니다. SYNC 재현 조건과 콘솔 연결은 [시험 문서](docs/testing.md)에 있습니다. Off의 해제를 확인했습니다. 프로세스 재시작 시 기본 Off와 로컬 학습 이력 보존은 구현했으나 release 재시작 검사는 에뮬레이터 문제로 완료하지 못했습니다. 서버 계정이나 외부 음성 API는 사용하지 않습니다.

## 증거와 배포

`evidence/`는 실제 차량 SDK 값, 콘솔로 만든 차량 상황, ADB/자동 UI 입력을 구별합니다. 고객 경험 영화는 제품 의도를 설명하며 APK 녹화와 별도입니다. 미확인 기능의 자동 실행을 구현 완료로 취급하지 않습니다.

소스는 이 디렉터리의 독립 Git 저장소입니다. 기존 연구·영상·이전 SYNC 앱은 별도 보존합니다. 사용자 요청으로 `changseokmid-cell/pleos-tutorial` 비공개 저장소와 Release에 보관했습니다. 승인 SYNC와 후속 네 편의 검토본도 상태를 구분해 Release에 첨부했습니다. 공식 접수나 로그인 없는 공개 배포를 완료한 것은 아닙니다.
