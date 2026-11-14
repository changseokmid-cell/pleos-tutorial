# DDS 복구와 재시작 조건

2026-11-14, 동일 Pleos Connect 2.1.0 AVD와 동일 서명 APK에서 차량 브리지·공조 DDS 송수신을 복구했습니다. Android 부팅 완료만 확인하던 시험 절차를 **실제 차량 전송 계층의 준비 확인**으로 보강했습니다.

## 관측한 원인과 복구

이미지의 [DDS 설정 원문](../evidence/dds-recovery/vhal-cyclonedds.xml)은 `NetworkInterfaceAddress`를 `10.0.2.15`로 고정합니다. [VHAL init 설정](../evidence/dds-recovery/vhal-service-init.txt)은 이 XML을 사용합니다. 부팅 직후 eth0에는 IPv6만 있었고, wlan0의 IPv4는 10.0.2.16이었습니다. 이때 `network eth0 is not ready yet`와 `Participant was not created`가 반복됐습니다.

이후 emulator RIL이 eth0에 10.0.2.15를 할당하자 VHAL이 IPv4를 인식했고, 콘솔 heartbeat에서 DDS `runtime-started`, `available`, `emulation-source-active`가 이어졌습니다. [첫 부팅 발췌](../evidence/dds-recovery/first-boot-excerpts.json)와 [재부팅 발췌](../evidence/dds-recovery/coldboot-boot-excerpts.json)에 같은 순서를 보존했습니다. 두 번째 기록에서는 AVD 표시 시각 01:59:06.414 주소 할당 → 01:59:11.633 DDS 활성화입니다.

따라서 이번 부팅 구간의 직접 장애는 DDS가 요구하는 주소의 준비 지연으로 좁혀졌습니다. 호스트 자원이 그 지연에 얼마나 영향을 주었는지, 과거 모든 중단이 같은 원인이었는지까지 단정하지 않습니다. `/data` 여유 3.5GB, 게스트 가용 메모리 약 2.4GB를 확인했으며 디스크 고갈 증거는 없었습니다.

## 재현 절차의 수정

1. `-no-snapshot -memory 4096 -cores 4 -gpu host -no-window`로 콜드 부팅했습니다. 두 번째 Android 부팅 완료는 [시작 로그](../evidence/dds-recovery/coldboot-start.txt)의 88,974ms입니다. 그 뒤에도 차량 네트워크가 준비될 때까지 기다립니다.
2. `hold_console.py`로 콘솔 heartbeat를 유지합니다. HTTP 200만으로 활성 상태라고 출력하던 도구를 `active=true` 확인으로 수정했습니다.
3. `wait_vehicle_ready.py`는 eth0 주소, 활성 세션, gear bridge, 공조 publisher/subscriber의 `all=true`를 **세 번 연속** 확인합니다. 최대 600초 후에도 미준비면 실패하며 차량 명령을 실행하지 않습니다.
4. 준비 후 서명 APK의 SDK 명령·재조회와 재시작 이력을 시험합니다. 준비 상태가 나중에 바뀌는 경우를 앱의 최신 샘플·지원성 검사로 다시 제한합니다.

```powershell
adb -s emulator-5572 forward tcp:18088 tcp:8088
# 이전 시험에서 만든 .local/stop-console이 있다면 해당 종료 표식을 제거한 뒤 실행
python tools/hold_console.py
# 별도 터미널
python tools/wait_vehicle_ready.py --out evidence/my-dds-check
python tools/release_smoke.py
```

기존 결과를 덮어쓰지 않으려면 실행 전에 `PLEOS_TRIAL`을 새 폴더 이름으로 지정합니다. 도구는 기존 run.json의 묵시적 덮어쓰기를 거부합니다. 이 도구들의 ADB serial·SDK 위치는 이번 전용 Windows 실험 환경 기준입니다.

## 재시작 중 추가로 해결한 두 문제

첫 전체 재시작 시 종료된 PID 30704의 `snapshot.lock.lock`, `hardware-qemu.ini.lock`이 남아 emulator가 시작하지 못했습니다. [실패 로그](../evidence/restart-launch-lock/emulator-start.txt)를 보존했습니다. emulator/qemu와 해당 PID가 실행 중이지 않음을 확인하고, 두 잠금 디렉터리만 AVD 안 `retired-locks-20261114`로 옮겼습니다. userdata와 snapshot 데이터는 삭제하지 않았습니다. 같은 옵션으로 다시 시작한 로그가 위 두 번째 콜드 부팅 기록입니다. 잠금 복구는 실행 중인 emulator가 없는 경우에만 적용할 수 있습니다.

모드 On에서 앱을 강제 종료한 뒤 component-only `am start`로 열면 Pleos task가 빈 화면으로 남고 자동 탭이 전달되지 않는 경우도 관측했습니다. MAIN/LAUNCHER intent로 열고 task 전환을 기다린 뒤, UI 조회 때마다 오른쪽 앱 pane의 포커스를 확인하도록 `ensure_app`과 `nodes`를 수정했습니다. Home·dock 전환을 섞은 중간 시도는 다른 앱을 선택할 수 있어 최종 경로에서 제외했습니다. 첫 중단과 런처 복구 후 실제 비교 결과는 [재시작 기록](../evidence/restart-persistence/run.json)에 함께 남깁니다.

vendor XML·SELinux·앱 차량 특권·서명 APK·앱 데이터는 변경하지 않았습니다. [복구 상태](../evidence/dds-recovery/recovery.json), [서명 APK 시험](../evidence/release-smoke-verified/run.json), [전체 결과](testing.md)를 연결해 확인할 수 있습니다.

## 공식 문서와 이번 관측의 구분

[Pleos 환경 설정](https://document.pleos.ai/docs/connect/guide/getting-started/application-development/configure-pleos-connect-emulator)은 콜드 부팅을 안내하고, [차량 콘솔 안내](https://document.pleos.ai/docs/connect/guide/getting-started/application-development/use-vehicle-emulator)는 ADB 포트 연결을 설명합니다. 고정 IP와 위 준비 지연은 이번 설치 이미지·런타임에서 직접 확인한 사실입니다. 일반 실차가 이 PC 콘솔이나 IP 주소를 사용한다는 의미는 아닙니다.
