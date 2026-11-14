"""Render the public implementation brief. Requires reportlab and PyMuPDF.
Fonts may be overridden with PLEOS_FONT / PLEOS_BOLD_FONT on other systems.
"""
from pathlib import Path
import os
from xml.sax.saxutils import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor,white
from reportlab.lib.pagesizes import A4

ROOT=Path(__file__).resolve().parents[1]
pdfmetrics.registerFont(TTFont('KR',os.environ.get('PLEOS_FONT','C:/Windows/Fonts/malgun.ttf')))
pdfmetrics.registerFont(TTFont('KRB',os.environ.get('PLEOS_BOLD_FONT','C:/Windows/Fonts/malgunbd.ttf')))
ink=HexColor('#153039');teal=HexColor('#067B75');muted=HexColor('#54666B')
styles={
 'title':ParagraphStyle('title',fontName='KRB',fontSize=27,leading=37,textColor=ink,spaceAfter=15,wordWrap='CJK'),
 'sub':ParagraphStyle('sub',fontName='KRB',fontSize=15,leading=22,textColor=teal,spaceBefore=15,spaceAfter=8,wordWrap='CJK'),
 'body':ParagraphStyle('body',fontName='KR',fontSize=10.4,leading=17,textColor=ink,spaceAfter=10,wordWrap='CJK'),
 'small':ParagraphStyle('small',fontName='KR',fontSize=8.4,leading=13,textColor=muted,spaceAfter=8,wordWrap='CJK'),
 'cell':ParagraphStyle('cell',fontName='KR',fontSize=9,leading=14,textColor=ink,wordWrap='CJK'),
 'head':ParagraphStyle('head',fontName='KRB',fontSize=9,leading=14,textColor=white,wordWrap='CJK')}
story=[]
def p(text,kind='body'):return Paragraph(escape(text),styles[kind])
def add(text,kind='body'):story.append(p(text,kind))
def table(rows,widths):
    data=[[p(t,'head' if i==0 else 'cell') for t in row] for i,row in enumerate(rows)]
    t=Table(data,colWidths=widths,hAlign='LEFT',repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),teal),('ROWBACKGROUNDS',(0,1),(-1,-1),[HexColor('#EDF5F4'),white]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9)]))
    story.append(t);story.append(Spacer(1,9))
def footer(canvas,doc):
    canvas.setStrokeColor(HexColor('#B6CBCB'));canvas.line(42,47,A4[0]-42,47)
    canvas.setFont('KR',8);canvas.setFillColor(muted)
    canvas.drawString(42,32,'PLEOS CONNECT  |  2026.11.14  |  구현 증거 기준 공개 초안')
    canvas.drawRightString(A4[0]-42,32,str(doc.page))

