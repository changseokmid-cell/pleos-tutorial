# Pleos 통합 튜토리얼 개발 상태

2026-11-14 시작. 이 디렉터리는 별도 Git 저장소이며 기존 sync-tutorial 및 영상/연구 원본을 변경하지 않는다.

- 구현 중: 공통 차량 샘플, 세션, 공식 음성 입출력, 로컬 이력, Gleo 3개 action, 다섯 기능 모듈.
- 실행 환경: 로컬 JDK 17.0.21, Android SDK 35/Build Tools 35, PleosSync210 AVD 확인.
- 첫 AVD 기동: 호스트 commit memory 부족으로 실패. RAM 2048MB로 재시도 예정.
- 현재 신규 앱 실행 성공은 아직 없음. SDK 정적 검사를 실행 근거로 사용하지 않음.
- 다음: compile → SDK capability/음성 초기화 → SYNC 제어 재조회 → 안내 모듈/예외 → release 새 설치.

배포 전 필요한 외부 항목: GitHub 대상, 후속 영상 최종 승인, 공식 참가 정보/동의. 이메일 발송은 작업 범위 밖이다.
