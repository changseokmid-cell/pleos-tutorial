"""Build the three-page Experio project brief from existing project media.

Requires reportlab, Pillow and pypdfium2. Uses Malgun Gothic on Windows;
override PLEOS_FONT / PLEOS_BOLD_FONT when building on another platform.
"""
from pathlib import Path
from xml.sax.saxutils import escape
import json
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from PIL import Image
import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/proposal-public.pdf'
QA = ROOT / '.local/experio-pdf-review'
QA.mkdir(parents=True, exist_ok=True)
REPO = 'https://github.com/changseokmid-cell/pleos-tutorial'
VIDEOS = REPO + '/releases/download/contest-five-feature-videos-20261115/'
RELEASE = REPO + '/releases/tag/contest-round1-verified-20261114'
pdfmetrics.registerFont(TTFont('KR', os.environ.get('PLEOS_FONT', 'C:/Windows/Fonts/malgun.ttf')))
pdfmetrics.registerFont(TTFont('KRB', os.environ.get('PLEOS_BOLD_FONT', 'C:/Windows/Fonts/malgunbd.ttf')))
W, H = A4
M = 44
CW = W - 2 * M
INK = '#202020'
GRAY = '#666666'
RULE = '#D6D2CD'
LINK = '#315775'
blocks = []
c = canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1, invariant=1)
c.setTitle('Experio(Agentic Tutorial) 작품 소개서')
c.setAuthor('오황')
c.setSubject('차량 기능을 필요한 순간에 체험하고 익히는 Pleos Connect 앱')
c.setCreator('오황 / Experio')

def para(text, x, top, width, size=10.5, leading=17, bold=False, color=INK, max_height=None):
    style = ParagraphStyle('p', fontName='KRB' if bold else 'KR', fontSize=size,
                           leading=leading, textColor=HexColor(color), wordWrap='CJK',
                           splitLongWords=False, allowWidows=0, allowOrphans=0)
    p = Paragraph(escape(text).replace('\n', '<br/>'), style)
    _, height = p.wrap(width, H)
    assert not max_height or height <= max_height, (text[:40], height, max_height)
    assert top + height < H - 42, (text[:40], top + height)
    p.drawOn(c, x, H - top - height)
    blocks.append({'page': c.getPageNumber(), 'text': text, 'x': x, 'top': top, 'width': width, 'height': height})
    return top + height

def img(path, x, top, width, url=None):
    with Image.open(ROOT/path) as im:
        height = width * im.height / im.width
    c.drawImage(str(ROOT/path), x, H-top-height, width=width, height=height, mask='auto')
    if url:
        c.linkURL(url, (x, H-top-height, x+width, H-top), relative=0, thickness=0)
    return top + height

def link(text, x, top, url, size=9):
    bottom = para(text, x, top, CW, size=size, leading=size+4, color=LINK)
    width = min(CW, pdfmetrics.stringWidth(text, 'KR', size))
    c.linkURL(url, (x, H-bottom, x+width, H-top), relative=0, thickness=0)

def footer(number):
    c.setStrokeColor(HexColor(RULE)); c.setLineWidth(0.5)
    c.line(M, 43, W-M, 43)
    c.setFont('KR', 8); c.setFillColor(HexColor(GRAY))
    c.drawString(M, 28, '오황  |  Experio(Agentic Tutorial)  |  2026.11.15')
    c.drawRightString(W-M, 28, f'{number} / 3')

def page_header(number, title, subtitle):
    para('EXPERIO  /  작품 소개', M, 36, CW, size=8.5, leading=12, color=GRAY)
    para(title, M, 62, CW, size=24, leading=32, bold=True)
    para(subtitle, M, 104, CW, size=9.5, leading=15, color=GRAY)

# 1. A concise project introduction, with a real frame from the team's film.
para('현대자동차그룹 차량용 앱 개발 공모전  ·  오황', M, 36, CW, size=9, leading=13, color=GRAY)
para('Experio', M, 67, CW, size=36, leading=45, bold=True)
para('(Agentic Tutorial)', M, 115, CW, size=17, leading=23)
para('차에 있는 기능을 필요한 순간에 직접 써 보고,\n다음에는 스스로 사용할 수 있도록 돕는 차량용 튜토리얼 앱입니다.',
     M, 157, CW, size=12, leading=19, max_height=40)
