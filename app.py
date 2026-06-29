import sys, os, io, html as html_lib, threading, webbrowser, json, urllib.parse, base64, re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# .env 파일 자동 로드
_env_path = Path(__file__).parent / '.env'
if _env_path.exists():
    for _line in _env_path.read_text(encoding='utf-8').splitlines():
        _line = _line.strip()
        if _line and not _line.startswith('#') and '=' in _line:
            _k, _v = _line.split('=', 1)
            os.environ.setdefault(_k.strip(), _v.strip())

try:
    from flask import Flask, request, send_file, send_from_directory, Response
except ImportError:
    os.system(f'{sys.executable} -m pip install flask')
    from flask import Flask, request, send_file, send_from_directory, Response

BASE_DIR = Path(__file__).parent
PORT = int(os.environ.get('PORT', 5000))

app = Flask(__name__)

VERSIONS = {
    'A': {'name': 'Pure Cream',       'bg': '#faf6ef', 'surface': '#f0ebe0', 'point': '#8b7355', 'text': '#2c2417', 'caption': '#9b8e7a', 'font': 'GangwonEdu'},
    'B': {'name': 'Cloud White',      'bg': '#f8f8f6', 'surface': '#eeede8', 'point': '#6b7c8a', 'text': '#1e2328', 'caption': '#8a9099', 'font': 'GangwonEdu'},
    'C': {'name': 'Rice Paper',       'bg': '#f2ece0', 'surface': '#e8dfc8', 'point': '#7a6a4f', 'text': '#2a1f0e', 'caption': '#9a8a72', 'font': 'Kkomi'},
    'D': {'name': 'Deep Navy Gold',   'bg': '#0e1624', 'surface': '#182436', 'point': '#c8a96e', 'text': '#f5f0e8', 'caption': '#786e62', 'font': 'GangwonEdu'},
    'E': {'name': 'Deep Navy Silver', 'bg': '#0e1624', 'surface': '#182436', 'point': '#c0c8d4', 'text': '#f5f8fc', 'caption': '#786e62', 'font': 'GangwonEdu'},
}

def _is_light_bg(hex_color):
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.5

TEXTURES = {
    'none':   {'label': '없음',      'freq': None,        'oct': 0, 'opacity': 0,    'opacity_light': 0   },
    'smooth': {'label': '부드러운',  'freq': '1.5',       'oct': 4, 'opacity': 0.12, 'opacity_light': 0.25},
    'paper':  {'label': '종이',      'freq': '0.85',      'oct': 4, 'opacity': 0.20, 'opacity_light': 0.42},
    'rough':  {'label': '거친 종이', 'freq': '0.55',      'oct': 3, 'opacity': 0.32, 'opacity_light': 0.58},
    'hanji':  {'label': '한지',      'freq': '0.3 0.8',  'oct': 5, 'opacity': 0.24, 'opacity_light': 0.48},
    'linen':  {'label': '린넨',      'freq': '0.65 0.3', 'oct': 2, 'opacity': 0.26, 'opacity_light': 0.50},
}


FONTS_URL_HTTP = f'http://localhost:{PORT}/fonts'
FONTS_URL_FILE = 'file:///' + str(BASE_DIR / 'fonts').replace('\\', '/')

# ── 이모지 아이콘 ─────────────────────────────────────────────
ICON_SVGS = {
    'none':    {'label': '없음',   'emoji': ''},
    'rainbow': {'label': '무지개', 'emoji': '🌈'},
    'moon':    {'label': '달·별',  'emoji': '🌙'},
    'flower':  {'label': '꽃',     'emoji': '🌸'},
    'sprout':  {'label': '새싹',   'emoji': '🌱'},
    'cloud':   {'label': '구름',   'emoji': '☁️'},
    'wave':    {'label': '파도',   'emoji': '🌊'},
    'star':    {'label': '별',     'emoji': '⭐'},
    'heart':   {'label': '마음',   'emoji': '🩷'},
    'coffee':  {'label': '커피',   'emoji': '☕'},
    'leaf':    {'label': '잎',     'emoji': '🍃'},
    'bird':    {'label': '새',     'emoji': '🐦'},
    'sun':     {'label': '해',     'emoji': '☀️'},
}