add('몰랐던 기능을,\n필요한 순간에.','title')
add('내 차 사용 안내 · Pleos Connect 차량용 앱','sub')
add('새 차량의 기능을 찾아 읽는 대신, 자신의 불편과 연결해 짧게 체험하고 다음에 스스로 사용하도록 돕습니다. 초기 검증 대상은 Pleos 탑재 그랜저를 새로 이용하는 50~69세 운전자입니다. 연령별 미인지율과 학습 효과는 검증할 가설입니다.')
add('차량 안에서 이어지는 학습','sub')
add('사용자가 튜토리얼 모드를 켭니다. 차량 상태와 직접 전달한 요청을 연결해 기능을 제안합니다. 수락 후 가능한 제어 또는 순정 조작 방법을 안내하고, 차량 결과와 사용자의 체감을 따로 기록합니다.')
table([['순서','앱이 제공하는 것'],['발견','불편을 기능의 가치와 연결: 좌석별 온도, 휴식, 소리 위치, 직풍, 복합 요청'],['체험','실제 지원성이 확인된 명령 또는 장착 사양에 맞는 순정 버튼·메뉴 안내'],['확인','명령 전송과 실제 차량 변화, 사용자 체감 응답을 구분'],['다음 사용','다시 사용해 본 경험을 로컬 이력에 기록. 학습 효과는 후속 사용자 검증']], [82,429])
add('이번 제출판의 범위','sub')
add('다섯 체험을 하나의 Android 앱에 통합했습니다. 상세 체험과 자동 공조 명령은 P 및 차량 UX 허용 상태에서 제공합니다. 주행 중 선제 음성 안내와 실제 Gleo 자연어 연동은 후속 검증 대상입니다.')
add('이 문서는 개인정보가 없는 작품 소개·구현표입니다. 공식 참가 신청서, 동의서와 서명을 대체하지 않습니다. 고객 경험 영상은 연출이며 실제 앱 실행 증거와 구분합니다.','small')
story.append(PageBreak())
add('다섯 체험, 확인된 범위','title')
table([['체험','구현 및 실제 확인','미지원·미검증 경계'],
['SYNC','실제 SDK로 연동 해제 후 동승석 목표온도 설정. 21/21°C → 21/24°C, 운전석 21°C 유지 재조회.','수락은 자동 시험 입력. 실차·실제 사람 음성 수락·주행 중 제어 성공을 뜻하지 않음.'],
['에르고','장착 사양에 맞는 버튼 안내. 전신 → 허리 → 골반 → 꺼짐. 체감·다음 사용 응답 기록.','전용 스트레칭 제어 없음. trip 시간 SDK 미지원. 앱 관측 2시간 제안의 실시간 경과 시험 미완료.'],
['사운드','위치 조절 안내 → 가운데 복원 응답 → 같은 곡·음량에서 별도 음장 비교.','CarAudioManager 획득과 제어 권한은 다름. 오디오 제어 권한 미부여, 앞뒤 스피커 직접 제어 없음.'],
['SPREAD','직풍 불편을 더위와 구분. 순정 SPREAD 메뉴 안내 후 좌우 목표온도 유지 관측.','SPREAD 전용 제어·모드 신호 미확인. 온도 유지가 벤트 작동 성공을 뜻하지 않음.'],
['Gleo','3개 App Schema action, 입력 검증, success/asking/fail callback, 마이크 양보와 복합 요청 안내.','ADB 수신부 시험. 실제 Gleo 자연어 왕복 및 A/C+라디오 복합 성공 미검증.']], [65,231,215])
add('증거를 남기는 방식','sub')
add('값·영역·단위·시각·출처·지원성·오류를 함께 기록합니다. 미지원 값을 false나 0으로 만들지 않습니다. ACK는 명령 접수이며 완료가 아닙니다. 별도 재조회와 ACTION_RESULT로 결과를 판단합니다.')
add('LIVE_SDK / MOCK_EVENT / UNVERIFIED_INTENT / TEST_PCM / USER_REPORT를 구분합니다. 자동 UI의 체감 버튼도 사용자 연구 결과로 해석하지 않습니다. 에르고·음장·SPREAD를 다른 제어로 흉내 내지 않습니다.','small')
story.append(PageBreak())
add('검증 결과와 다음 단계','title')
table([['시험','결과'],['빌드·기본 안전 조건','서명 release 빌드 및 lintVital 통과. 단위 시험 9개 통과.'],['실제 차량 SDK','SYNC 연동 해제와 동승석 24°C 설정 후 운전석 유지·동승석 온도 재조회 확인.'],['재시작·이력','서명 APK에서 앱 재실행·AVD 콜드 부팅·모드 On 강제 종료 후 기본 Off, 표시 이력과 다섯 설정 유지 확인.'],['예외·백그라운드','빈 동승석 차단, 중복 억제, 거절·D 전환 취소, Home 뒤 90초 만료와 SDK 변화 수신 확인.'],['Gleo 수신부','앱이 열린 상태에서 action 성공·질문·실패 callback 확인. 백그라운드 ADB 모드 시작은 OS가 거부.'],['공식 음성','ko-KR TTS 완료 관측과 반복 시간 초과를 모두 보존. 실제 사람 STT와 합성 PCM 최종 인식 성공 없음.']], [105,406])
add('1차: 재현 가능한 구현과 정직한 증거','sub')
add('단일 앱 소스, 서명 APK, 실행 로그·스크린샷, 실구동 녹화, 고객 경험 영상 목록과 파일 해시를 연결합니다. APK 녹화의 UI 입력은 자동화되었으며 사용자 만족이나 학습 개선을 입증하지 않습니다.')
add('2차: 실제 발화, 실차, 재사용 검증','sub')
add('실제 마이크와 Gleo 자연어 왕복, 정상 자원 조건의 음성 지연, 전화·미디어와의 focus 충돌, 장시간 주행 후 제안, 실차 사양별 권한·메뉴를 확인합니다. 목표 고객이 기능을 발견하고 다음에 스스로 재사용하는지 관찰합니다.')
add('기술 기준과 참고','sub')
add('kr.pleosguide 1.0.0 · Pleos Connect 2.1.0 / Android 14 API 34 · Vehicle 2.3.2 · SpeechToText/TextToSpeech 3.3.1 ON_DEVICE · targetSdk 33','small')
for title,url in [('Pleos SDK','https://document.pleos.ai/'),('그랜저 시트','https://ownersmanual.hyundai.com/full_webhelp/gn7/2027/ko_kr/safety-adj_front_seats-power_adjust.html'),('그랜저 공조','https://ownersmanual.hyundai.com/full_webhelp/gn7/2027/ko_kr/convenience-auto_climate_ctrl-ctrl_in_manual_mode.html'),('사운드','https://ownersmanual.hyundai.com/ivi/Connect-S/AVNT/KOR/Korean/009_Vehiclesettings_12.html')]:
    story.append(Paragraph(f'<link href="{url}" color="#067B75">{escape(title)}: {escape(url)}</link>',styles['small']))
add('심사 읽기: docs/reviewer-guide.md · 코드 구조: docs/architecture.md · 재현·제한: docs/testing.md · 구현표: docs/implementation.md · 제출 버전 해시: submission-manifest.json','small')
out=ROOT/'docs/proposal-public.pdf'
SimpleDocTemplate(str(out),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=42,bottomMargin=64,title='내 차 사용 안내 - 구현 근거와 개발 계획',author='Pleos Tutorial').build(story,onFirstPage=footer,onLaterPages=footer)
import fitz
doc=fitz.open(out);preview=ROOT/'.local/pdf-review';preview.mkdir(parents=True,exist_ok=True)
for i,page in enumerate(doc):page.get_pixmap(matrix=fitz.Matrix(1.4,1.4)).save(preview/f'page-{i+1}.png')
assert len(doc)==3,f'Unexpected overflow: {len(doc)} pages'
print(f'{len(doc)} pages rendered: {out}')
