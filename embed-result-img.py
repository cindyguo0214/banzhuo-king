"""把 result-img 的結算插圖壓成 WebP，內嵌進 index.html（單檔也能匯出 PNG，canvas 不會被污染）。
換圖或改對應後重新執行：python embed-result-img.py
"""
import base64, io, os, re
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(ROOT, 'index.html')
WIDTH, QUALITY = 1080, 72

# 圖卡 key → 檔案。吃席：f-稱號-桌別（1 婚宴、2 尾牙、3 普渡、4 廟口），依畫面上的角色對應，不是檔名尾碼
ART = {
    'f-king-1': '吃席/辦桌掃盤王的勝利-1.png',   'f-king-2': '吃席/辦桌掃盤王-2.png',
    'f-king-3': '吃席/辦桌掃盤王-3.png',         'f-king-4': '吃席/辦桌掃盤王登場-4.png',
    'f-full-1': '吃席/吃好吃滿的幸福宴席-1.png', 'f-full-2': '吃席/台式宴席，吃好吃滿-2.png',
    'f-full-3': '吃席/吃好吃滿，還有雞腿-4.png', 'f-full-4': '吃席/吃好吃滿，幸福滿腹-3.png',
    'f-shy-1': '吃席/客氣拒吃，雞腿來了-1.png',  'f-shy-2': '吃席/太客氣的年終宴-2.png',
    'f-shy-3': '吃席/客氣拒吃，鬼怪端來雞腿-3.png', 'f-shy-4': '吃席/神明熱情餵雞腿-4.png',
    'f-enemy-1': '吃席/雞腿誤飛，三人驚呆-2.png', 'f-enemy-2': '吃席/雞腿誤中臉頰-1.png',
    'f-enemy-3': '吃席/同桌公敵：雞腿飛上臉-3.png', 'f-enemy-4': '吃席/同桌公敵：雞腿飛臉-4.png',
    'f-bone-1': '吃席/放大鏡鑑賞雞骨頭-1.png',   'f-bone-2': '吃席/雞骨頭鑑賞家-2.png',
    'f-bone-3': '吃席/放大鏡鑑賞雞骨頭-4.png',   'f-bone-4': '吃席/放大鏡鑑賞空骨大餐-3.png',
    'f-empty-1': '吃席/空盤收藏家與飛蠅-1.png',  'f-empty-2': '吃席/空盤收藏家的尷尬瞬間-4.png',
    'f-empty-3': '吃席/空盤收藏家-3.png',        'f-empty-4': '吃席/空碗收藏家-2.png',
    # 四攤：l-攤-評價（神明誕辰 li＝擲出立筊）
    'l-1-god': '關卡/婚禮紅包勝利時刻.png',      'l-1-pass': '關卡/婚禮紅包順利入箱.png',
    'l-1-fail': '關卡/婚宴紅包箱的尷尬瞬間-1.png', 'l-1-erupt': '關卡/婚宴紅包大噴發-2.png',
    'l-2-god': '關卡/年終抽獎大獲全勝-3.png',    'l-2-pass': '關卡/年終抽獎小勝利-4.png',
    'l-2-fail': '關卡/抽獎箱卡住的拳頭-3.png',   'l-2-tip': '關卡/抽獎箱翻倒大災難-1.png',
    'l-3-god': '關卡/白幽靈搶供品大勝-2.png',    'l-3-pass': '關卡/白鬼抱著翡翠供品袋-4.png',
    'l-3-fail': '關卡/鬼怪拔河搶烤雞，空袋落敗-1.png', 'l-3-salt': '關卡/奶奶撒米鹽，白鬼狼狽倒飛-3.png',
    'l-4-li': '關卡/站立筊杯的驚喜瞬間-2.png',   'l-4-pass': '關卡/擲筊得聖筊-4.png',
    'l-4-fail': '關卡/兩枚紅筊，擲筊失敗-1.png', 'l-4-kick': '關卡/掃把送客，神明傻眼-2.png',
}

used = set(ART.values())
for sub in ('吃席', '關卡'):
    for f in os.listdir(os.path.join(ROOT, 'result-img', sub)):
        if f'{sub}/{f}' not in used:
            print('沒用到的圖：', sub, f)

parts, total = [], 0
for key, rel in ART.items():
    im = Image.open(os.path.join(ROOT, 'result-img', rel)).convert('RGB')
    im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=QUALITY, method=6)
    total += buf.tell()
    parts.append(f'"{key}":"data:image/webp;base64,{base64.b64encode(buf.getvalue()).decode()}"')

block = '<script id="card-art">window.CARD_ART={' + ','.join(parts) + '};</script>'
s = open(HTML, encoding='utf-8', newline='').read()
s, n = re.subn(r'<script id="card-art">.*?</script>', lambda _: block, s, flags=re.S)
if not n:
    assert s.count('</body>') == 1
    s = s.replace('</body>', block + '\n</body>')
open(HTML, 'w', encoding='utf-8', newline='').write(s)
print(f'{len(ART)} 張，WebP 共 {total / 1e6:.1f} MB，index.html {os.path.getsize(HTML) / 1e6:.1f} MB')