def build_card_html(lines, tag, handle, version, font_override=None,
                    font_size=60, tag_font_size=22, icon='', texture='paper', font_base=None,
                    bg_image='', bg_mode='overlay', bg_opacity=0.35):
    v   = VERSIONS.get(version, VERSIONS['E'])
    tx  = TEXTURES.get(texture, TEXTURES['paper'])
    font = font_override or v['font']
    font_size     = int(font_size or 60)
    tag_font_size = int(tag_font_size or 22)
    bg_opacity    = float(bg_opacity or 0.35)
    body      = '<br>\n      '.join(html_lib.escape(ln) for ln in lines)
    fb        = font_base or FONTS_URL_HTTP
    icon_emoji = ICON_SVGS.get(icon or 'none', {}).get('emoji', '')
    icon_html  = f'<div class="card-icon">{icon_emoji}</div>' if icon_emoji else ''

    # 배경 이미지 CSS
    bg_css = ''
    bg_overlay_div = ''
    if bg_image:
        if bg_mode == 'background':
            bg_css = f"""
    .card {{
      background-image: url("{bg_image}");
      background-size: cover; background-position: center;
    }}"""
        else:  # overlay
            bg_css = f"""
    .card-bg-image {{
      position: absolute; inset: 0;
      background-image: url("{bg_image}");
      background-size: cover; background-position: center;
      opacity: {bg_opacity}; z-index: 1; pointer-events: none;
    }}"""
            bg_overlay_div = '<div class="card-bg-image"></div>'

    # 텍스처는 프론트엔드 Canvas로 처리 (data-texture 속성 전달)
    noise_html = ''
    tex_attr = f' data-texture="{texture}"' if texture and texture != 'none' else ''

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <style>
    @font-face {{ font-family: 'GangwonEdu';   src: url('{fb}/GangwonEduSaeum-fixed.ttf') format('truetype'); }}
    @font-face {{ font-family: 'Kkomi';         src: url('{fb}/KNPSKkomi-fixed.otf')       format('opentype'); }}
    @font-face {{ font-family: 'SUIT';          src: url('{fb}/SUIT-Light.ttf')             format('truetype'); font-weight: 300; }}
    @font-face {{ font-family: 'YeongdeokSea'; src: url('{fb}/Yeongdeok%20Sea.ttf')        format('truetype'); }}
    @font-face {{ font-family: 'PaperlogyL';   src: url('{fb}/Paperlogy-3Light.ttf')       format('truetype'); }}
    @font-face {{ font-family: 'Paperlogy';    src: url('{fb}/Paperlogy-4Regular.ttf')     format('truetype'); }}
    @font-face {{ font-family: 'PaperlogyB';   src: url('{fb}/Paperlogy-7Bold.ttf')        format('truetype'); }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html, body {{ width: 1080px; height: 1350px; overflow: hidden; }}
    .card {{
      position: relative; width: 1080px; height: 1350px;
      background: {v['bg']}; border: 0.5px solid {v['surface']};
      border-radius: 14px; overflow: hidden;
    }}{bg_css}
    .card-tag {{
      position: absolute; top: 70px; left: 0; right: 0; text-align: center;
      font-family: 'SUIT', sans-serif; font-weight: 300;
      font-size: {tag_font_size}px; letter-spacing: 0.14em; line-height: 1.4;
      color: {v['point']}; z-index: 3;
    }}
    .card-content {{
      position: absolute; top: 50%; transform: translateY(-50%);
      left: 0; right: 0; text-align: center; z-index: 3; padding: 0 72px;
    }}
    .card-icon {{
      font-size: 96px; line-height: 1; margin-bottom: 36px;
      display: block;
    }}
    .card-body {{
      font-family: '{font}', sans-serif; font-size: {font_size}px; line-height: 2.0;
      color: {v['text']}; word-break: keep-all;
    }}
    .card-handle {{
      position: absolute; bottom: 70px; left: 0; right: 0; text-align: center;
      font-family: 'SUIT', sans-serif; font-weight: 300;
      font-size: 24px; letter-spacing: 0.10em; line-height: 1.4;
      color: {v['caption']}; z-index: 3;
    }}
  </style>
</head>
<body>
<div class="card"{tex_attr}>
  {bg_overlay_div}
  <canvas id="tx-canvas" style="position:absolute;top:0;left:0;z-index:2;pointer-events:none;opacity:0"></canvas>
  <span class="card-tag">{html_lib.escape(tag)}</span>
  <div class="card-content">
    {icon_html}
    <div class="card-body">{body}</div>
  </div>
  <span class="card-handle">{html_lib.escape(handle)}</span>
</div>
<script>
(function(){{
  var card = document.querySelector('.card');
  var tex  = card && card.dataset.texture;
  if (!tex) return;
  var W = 1080, H = 1350;
  var cv = document.getElementById('tx-canvas');
  cv.width = W; cv.height = H;
  var ctx = cv.getContext('2d');
  var light = {str(_is_light_bg(v['bg'])).lower()};
  var cfg = {{
    smooth:     {{grain:1, scale:2,  alpha: light?0.18:0.10}},
    paper:      {{grain:1, scale:4,  alpha: light?0.28:0.16}},
    rough:      {{grain:2, scale:8,  alpha: light?0.38:0.22}},
    hanji:      {{grain:1, scale:3,  alpha: light?0.22:0.14, horiz:true}},
    linen:      {{grain:1, scale:3,  alpha: light?0.26:0.16, grid:true}},
  }}[tex];
  if (!cfg) return;
  // 작은 캔버스에 노이즈 생성 후 스케일업 (종이질감 효과)
  var sw = Math.ceil(W / cfg.scale), sh = Math.ceil(H / cfg.scale);
  var tmp = document.createElement('canvas');
  tmp.width = sw; tmp.height = sh;
  var tc = tmp.getContext('2d');
  var id = tc.createImageData(sw, sh);
  var d = id.data;
  var color = light ? 0 : 255;
  for (var i=0; i<d.length; i+=4) {{
    var r = Math.random();
    // hanji: 수평 방향 강조
    if (cfg.horiz) {{ var row=(i/4/sw)|0; r = r*0.4 + (Math.sin(row*0.8)*0.5+0.5)*0.6; }}
    // linen: 격자 방향
    if (cfg.grid) {{ var px=((i/4)%sw)|0; var py=(i/4/sw)|0; r = r*0.3+(Math.sin(px*1.2)*0.5+0.5)*0.35+(Math.sin(py*1.2)*0.5+0.5)*0.35; }}
    d[i]=color; d[i+1]=color; d[i+2]=color;
    d[i+3]=Math.floor(r * cfg.alpha * 255 * (cfg.grain>1?(0.5+Math.random()*0.5):1));
  }}
  tc.putImageData(id, 0, 0);
  ctx.imageSmoothingEnabled = (cfg.scale > 2);
  ctx.imageSmoothingQuality = 'low';
  ctx.drawImage(tmp, 0, 0, W, H);
  cv.style.opacity = '1';
}})();
</script>
</body>
</html>"""


@app.after_request
def cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/')
def index():
    return send_from_directory(str(BASE_DIR / 'web'), 'index.html')


@app.route('/fonts/<path:filename>')
def fonts(filename):
    return send_from_directory(str(BASE_DIR / 'fonts'), filename)


@app.route('/api/versions')
def api_versions():
    return Response(json.dumps(VERSIONS), mimetype='application/json')

@app.route('/api/icons')
def api_icons():
    return Response(
        json.dumps({k: {'label': v['label'], 'emoji': v.get('emoji', '')} for k, v in ICON_SVGS.items()}, ensure_ascii=False),
        mimetype='application/json',
    )

@app.route('/api/textures')
def api_textures():
    return Response(
        json.dumps({k: {'label': v['label']} for k, v in TEXTURES.items()}),
        mimetype='application/json',
    )

@app.route('/api/card', methods=['POST'])
def api_card():
    d = request.json
    html = build_card_html(
        lines=d.get('lines', ['']),
        tag=d.get('tag', '— 오늘의 마음 —'),
        handle=d.get('handle', '— @mind.teum —'),
        version=d.get('version', 'E'),
        font_override=d.get('font'),
        font_size=d.get('fontSize', 60),
        tag_font_size=d.get('tagFontSize', 22),
        icon=d.get('icon', ''),
        texture=d.get('texture', 'paper'),
        bg_image=d.get('bgImage', ''),
        bg_mode=d.get('bgMode', 'overlay'),
        bg_opacity=d.get('bgOpacity', 0.35),
    )
    return Response(html, mimetype='text/html; charset=utf-8')


GENERATE_SYSTEM = """당신은 @mind.teum 인스타그램 카드뉴스 작가이자 SNS 캡션 전문가입니다.
Mind.teum은 감정·관계·자존·성장을 다루는 브랜드로, 짧고 진한 글귀를 전달합니다.

카드뉴스 글쓰기 원칙:
- 담담하고 따뜻한 톤, 설명보다 감정을 건드리는 문장
- 한 슬라이드당 3~6줄, 각 줄은 10자 이내 권장
- 빈 줄("")을 활용해 시각적 여백 표현 가능
- 마지막 슬라이드는 여운을 남기는 마무리

출력 형식 (순수 JSON 객체, 설명 없이):
{
  "slides": [
    {"tag": "— 태그 —", "icon": "heart", "lines": ["줄1", "줄2", "줄3"]},
    {"tag": "— 태그 —", "icon": "none",  "lines": ["줄1", "", "줄3"]},
    ...
  ],
  "caption": "인스타그램 캡션 텍스트",
  "poll": {
    "question": "독자 질문?",
    "choices": ["① 선택지1", "② 선택지2", "③ 선택지3"]
  },
  "keywords": ["#키워드1", "#키워드2", "#키워드3"]
}

규칙:
- slides: 요청 개수만큼 정확히 생성
  - tag: "— 주제 —" 형식
  - icon: rainbow/moon/flower/sprout/cloud/wave/star/heart/coffee/leaf/bird/sun/none 중 하나
  - lines: 카드 본문 줄 배열 (빈 줄은 "" 사용)
- caption: 카드 내용을 요약·정리하지 말 것. 독자가 자신의 이야기처럼 느낄 수 있는 공감형 문장으로 작성. 이모지 1~3개 포함. 400자 이내.
- poll: 독자가 자신의 감정·경험을 돌아볼 수 있는 질문으로 마무리. 3가지 선택지는 서로 다른 감정/상황을 대변.
- keywords: 관련 해시태그 5~8개
- JSON만 출력, 마크다운 코드블록 없이"""


def fetch_url_text(url):
    """Playwright로 URL의 텍스트 내용을 가져온다."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'
        )
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=20000)
            page.wait_for_timeout(2000)
            # 주요 텍스트 영역 우선 추출
            for selector in ['article', 'main', '[role="main"]', 'body']:
                try:
                    el = page.query_selector(selector)
                    if el:
                        text = el.inner_text()
                        if len(text.strip()) > 50:
                            return text[:4000]
                except Exception:
                    continue
            return page.inner_text('body')[:4000]
        finally:
            browser.close()