end = img('demos/thumbnails/sync-web-17e9fe22.jpg', M, 214, CW, VIDEOS+'01_SYNC_17e9fe22.mp4')
para('좌석별 독립 온도를 경험하는 장면. 팀 제작 고객 경험 영상에서 발췌했습니다.',
     M, end+7, CW, size=8, leading=12, color=GRAY)
para('기획 배경', M, 542, CW, size=13, leading=19, bold=True)
background = ('차를 고를 때는 편의 기능을 꼼꼼히 살펴보지만, 막상 차를 받은 뒤에는 익숙한 기능만 쓰기 쉽습니다. '
              '화면 속 메뉴를 찾아보고 긴 설명서를 읽어야 하기 때문입니다. SDV 전환으로 기능이 늘어나고 업데이트될수록, '
              '고객이 새 기능을 알고 익히는 과정도 함께 마련되어야 한다고 생각했습니다.')
para(background, M, 570, CW, size=10.3, leading=17, max_height=85)
para('튜토리얼 모드를 켜면', M, 660, CW, size=13, leading=19, bold=True)
experience = ('차량 상태와 탑승자가 전달한 요청을 바탕으로 필요한 기능을 제안합니다. 사용자가 수락하면 기능을 체험하거나 '
              '조작 방법을 안내받고, 무엇이 달라졌는지 배웁니다. 초기 대상은 Pleos 탑재 그랜저를 새로 이용하는 '
              '50~69세 중 디지털 조작과 기능 탐색에 어려움을 겪는 운전자입니다.')
para(experience, M, 688, CW, size=10.3, leading=17, max_height=85)
footer(1); c.showPage()

# 2. Five scenes in reading order. Each image is a working video link.
page_header(2, '다섯 가지 고객 경험', '장면을 누르면 전체 영상이 열립니다. 영상은 제품이 지향하는 경험을 보여 주는 연출입니다.')
features = [
    ('01', '좌석별 독립 온도', '좌석마다 온도를 다르게 맞출 수 있다는 걸 모릅니다.',
     'SYNC를 해제하고 운전석은 21°C, 동승석은 24°C로 맞추는 차이를 경험합니다. 다음에는 필요한 좌석의 온도만 바꾸는 방법을 떠올릴 수 있습니다.',
     'sync-web-17e9fe22.jpg', '01_SYNC_17e9fe22.mp4', '0:48'),
    ('02', 'SPREAD', '시원함을 유지하면서 몸에 닿는 바람을 피할 수 있다는 걸 모릅니다.',
     '얼굴에 닿는 바람이 불편할 때 공조 메뉴의 SPREAD를 안내합니다. 다음에는 온도를 높이거나 에어컨을 끄기 전에 바람 방향을 조절할 수 있습니다.',
     'spread-abd18197.jpg', '02_SPREAD_abd18197.mp4', '1:01'),
    ('03', '사운드 위치', '음량뿐 아니라 소리의 중심도 바꿀 수 있다는 걸 모릅니다.',
     '뒷자리에서 음악이 크게 들릴 때 소리의 중심을 앞쪽으로 옮겨 봅니다. 가운데로 되돌리는 방법까지 익혀 탑승자의 요구에 맞춰 조절할 수 있습니다.',
     'sound-9fc8ab12.jpg', '03_SOUND_9fc8ab12.mp4', '1:21'),
    ('04', '에르고 시트 스트레칭', '시트에 스트레칭 기능이 있다는 걸 모릅니다.',
     '장거리 운전 후 정차했을 때, 해당 기능이 장착된 차량의 버튼 위치와 모드 변경·종료 방법을 안내합니다. 다음 휴식 때는 직접 사용할 수 있도록 돕습니다.',
     'ergo-c248edc4.jpg', '04_ERGO_c248edc4.mp4', '2:01'),
    ('05', 'Gleo 복합 요청', '여러 기능을 한 문장으로 부탁할 수 있다는 걸 모릅니다.',
     '“헤이 글레오, 에어컨 끄고 라디오 켜줘”처럼 말하는 방법을 배웁니다. 다음에는 Gleo가 지원하는 요청을 한 문장으로 묶어 전달할 수 있습니다.',
     'gleo-9aca15d5.jpg', '05_GLEO_9aca15d5.mp4', '1:10'),
]
for i, (number, name, problem, body, thumb, video, duration) in enumerate(features):
    top = 146 + i * 125
    iw = 168
    tx = M + iw + 20
    tw = CW-iw-20
    img('demos/thumbnails/'+thumb, M, top, iw, VIDEOS+video)
    para(f'{number}  {name}', tx, top-2, tw, size=12, leading=17, bold=True, max_height=19)
    para(problem, tx, top+24, tw, size=10, leading=15, bold=True, max_height=31)
    para(body, tx, top+58, tw, size=9.5, leading=14, max_height=57)
    link('영상 보기  '+duration, M, top+98, VIDEOS+video, size=8)
