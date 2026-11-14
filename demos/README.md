# 영상 목록

고객 경험 영화와 실제 APK 녹화를 구분한다. 아래 원본은 이 Git 저장소 밖의 제작 보관소에 있고, 해시·버전·승인 상태는 [media-manifest.json](media-manifest.json)에 고정했다. 공개 Release URL은 아직 없다.

| 기능 | 현재 연결본 | 길이 | 상태 |
|---|---|---|---|
| SYNC | [로컬 제작본](../../outputs/20261113-sync-verbatim/SYNC_ChatLog.mp4) | 47.94초 | 사용자 승인본 |
| ERGO | [로컬 제작본](../../outputs/20261114-ergo-film/full-rebuild-20261114/final.mp4) | 123.75초 | 신규 검토본, 최종 승인 미확인 |
| SOUND | [로컬 제작본](../../outputs/20261114-sound-film/full-rebuild-20261114/final.mp4) | 101.01초 | 신규 검토본, 최종 승인 미확인 |
| SPREAD | [로컬 제작본](../../outputs/20261114-spread-film/sync-verified-20261114/final.mp4) | 61.27초 | 신규 검토본, 최종 승인 미확인 |
| GLEO | [로컬 제작본](../../outputs/20261114-gleo-film/full-rebuild-20261114/final.mp4) | 69.50초 | 신규 검토본, 최종 승인 미확인 |

이 표의 로컬 제작본 링크는 공유 프로젝트 안에서만 열린다. 제출용 공개 저장소에서는 승인된 MP4를 Release에 업로드하고 실제 다운로드 URL로 바꾼 뒤 접근성을 검사한다. 후속 네 편의 이전 revision-2는 현재 목록의 최신본으로 사용하지 않는다.

## 실제 앱 녹화

[Release_Emulator.mp4](Release_Emulator.mp4)는 검증 묶음 ZIP에 포함하는 102.508초의 실제 에뮬레이터 화면 녹화다. Android screenrecord는 오디오를 녹음하지 않는다. UI 수락과 체감 버튼은 자동화 입력이며 실제 사람 음성·만족·학습을 입증하지 않는다. 새 설치, P 상태, SYNC 실제 제어와 Off까지 확인했다. 재시작 검사는 중단되어 전체 통과가 아니다. [부분 성공·중단 기록](../evidence/release-smoke-first/run.json) 및 [재현 문서](../docs/testing.md)와 함께 확인한다.

## 제작과 구현 경계

고객 경험 영화의 그랜저·배역·차량 UI는 제작 자료이며 실차 앱 동작 촬영이 아니다. 영화에 나오는 주행 중 안내, 스트레칭·음장·SPREAD 자동 실행은 이번 APK의 검증 범위와 다르다. APK는 세 기능의 순정 조작 안내를 제공한다. SYNC 영화의 음성은 Gleo를 연기한 합성 보이스이며 실제 순정 Gleo 음성 증거가 아니다.

원본 Blender ZIP과 중간 미디어는 제작 폴더에 보존한다. 이번 검증 묶음에는 권리·최종 선택이 정리되지 않은 고객 경험 영화를 일괄 복사하지 않았다.