@app.route('/api/generate', methods=['POST'])
def api_generate():
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return Response(
            json.dumps({'error': 'ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.'}),
            status=400, mimetype='application/json'
        )

    import anthropic
    d = request.json
    topic = d.get('topic', '').strip()
    count = max(1, min(20, int(d.get('count', 6))))
    if not topic:
        return Response(json.dumps({'error': '주제를 입력해주세요.'}), status=400, mimetype='application/json')

    # URL이면 페이지 내용 스크래핑
    is_url = topic.startswith('http://') or topic.startswith('https://')
    if is_url:
        try:
            page_text = fetch_url_text(topic)
            user_message = (
                f"다음은 참고할 인터넷 페이지의 내용입니다:\n\n{page_text}\n\n"
                f"위 내용을 Mind.teum 스타일로 재해석해서 카드뉴스 {count}장을 생성해주세요. "
                f"원문을 직역하지 말고, 감정적 여운이 있는 짧은 문장으로 재창작해주세요."
            )
        except Exception as e:
            user_message = (
                f"URL: {topic}\n\n"
                f"(페이지를 직접 가져오지 못했습니다: {e})\n"
                f"URL의 주제를 추측해서 카드뉴스 {count}장을 생성해주세요."
            )
    else:
        user_message = f'주제: {topic}\n\n위 주제로 카드뉴스 {count}장을 생성해주세요.'

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=4000,
        system=GENERATE_SYSTEM,
        messages=[{'role': 'user', 'content': user_message}],
    )

    raw = msg.content[0].text.strip()
    if raw.startswith('```'):
        raw = raw.split('\n', 1)[1]
        raw = raw.rsplit('```', 1)[0].strip()

    result = json.loads(raw)
    # 이전 형식(배열)과 신규 형식(객체) 모두 처리
    if isinstance(result, list):
        result = {'slides': result, 'caption': '', 'poll': {}, 'keywords': []}
    return Response(json.dumps(result, ensure_ascii=False), mimetype='application/json')