footer(2); c.showPage()

# 3. Readable implementation status with the untouched emulator screenshot.
page_header(3, '현재 구현과 다음 개발', 'Pleos Connect 2.1.0 에뮬레이터에서 확인한 시제품을 기준으로 정리했습니다.')
end = img('evidence/release-smoke-verified/03-confirmed-21-24.png', M, 143, CW,
          REPO+'/releases/download/contest-round1-verified-20261114/Release_Emulator.mp4')
para('실제 실행 화면. 운전석 21°C 유지, 동승석 24°C 변경과 SYNC 해제 상태를 다시 조회했습니다.',
     M, end+7, CW, size=8, leading=12, color=GRAY)
col = (CW-28)/2
para('구현하고 확인한 내용', M, 466, col, size=12.5, leading=18, bold=True)
left = ('정차 및 차량 UX 허용 조건에서 SYNC 해제와 동승석 온도 설정을 실행하고, 명령 이후의 차량 상태를 다시 확인했습니다. '
        '앱 재실행·에뮬레이터 재부팅·강제 종료 후에도 이력과 설정이 유지되는지 시험했습니다.\n\n'
        '에르고·SPREAD·사운드 위치는 순정 조작 안내와 응답 기록을 구현했습니다. Gleo는 시험 요청의 수신과 결과 반환까지 확인했습니다.')
para(left, M, 495, col, size=10, leading=16, max_height=178)
rx = M+col+28
para('다음에 확인할 내용', rx, 466, col, size=12.5, leading=18, bold=True)
right = ('실제 발화로 STT와 Gleo를 시험하고, 음성 안내를 반복했을 때의 시간 초과와 다른 차량 음성의 간섭을 점검하겠습니다. '
         '이후 장시간 주행 후 정차 시 제안, 반복 안내 억제, 차종·옵션별 지원 범위를 확인하겠습니다.\n\n'
         '사용자 시험에서는 같은 상황에서 안내 없이 기능을 다시 쓰는지, 얼마나 걸리는지, 추가 도움이 필요한지 살펴보겠습니다.')
para(right, rx, 495, col, size=10, leading=16, max_height=178)
note = ('실행 시험의 수락·응답은 자동 입력입니다. 실제 사람의 STT·Gleo 음성 왕복, 주행 중 선제 안내와 학습 효과는 아직 검증하지 않았습니다. '
        '화면의 “내 차 사용 안내”는 시제품 개발 당시 명칭입니다.')
para(note, M, 683, CW, size=8.5, leading=13, color=GRAY, max_height=41)
link('프로젝트 소개·소스코드  github.com/changseokmid-cell/pleos-tutorial', M, 736, REPO, size=9)
link('설치 APK·실제 실행 녹화', M, 758, RELEASE, size=9)
link('기능별 구현표와 시험 기록', M+238, 758, REPO+'/blob/codex/contest-integrated/docs/testing.md', size=9)
footer(3); c.save()

doc = pdfium.PdfDocument(str(OUT))
assert len(doc) == 3
texts = []
for i in range(len(doc)):
    page = doc[i]
    tp = page.get_textpage()
    texts.append(tp.get_text_range())
    page.render(scale=1.6).to_pil().save(QA/f'page-{i+1}.png')
    tp.close(); page.close()
doc.close()
(QA/'text.txt').write_text('\n\n'.join(texts),encoding='utf-8')
(QA/'layout.json').write_text(json.dumps(blocks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':str(OUT),'pages':3,'textBlocks':len(blocks)},ensure_ascii=True))
