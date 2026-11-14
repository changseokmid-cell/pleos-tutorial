# 중간 실행 기록

DDS 복구 직후 동일 서명 APK에서 SDK 제어·Off·이력 유지가 관측됐다. app-log.txt/evidence.jsonl과 화면·영상은 이 시험의 원본이다. 이후 진단용 helper 호출이 run.json을 한 개 진단 이벤트로 덮어써 이 폴더의 run.json은 전체 실행 순서를 대표하지 않는다. 복구한 순서를 추정해 채워 넣지 않았다. 덮어쓰기 방지와 런처 포커스 처리를 보완한 뒤 release-smoke-verified에서 전체 흐름을 새로 실행하고 최종 판정했다.
