# Pleos 통합 튜토리얼 개발 상태

2026-11-14. 단일 개발창과 별도 Git 저장소 `pleos-tutorial`에서 진행했다. 기존 sync-tutorial, 연구·영상 원본, ev6-cockpit-lab, artifacts는 보존했다.

## 구현과 실행

`kr.pleosguide` 1.0.0에 공통 차량 샘플·capability·한 세션·공식 ON_DEVICE STT/TTS·로컬 이력·Gleo 3개 action·다섯 기능 안내를 통합했다. 상세 체험과 자동 공조 명령은 P/CarUxRestrictions 허용 상태로 제한한다. 주행 중 선제 안내는 후속 검증 대상이다.

- debug 실제 SDK에서 SYNC 해제와 동승석 온도 설정 후 21/21 → 21/24°C, 운전석 21°C 유지, dual=false를 재조회했다. 수락은 MOCK_EVENT다.
- signed release 새 설치에서도 같은 결과와 Off를 확인했다. 첫 재시작 검사는 차량의 왼쪽 pane 선택 및 이후 에뮬레이터 캡처 정지로 중단됐다. 기본/software GPU cold boot 복구에서도 DDS participant 생성 실패와 console 503이 지속되어 전체 release PASS로 표시하지 않았다. 102.508초 녹화, 부분 성공과 중단은 `evidence/release-smoke-first`, 복구 실패는 `evidence/release-smoke`에 보존했다.
- 빈 동승석 차단, 중복 억제, 거절·D 전환 취소, Home 뒤 90초 무응답 종료와 SDK 변화 수신을 확인했다.
- 에르고·사운드·SPREAD는 공식 매뉴얼에 근거한 순정 조작 안내와 응답 기록이다. 전용 스트레칭·음장·전동 벤트 자동 제어는 없다.
- Gleo action은 앱이 열린 상태에서 ADB SET/START/RESPOND와 success/asking/fail callback 송신을 확인했다. background ADB SET은 OS가 FGS 시작을 거부했다. 실제 Gleo 자연어 왕복은 미검증이다.
- Locale.KOREA(ko-KR) 수정 후 공식 TTS_DONE을 관측했으나 반복 timeout도 있다. 실제 사람 STT와 TEST_PCM 최종 인식 성공 없음.
- 단위 시험 9개, release 빌드/lintVital, 서명 검증 통과. release의 debug flag/TestReceiver/시험 PCM 제외와 schema 포함을 확인했다.

## 지원성과 환경

Pleos Connect 2.1.0 / API34 / 2560×1440. HVAC READ_WRITE, 동승석 15~30°C/0.5°C. 착좌 반전은 정확한 이미지 fingerprint의 동승석에만 적용한다. 운전석/후석 raw 의미 매핑은 UNKNOWN이다. 현재 trip 시간은 ERROR_NOT_SUPPORTED_PROPERTY. CarAudioManager 획득 가능, 오디오 제어 권한 -1.

호스트 메모리 압박·서비스 준비 지연을 관측했다. SDK 초기화/호출을 IO로 옮겨 첫 FGS ANR을 해결했다. 이번 기존 기준 앱 재현은 ANR로 전체 실패했으며 과거 성공 기록과 구분했다. 재기동 후 DDS 노드 생성 실패/503도 발생했다. 최종 결과와 재현 조건은 [testing.md](docs/testing.md), 실행별 run.json을 따른다.

## 제출 산출물과 Git

[README](README.md), [공개 소개 PDF](docs/proposal-public.pdf), [공식 양식 반영용 개발 계획](docs/proposal-public.md), [구현표](docs/implementation.md), [시험 문서](docs/testing.md)를 작성했다. APK는 `apk/PleosTutorial-1.0.0.apk`, 검증/hash는 `evidence/build/release-audit.json`에 있다. Git 일반 이력에 APK·MP4·키·캐시를 넣지 않는다.

Git 단계: `bda0675` 격리 저장소/계약 → `b2991b5` 통합 모듈 → `4fe8a913b52770218757791bf1749c2fb8b35ef9` IO·locale 수정과 HVAC 검증. 현재 APK의 Android 소스 기준은 마지막 hash다. 후속 문서·증거 commit과 ZIP은 `dist/submission-manifest.json`에서 연결한다. 패키징 시 Android diff가 비어 있는지 대조한다.

[영상 목록](demos/README.md)은 승인 SYNC와 후속 네 편의 최신 확인 검토본을 구분한다. 작업창의 제작 완료를 사용자 최종 승인으로 간주하지 않는다. 사용자 요청으로 [비공개 GitHub](https://github.com/changseokmid-cell/pleos-tutorial)에 연결했고 후보 태그/Release에 소스·APK·문서·영상 14개 첨부파일을 보관했다. 후보 commit은 `35c4f74a2c5a0cbcfe8755c226d2f7b371ef4706`, 검증 기록은 [github-storage.json](docs/github-storage.json)이다. 공식 참가자 정보는 미지정이며 이메일은 발송하지 않았다.

## 남은 외부 검증과 2차 계획

실제 사람 STT와 순정 Gleo 음성 시험은 사용자가 2026-11-14에 나중으로 남기도록 결정했다. 정상 자원 조건의 음성 반복·focus 충돌, 2시간 주행 후 자동 제안, 실차 사양별 지원과 사용자 학습·재사용 검증도 남는다. 영상 최종 선택·참가자 정보와 동의·접수용 공개 전환은 별도다. 비공개 보관을 공식 접수 완료로 표시하지 않는다.