CAPTION_SYSTEM = """당신은 @mind.teum 인스타그램 캡션 전문가입니다.
Mind.teum은 감정·관계·자존·성장을 다루는 브랜드입니다.

카드뉴스 내용을 바탕으로 아래 세 가지를 새롭게 작성하세요.

출력 형식 (순수 JSON, 설명 없이):
{
  "caption": "인스타그램 캡션 텍스트",
  "poll": {
    "question": "독자 질문?",
    "choices": ["① 선택지1", "② 선택지2", "③ 선택지3"]
  },
  "keywords": ["#키워드1", "#키워드2", "#키워드3"]
}

규칙:
- caption: 카드 내용을 요약·정리하지 말 것. 독자가 자신의 이야기처럼 느낄 수 있는 공감형 문장. 이모지 1~3개 포함. 400자 이내.
- poll: 독자가 자신의 감정·경험을 돌아볼 수 있는 질문. 3가지 선택지는 서로 다른 감정/상황을 대변.
- keywords: 관련 해시태그 5~8개
- JSON만 출력, 마크다운 코드블록 없이"""


@app.route('/api/caption', methods=['POST'])
def api_caption():
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return Response(json.dumps({'error': 'ANTHROPIC_API_KEY 없음'}), status=400, mimetype='application/json')

    import anthropic, traceback
    try:
        d = request.json or {}
        slides = d.get('slides', [])
        slides_text = '\n'.join(
            f"[슬라이드 {i+1}] {s.get('tag','')} / {' / '.join(s.get('lines', []))}"
            for i, s in enumerate(slides)
        )
        user_message = f"다음 카드뉴스 내용을 바탕으로 캡션·설문·키워드를 새로 작성해주세요.\n\n{slides_text}"

        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=1500,
            system=CAPTION_SYSTEM,
            messages=[{'role': 'user', 'content': user_message}],
        )
        raw = msg.content[0].text.strip()
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[1]
            raw = raw.rsplit('```', 1)[0].strip()
        return Response(json.dumps(json.loads(raw), ensure_ascii=False), mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({'error': str(e), 'trace': traceback.format_exc()[-400:]}, ensure_ascii=False),
                        status=500, mimetype='application/json')


