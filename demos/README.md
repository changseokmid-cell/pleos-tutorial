# 영상 목록

고객 경험 영화와 실제 APK 녹화를 구분한다. 아래 원본은 이 Git 저장소 밖의 제작 보관소에 있고, 해시·버전·승인 상태는 [media-manifest.json](media-manifest.json)에 고정했다. 현재는 비공개 GitHub Release에 보관되어 저장소 접근 권한이 필요하다.

| 기능 | 현재 연결본 | 길이 | 상태 |
|---|---|---|---|
| SYNC | [비공개 보관본](https://github.com/changseokmid-cell/pleos-tutorial/releases/download/contest-round1-candidate-20261114/SYNC_Approved_339b0091.mp4) | 47.94초 | 사용자 승인본 |
| ERGO | [비공개 보관본](https://github.com/changseokmid-cell/pleos-tutorial/releases/download/contest-round1-candidate-20261114/ERGO_Review_f73a39df.mp4) | 123.75초 | 신규 검토본, 최종 승인 미확인 |
| SOUND | [비공개 보관본](https://github.com/changseokmid-cell/pleos-tutorial/releases/download/contest-round1-candidate-20261114/SOUND_Review_2befdabe.mp4) | 101.01초 | 신규 검토본, 최종 승인 미확인 |
| SPREAD | [비공개 보관본](https://github.com/changseokmid-cell/pleos-tutorial/releases/download/contest-round1-candidate-20261114/SPREAD_Review_abd18197.mp4) | 61.27초 | 신규 검토본, 최종 승인 미확인 |
| GLEO | [비공개 보관본](https://github.com/changseokmid-cell/pleos-tutorial/releases/download/contest-round1-candidate-20261114/GLEO_Review_9aca15d5.mp4) | 69.50초 | 신규 검토본, 최종 승인 미확인 |

이 표의 링크는 저장소 접근 권한이 있는 GitHub 로그인에서 확인했다. 실제 접수용으로 공개 전환할 때 로그인 없이 다시 접근성을 검사한다. 후속 네 편의 이전 revision-2는 현재 목록의 최신본으로 사용하지 않는다.

## 실제 앱 녹화

[Release_Emulator.mp4](https://github.com/changseokmid-cell/pleos-tutorial/releases/download/contest-round1-candidate-20261114/Release_Emulator.mp4)는 검증 묶음 ZIP에 포함하는 102.508초의 실제 에뮬레이터 화면 녹화다. Android screenrecord는 오디오를 녹음하지 않는다. UI 수락과 체감 버튼은 자동화 입력이며 실제 사람 음성·만족·학습을 입증하지 않는다. 새 설치, P 상태, SYNC 실제 제어와 Off까지 확인했다. 재시작 검사는 중단되어 전체 통과가 아니다. [부분 성공·중단 기록](../evidence/release-smoke-first/run.json) 및 [재현 문서](../docs/testing.md)와 함께 확인한다.

## 제작과 구현 경계

고객 경험 영화의 그랜저·배역·차량 UI는 제작 자료이며 실차 앱 동작 촬영이 아니다. 영화에 나오는 주행 중 안내, 스트레칭·음장·SPREAD 자동 실행은 이번 APK의 검증 범위와 다르다. APK는 세 기능의 순정 조작 안내를 제공한다. SYNC 영화의 음성은 Gleo를 연기한 합성 보이스이며 실제 순정 Gleo 음성 증거가 아니다.

원본 Blender ZIP과 중간 미디어는 제작 폴더에 보존한다. 이번 검증 묶음에는 권리·최종 선택이 정리되지 않은 고객 경험 영화를 일괄 복사하지 않았다.
