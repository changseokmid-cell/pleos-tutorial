# 구현 범위와 증거 기준

하나의 `kr.pleosguide` 앱. Vehicle 2.3.2, SpeechToText/TextToSpeech 3.3.1 ON_DEVICE를 사용한다. NaviHelper/FusedLocation은 현재 기능에 필요하지 않아 의존하지 않는다.

| 기능 | 구현 경로 | 검증할 경계 |
|---|---|---|
| SYNC | 사용자 요청과 수락 → capability → 연동 해제 → 독립 재조회 → 동승석 온도 설정 → 좌우/연동 재조회 | ACK는 완료가 아니다. 권한/지원성 실패는 수동 안내. 명령을 자동 재시도하지 않는다. |
| 에르고 | SDK 주행 시간 또는 앱이 직접 관측한 주행 시간 → P 전환 → 시트 버튼 안내 → 체감 기록 | OEM 스트레칭 제어/상태 API 미확인. 허리 지지 setter를 대체 실행하지 않는다. |
| 사운드 | 실제 요청 → 위치 안내 → 가운데 복원 응답 → 음장 비교 | CarAudioManager 권한 실제 probe. 자체 패닝은 사용하지 않는다. 사용자 응답만으로 차량 실행 확인을 기록하지 않는다. |
| SPREAD | 직풍과 더위 구별 → 수락 → 순정 SPREAD 안내 → 목표온도 유지 관측 → 체감 | FACE/FLOOR 변경을 사용하지 않는다. SPREAD 상태는 UNKNOWN이다. |
| Gleo | 3개 App Schema action/응답 + 순정 복합 요청 학습 | Broadcast 수신/송신과 실제 Gleo 음성 왕복은 별개. A/C 상태와 라디오 사용자 관측을 분리한다. |

샘플마다 값/영역/단위/시각/출처/오류를 기록한다. 값 없음과 false/0을 구별한다. 5초 이상 지난 값과 3초 이상 걸린 묶음은 조작에 사용하지 않는다.
튜토리얼은 사용자가 켠 FGS 한 개에서 동작한다. 한 번에 한 세션, 수락 중복 억제, 무응답 만료, 조건 이탈 취소, 음성 focus 반환, Off 시 SDK 해제를 구현한다. 프로세스 재시작 시 기본 Off와 로컬 학습 이력 보존을 구현했으나 해당 release 재시작 시험은 에뮬레이터 장애로 완료하지 못했다.

현재 첫 배포의 상세 체험/자동 공조 명령은 P 및 CarUxRestrictions 허용 조건에 제한한다. 주행 중 짧은 선제 음성 안내는 제품 목표이며, 충분한 주행/음성 충돌 검증 전 완료로 표시하지 않는다. 앱은 모든 주변 대화나 다른 앱 화면 탐색을 감시하지 않는다. 말하기 버튼, 알림의 말하기, Gleo action 또는 명시적 입력으로 요청한다.

## 안내 근거

- [그랜저 2027 시트 매뉴얼](https://ownersmanual.hyundai.com/full_webhelp/gn7/2027/ko_kr/safety-adj_front_seats-power_adjust.html): 스트레칭 버튼 순서 전신 → 허리 → 골반 → 꺼짐.
- [그랜저 공조 매뉴얼](https://ownersmanual.hyundai.com/full_webhelp/gn7/2027/ko_kr/convenience-auto_climate_ctrl-ctrl_in_manual_mode.html): SPREAD는 탑승자에게 직접 닿는 바람을 분산하는 전동 벤트 모드.
- [Connect-S 사운드 매뉴얼](https://ownersmanual.hyundai.com/ivi/Connect-S/AVNT/KOR/Korean/009_Vehiclesettings_12.html): 사운드 위치와 음장 사양, Centerpoint의 멀티채널 소스 제한. 차량/옵션별 실제 메뉴가 다르다.
- [Gleo App Schema](https://document.pleos.ai/docs/pleos-only/app-integration-guide/guide/app-capability), [callback](https://document.pleos.ai/docs/pleos-only/app-integration-guide/guide/action_callback).

테스트 결과는 evidence와 DEV_STATE.md에서 확인한다. 이 문서의 구현 경로 설명은 실행 통과 선언이 아니다.