def _playwright_screenshot(file_url):
    """새 스레드에서 asyncio 루프를 직접 생성해 Playwright 실행 (Flask 스레드 충돌 우회)."""
    import asyncio, threading, traceback
    out = {}

    def _run():
        try:
            asyncio.set_event_loop(asyncio.new_event_loop())
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 1080, 'height': 1350})
                page.goto(file_url, wait_until='networkidle')
                page.wait_for_timeout(500)
                out['png'] = page.screenshot(clip={'x': 0, 'y': 0, 'width': 1080, 'height': 1350})
                browser.close()
        except Exception:
            out['error'] = traceback.format_exc()

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout=30)

    if 'error' in out:
        print(out['error'])
        raise RuntimeError(out['error'])
    if 'png' not in out:
        raise RuntimeError('Playwright 타임아웃 (30초 초과)')
    return out['png']


@app.route('/api/export', methods=['POST'])
def api_export():
    import tempfile, traceback
    tmp = None
    try:
        d = request.json or {}
        html = build_card_html(
            lines=d.get('lines', ['']),
            tag=d.get('tag', '— 오늘의 마음 —'),
            handle=d.get('handle', '— @mind.teum —'),
            version=d.get('version', 'E'),
            font_override=d.get('font'),
            font_size=d.get('fontSize', 60),
            tag_font_size=d.get('tagFontSize', 22),
            icon=d.get('icon', ''),
            texture=d.get('texture', 'paper'),
            font_base=FONTS_URL_FILE,
            bg_image=d.get('bgImage', ''),
            bg_mode=d.get('bgMode', 'overlay'),
            bg_opacity=d.get('bgOpacity', 0.35),
        )

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False,
                                         mode='w', encoding='utf-8') as f:
            f.write(html)
            tmp = f.name

        file_url = 'file:///' + tmp.replace('\\', '/')
        png = _playwright_screenshot(file_url)

        filename = d.get('filename', f'card-{d.get("version", "E").lower()}.png')
        return send_file(
            io.BytesIO(png), mimetype='image/png',
            as_attachment=True, download_name=filename,
        )

    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        return Response(
            json.dumps({'error': str(e), 'trace': tb[-600:]}, ensure_ascii=False),
            status=500, mimetype='application/json',
        )
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


