# Pleos 통합 튜토리얼 개발 상태

2026-11-14 시작. 이 디렉터리는 별도 Git 저장소이며 기존 sync-tutorial 및 영상/연구 원본을 변경하지 않는다.

- 구현: 공통 차량 샘플, 세션, 공식 ON_DEVICE 음성 입출력, 로컬 이력, Gleo 3개 action, 다섯 기능 모듈. 실제 통합 실행 검증 중.
- 실행 환경: 로컬 JDK 17.0.21, Android SDK 35/Build Tools 35, PleosSync210 AVD 확인.
- 첫 AVD 기동: 호스트 commit memory 부족. RAM 2048MB/2 cores로 부팅, API34/기존 2.1.0 이미지와 ADB 연결.
- debug 빌드 및 안전 조건 단위 테스트 9개 통과. Windows 한글 경로의 JUnit ClassNotFound를 ASCII 빌드 출력 경로로 해결했다. 출력: `%LOCALAPPDATA%/PleosSyncLab/tutorial-build`.
- 첫 실행에서 SDK 초기화/호출이 메인 스레드를 붙잡아 FGS ANR 발생. SDK 초기화와 차량 probe/poll을 IO로 옮겨 다시 빌드/테스트 통과. 수정 APK의 실제 재시험 진행 중.
- Virtual Console 초기 `emulator_inactive`/503은 브리지 준비 지연과 연결 유지 문제로 관측. 콘솔 원문의 `/browser/session` heartbeat를 유지한 뒤 gear Park 요청 200/bridge_ready=true 확인.
- 기존 SYNC 재현 시험 진행 중. 신규 차량 제어/음성 성공은 아직 기록하지 않음.
- 11/14 통합 debug 시험: 실제 SDK 두 명령(setHvacDual=false, 동승석 setHvacTemperature=24) 후 21/21 → 21/24, 운전석 유지/연동 Off 독립 재조회 CONFIRMED. 수락은 MOCK_EVENT이며 실제 음성 수락 아님.
- 다섯 기능 안내/응답/이력 흐름, Gleo 수신부 asking/fail, CarUxRestrictions P=0/D=80 관측. 세션 테스트 응답은 실제 사용자 체감/학습 증거 아님.
- 음성 첫 오류는 Locale.KOREAN의 ko-가 지원되지 않아 발생. Locale.KOREA(ko-KR)로 고친 후 공식 ON_DEVICE TTS_DONE 확인. 마이크 입력은 첫 준비 지연/무응답을 관측했고 실제 사람 인식은 미검증. TEST_PCM 별도 시험 진행 중.
- 실제 capability: 공조 READ_WRITE, 동승석 15~30°C/0.5°C 간격. getTripCurrentDrivingTime은 ERROR_NOT_SUPPORTED_PROPERTY. CarAudioManager 접근 가능, CAR_CONTROL_AUDIO_SETTINGS 권한 -1. 스트레칭/SPREAD/음장 전용 제어 미구현.
- 기존 기준선 재현은 빈 좌석/공조/22·22 읽기까지 확인했으나 현재 저메모리 환경에서 기존 앱 초기화 ANR로 전체 절차 실패. 이전 성공 기록은 보존하고 이번 실패를 새 성공으로 덮지 않음.
- targetSdk33, 서명한 release 빌드 및 lintVital 통과. 서명키/암호는 저장소 밖 로컬 도구 폴더에 있으며 비공개 유지. 다음: release 새 설치·실구동 녹화·제출 묶음.

## 로컬 Git 단계

- `bda0675`: 제출 전용 저장소/공통 데이터 계약.
- `b2991b5`: 다섯 모듈, 음성, Gleo, 시험 도구.
- 후속 IO/빌드 경로 수정은 실행 검증 후 커밋 예정.

## 원본/영상 상태

SYNC 확정 영상은 이전 사용자 승인본 그대로 유지한다. Gleo 및 에르고 제작창은 11월 14일 새 음성/영상 최종 출력 작업 중인 것을 읽기 확인했다. 후속 네 편을 최종 승인으로 표시하지 않는다. 사운드 원문 스냅샷 파일이 빈 파일임을 발견해 공식 매뉴얼 URL을 다시 열어 본문과 음원 제약을 확인했다.

배포 전 필요한 외부 항목: GitHub 대상, 후속 영상 최종 승인, 공식 참가 정보/동의. 이메일 발송은 작업 범위 밖이다.
