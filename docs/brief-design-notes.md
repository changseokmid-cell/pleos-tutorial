# 작품 소개서 편집 기준

2026-11-15 새 작품 소개서를 작성했습니다. 앱 소개, 다섯 고객 경험, 구현과 다음 개발을 A4 세 쪽으로 구성했습니다. 기존 공개 PDF의 표 중심 편집과 기술 상태 나열을 줄이고, 팀이 제작한 영상 장면과 실제 실행 화면을 설명과 함께 배치했습니다.

## 확인한 편집 참고 자료

- [현대자동차 그랜저 카탈로그](https://www.hyundai.com/contents/repn-car/catalog/grandeur-hybrid-catalog.pdf): 실제 PDF의 2쪽과 7쪽을 확인했습니다. 큰 이미지와 검은 제목, 짧은 설명, 여백의 비율을 참고했습니다. 해당 카탈로그의 사진·문구·로고는 재사용하지 않았으며, 차량 사양 근거로 사용하지 않았습니다.
- [Design Council, Design methods for developing services](https://www.designcouncil.org.uk/fileadmin/uploads/dc/Documents/DesignCouncil_Design%2520methods%2520for%2520developing%2520services.pdf): 실제 PDF의 3쪽과 11쪽을 확인했습니다. 사례 이미지 옆의 설명과 두 단 본문 구성, 제목 단계와 문단 길이를 참고했습니다.
- 공식 공모전 접수양식: 기획 배경·사용 시나리오·개발 계획이라는 읽기 순서와 개인정보를 작품 소개에 넣지 않는 작성 원칙을 따랐습니다. 참가자 정보가 있는 신청서는 공개하지 않습니다.

## 이미지와 검증 범위

고객 경험 그림은 `demos/thumbnails`의 기존 영상 장면이며 실제 기능 실행 증거가 아닙니다. 3쪽은 `evidence/release-smoke-verified/03-confirmed-21-24.png`를 그대로 사용한 실제 에뮬레이터 화면입니다. 영상 링크와 APK·시험 자료를 PDF 안에서 열 수 있습니다. Android 소스, APK, 기존 영상과 시험 결과는 변경하지 않았습니다.

재생성: `python tools/build_experio_brief.py`. 필요한 패키지는 reportlab, Pillow, pypdfium2입니다. 글꼴 경로는 `PLEOS_FONT`와 `PLEOS_BOLD_FONT`로 지정할 수 있습니다. 기존 `tools/build_public_pdf.py`는 이전 버전의 작성 도구입니다.