_FONT_FILES = {
    'GangwonEdu':  'GangwonEduSaeum-fixed.ttf',
    'Kkomi':       'KNPSKkomi-fixed.otf',
    'YeongdeokSea':'Yeongdeok Sea.ttf',
    'PaperlogyL':  'Paperlogy-3Light.ttf',
    'Paperlogy':   'Paperlogy-4Regular.ttf',
    'PaperlogyB':  'Paperlogy-7Bold.ttf',
    'SUIT':        'SUIT-Light.ttf',
}
_FONT_MIMES = {
    'ttf': 'font/truetype',
    'otf': 'font/opentype',
}
_FONT_FORMATS = {
    'ttf': 'truetype',
    'otf': 'opentype',
}


def _embed_font_css(family):
    fname = _FONT_FILES.get(family)
    if not fname:
        return ''
    path = BASE_DIR / 'fonts' / fname
    if not path.exists():
        return ''
    ext = fname.rsplit('.', 1)[-1].lower()
    data = base64.b64encode(path.read_bytes()).decode('ascii')
    mime = _FONT_MIMES.get(ext, 'font/truetype')
    fmt = _FONT_FORMATS.get(ext, 'truetype')
    return f"@font-face{{font-family:'{family}';src:url('data:{mime};base64,{data}') format('{fmt}');}}\n"


def build_card_svg(lines, tag, handle, version, font_override=None,
                   font_size=60, tag_font_size=22, icon='none', texture='paper'):
    v = VERSIONS.get(version, VERSIONS['E'])
    tx = TEXTURES.get(texture or 'paper', TEXTURES['paper'])
    font = font_override or v['font']
    font_size = int(font_size or 60)
    tag_font_size = int(tag_font_size or 22)

    W, H = 1080, 1350
    LINE_H = font_size * 2.0  # matches CSS line-height: 2.0

    # ── 폰트 임베드 ─────────────────────────────────────────────
    embedded_css = _embed_font_css('SUIT') + _embed_font_css(font)

    # ── 노이즈 텍스처 필터 ───────────────────────────────────────
    noise_filter = noise_rect = ''
    if tx.get('url'):
        freq_raw = '0.85'  # 기본값; 텍스처별 baseFrequency 매핑
        freq_map = {'smooth': '1.5', 'paper': '0.85', 'rough': '0.55',
                    'hanji': '0.3 0.8', 'linen': '0.65 0.3'}
        oct_map  = {'smooth': 4,     'paper': 4,      'rough': 3,
                    'hanji': 5,      'linen': 2}
        freq_raw = freq_map.get(texture, '0.85')
        oct_n    = oct_map.get(texture, 4)
        noise_filter = (
            f'<filter id="tex" x="0%" y="0%" width="100%" height="100%" color-interpolation-filters="sRGB">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{freq_raw}" numOctaves="{oct_n}" stitchTiles="stitch" result="n"/>'
            f'<feColorMatrix type="saturate" values="0" in="n" result="gray"/>'
            f'<feComposite in="SourceGraphic" in2="gray" operator="over"/>'
            f'</filter>'
        )
        noise_rect = (
            f'<rect width="{W}" height="{H}" fill="white" '
            f'opacity="{tx["opacity"]}" filter="url(#tex)" '
            f'style="mix-blend-mode:overlay;pointer-events:none"/>'
        )

    # ── 아이콘 배치 ──────────────────────────────────────────────
    icon_emoji = ICON_SVGS.get(icon or 'none', ICON_SVGS['none']).get('emoji', '')
    ICON_FONT_SIZE = 100
    ICON_MARGIN_B  = 40
    icon_block_h   = (ICON_FONT_SIZE + ICON_MARGIN_B) if icon_emoji else 0

    # ── 텍스트 세로 배치 계산 ────────────────────────────────────
    body_h = len(lines) * LINE_H
    total_content_h = icon_block_h + body_h
    content_start_y = H / 2 - total_content_h / 2

    icon_element = ''
    if icon_emoji:
        icon_y = content_start_y + ICON_FONT_SIZE * 0.85
        icon_element = (
            f'<text x="{W//2}" y="{icon_y:.1f}" text-anchor="middle" '
            f'font-size="{ICON_FONT_SIZE}">{icon_emoji}</text>'
        )

    # 본문 tspan
    body_start_y = content_start_y + icon_block_h + font_size * 0.75
    body_tspans = ''
    for i, line in enumerate(lines):
        y = body_start_y + i * LINE_H
        body_tspans += f'<tspan x="{W//2}" y="{y:.1f}">{html_lib.escape(line)}</tspan>'

    # 태그 & 핸들 Y
    tag_y = 70 + tag_font_size
    handle_y = H - 70

    svg = f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}"
  xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
