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

[Release_Emulator.mp4](https://github.com/changseokmid-cell/pleos-tutorial/releases/download/contest-round1-verified-20261114/Release_Emulator.mp4)는 최종 서명 APK의 실제 화면 녹화(126.812초)다. UI 수락·체감 응답은 자동화 입력이며 녹음된 음성은 없다. SDK 21/21→21/24 제어, Off, 재실행·이력 확인을 [실행 기록](../evidence/release-smoke-verified/run.json)과 함께 본다. 전체 AVD 콜드 부팅 및 On 강제 종료 검사는 [별도 로그·화면](../evidence/restart-persistence/run.json)에 있다.

이전 102.508초 부분 녹화는 첫 후보 Release에 그대로 보존했다. 그때의 미완료와 새 검증본의 PASS를 혼동하지 않는다.

## 제작과 구현 경계

고객 경험 영화의 그랜저·배역·차량 UI는 제작 자료이며 실차 앱 동작 촬영이 아니다. 영화에 나오는 주행 중 안내, 스트레칭·음장·SPREAD 자동 실행은 이번 APK의 검증 범위와 다르다. APK는 세 기능의 순정 조작 안내를 제공한다. SYNC 영화의 음성은 Gleo를 연기한 합성 보이스이며 실제 순정 Gleo 음성 증거가 아니다.

원본 Blender ZIP과 중간 미디어는 제작 폴더에 보존한다. 이번 검증 묶음에는 권리·최종 선택이 정리되지 않은 고객 경험 영화를 일괄 복사하지 않았다.