<defs>
<style>
{embedded_css}
</style>
{noise_filter}
</defs>

<!-- 배경 -->
<rect width="{W}" height="{H}" fill="{v['bg']}" rx="14"/>

<!-- 텍스처 -->
{noise_rect}

<!-- 아이콘 -->
{icon_element}

<!-- 태그 -->
<text x="{W//2}" y="{tag_y}"
  text-anchor="middle" dominant-baseline="auto"
  font-family="SUIT, sans-serif" font-weight="300"
  font-size="{tag_font_size}" letter-spacing="3"
  fill="{v['point']}">{html_lib.escape(tag)}</text>

<!-- 본문 -->
<text text-anchor="middle"
  font-family="{font}, sans-serif"
  font-size="{font_size}"
  fill="{v['text']}">{body_tspans}</text>

<!-- 핸들 -->
<text x="{W//2}" y="{handle_y}"
  text-anchor="middle" dominant-baseline="auto"
  font-family="SUIT, sans-serif" font-weight="300"
  font-size="24" letter-spacing="2.5"
  fill="{v['caption']}">{html_lib.escape(handle)}</text>

</svg>'''
    return svg


@app.route('/api/export-svg', methods=['POST'])
def api_export_svg():
    import traceback
    try:
        d = request.json or {}
        svg = build_card_svg(
            lines=d.get('lines', ['']),
            tag=d.get('tag', '— 오늘의 마음 —'),
            handle=d.get('handle', '— @mind.teum —'),
            version=d.get('version', 'E'),
            font_override=d.get('font'),
            font_size=d.get('fontSize', 60),
            tag_font_size=d.get('tagFontSize', 22),
            icon=d.get('icon', 'none'),
            texture=d.get('texture', 'paper'),
        )
        raw_name = d.get('filename', f'card-{d.get("version","E").lower()}.png')
        filename = re.sub(r'\.(png|jpg|jpeg)$', '.svg', raw_name, flags=re.IGNORECASE)
        if not filename.endswith('.svg'):
            filename += '.svg'
        return Response(
            svg.encode('utf-8'),
            mimetype='image/svg+xml',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        return Response(
            json.dumps({'error': str(e), 'trace': tb[-600:]}, ensure_ascii=False),
            status=500, mimetype='application/json',
        )


if __name__ == '__main__':
    print(f'\n  Mind.teum Card Studio  →  http://localhost:{PORT}\n')
    if not os.environ.get('RENDER'):
        threading.Timer(1.2, lambda: webbrowser.open(f'http://localhost:{PORT}')).start()
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
