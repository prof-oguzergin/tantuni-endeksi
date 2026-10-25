"""Asgari ücretle alınabilen tantuni sayısı paylaşım kartları.

index.html'deki tantuniData'dan basamaklı çizgi üretir, iki şablon yazar:
  tools/alim-gucu-karti.html           1200x675  (X)
  tools/alim-gucu-karti-linkedin.html  1200x1500 (LinkedIn)
  tools/alim-gucu-karti-instagram.html 1080x1080 (Instagram)
Sonra başsız Chrome ile çekilir (pencere yüksekliği karttan uzun, çıktı kırpılır).
"""
import re
import datetime as dt
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
src = (KOK / 'index.html').read_text(encoding='utf-8')
rows = re.findall(r"\{date:'(\d{4}-\d\d-\d\d)', price:([\d.]+), usd:[\d.]+, minWage:(\d+)", src)
rows = [(dt.date.fromisoformat(d), float(p), int(w)) for d, p, w in rows]
pts = [(d, w / p) for d, p, w in rows]

baz = next(c for d, c in pts if d == dt.date(2020, 12, 17))
son_d, son = pts[-1]
yil = (son_d - dt.date(2020, 12, 17)).days / 365.25
yillik = ((son / baz) ** (1 / yil) - 1) * 100
kayip = (1 - son / baz) * 100

zirve = {}
for d, c in pts:
    if d.year >= 2021 and (d.year not in zirve or c > zirve[d.year][1]):
        zirve[d.year] = (d, c)

AYLAR = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos',
         'Eylül', 'Ekim', 'Kasım', 'Aralık']


def tr(x, nd=1):
    return f'{x:.{nd}f}'.replace('.', ',')


def svg(W, H, pad_l=8, pad_r=70, pad_t=46, pad_b=40, yazi=1.0):
    d0, d1 = pts[0][0], son_d
    ymax = 170.0
    iw, ih = W - pad_l - pad_r, H - pad_t - pad_b

    def X(d):
        return pad_l + (d - d0).days / (d1 - d0).days * iw

    def Y(v):
        return pad_t + (1 - v / ymax) * ih

    yol = []
    for i, (d, c) in enumerate(pts):
        x, y = X(d), Y(c)
        if i == 0:
            yol.append(f'M{x:.1f},{y:.1f}')
        else:
            yol.append(f'V{y:.1f}')
        if i + 1 < len(pts):
            yol.append(f'H{X(pts[i + 1][0]):.1f}')
    cizgi = ' '.join(yol)
    alan = f'{cizgi} V{Y(0):.1f} H{X(d0):.1f} Z'

    fs = lambda n: f'{n * yazi:.1f}'
    o = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">',
         '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0" stop-color="#ff8c42" stop-opacity="0.30"/>'
         '<stop offset="1" stop-color="#ff8c42" stop-opacity="0.02"/></linearGradient></defs>']
    for v in (50, 100, 150):
        o.append(f'<line x1="{pad_l}" x2="{W - 44 * yazi:.1f}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" '
                 f'stroke="rgba(255,255,255,0.07)" stroke-dasharray="4 6"/>')
        o.append(f'<text x="{W - 2}" y="{Y(v) + 5:.1f}" text-anchor="end" fill="#6e6e8c" font-size="{fs(15)}">{v}</text>')
    for y in range(2021, 2027):
        x = X(dt.date(y, 1, 1))
        o.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{pad_t - 10}" y2="{Y(0):.1f}" stroke="rgba(255,255,255,0.06)"/>')
        o.append(f'<text x="{x + 6:.1f}" y="{H - 10}" fill="#8585a5" font-size="{fs(16)}" font-weight="600">{y}</text>')
    o.append(f'<line x1="{pad_l}" x2="{W - 44 * yazi:.1f}" y1="{Y(0):.1f}" y2="{Y(0):.1f}" stroke="rgba(255,255,255,0.14)"/>')
    o.append(f'<path d="{alan}" fill="url(#g)"/>')
    o.append(f'<path d="{cizgi}" fill="none" stroke="#ff8c42" stroke-width="3.2" stroke-linejoin="round"/>')
    # yıllık zirveleri birleştiren kesikli çizgi
    zp = [zirve[y] for y in sorted(zirve)]
    o.append('<polyline points="' + ' '.join(f'{X(d):.1f},{Y(c):.1f}' for d, c in zp) +
             '" fill="none" stroke="#ff4757" stroke-width="2.2" stroke-dasharray="7 6" opacity="0.85"/>')
    for d, c in zp:
        o.append(f'<circle cx="{X(d):.1f}" cy="{Y(c):.1f}" r="{fs(6)}" fill="#ff4757" stroke="#0f0f13" stroke-width="2"/>')
        o.append(f'<text x="{X(d):.1f}" y="{Y(c) - 14:.1f}" text-anchor="middle" fill="#ff6b78" '
                 f'font-size="{fs(21)}" font-weight="800">{round(c)}</text>')
    xb, yb = X(dt.date(2020, 12, 17)), Y(baz)
    o.append(f'<circle cx="{xb:.1f}" cy="{yb:.1f}" r="{fs(6)}" fill="#c7c7dd"/>')
    o.append(f'<text x="{xb:.1f}" y="{yb + 30:.1f}" text-anchor="start" fill="#c7c7dd" font-size="{fs(19)}" font-weight="700">{round(baz)}</text>')
    xs, ys = X(son_d), Y(son)
    o.append(f'<circle cx="{xs:.1f}" cy="{ys:.1f}" r="{fs(8)}" fill="#ff8c42" stroke="#0f0f13" stroke-width="2.5"/>')
    o.append(f'<text x="{xs + 14:.1f}" y="{ys + 9:.1f}" fill="#ff8c42" font-size="{fs(28)}" font-weight="900">{round(son)}</text>')
    o.append('</svg>')
    return '\n'.join(o)


tarih = f'{son_d.day} {AYLAR[son_d.month - 1]} {son_d.year}'
zirveler = ', '.join(str(round(zirve[y][1])) for y in sorted(zirve))
fiyat = int(rows[-1][1])

ORTAK_CSS = """
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Inter', sans-serif; color: #f0f0f5; position: relative;
    background: radial-gradient(ellipse 60% 55% at 70% 30%, rgba(255,140,66,0.12) 0%, transparent 62%),
                linear-gradient(150deg, #0f0f13 0%, #1a0f05 52%, #0f0a05 100%); }
  .marka { font-size: 21px; font-weight: 700; color: #ff8c42; }
  .tarih { font-size: 18px; color: #8585a5; font-weight: 500; }
  .ust { display: flex; justify-content: space-between; align-items: baseline; }
  h1 { font-weight: 900; letter-spacing: -1.2px; line-height: 1.1; }
  h1 span { color: #ff8c42; }
  .alt-yazi { color: #a8a8c4; font-weight: 500; line-height: 1.45; }
  .sayi { display: flex; align-items: baseline; gap: 18px; font-weight: 900; letter-spacing: -2px; }
  .sayi .eski { color: #8a8aa6; }
  .sayi .ok { color: #ff8c42; font-weight: 700; }
  .sayi .yeni { color: #ff8c42; text-shadow: 0 0 34px rgba(255,140,66,0.45); }
  .lejant { display: flex; gap: 26px; color: #a8a8c4; font-size: 16px; }
  .lejant i { display: inline-block; width: 18px; height: 4px; border-radius: 2px; margin-right: 8px; vertical-align: middle; }
  .site { font-weight: 700; color: #ff8c42; }
"""
HEAD = ('<!DOCTYPE html>\n<html lang="tr">\n<head>\n<meta charset="UTF-8">\n'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">\n')

x_html = HEAD + f"""<style>{ORTAK_CSS}
  html, body {{ width: 1200px; height: 675px; }}
  body {{ padding: 38px 52px 0; }}
  h1 {{ font-size: 40px; margin-top: 10px; }}
  .orta {{ display: flex; justify-content: space-between; align-items: flex-end; margin-top: 6px; }}
  .alt-yazi {{ font-size: 18px; }}
  .sayi {{ font-size: 64px; }}
  .sayi small {{ font-size: 20px; color: #8585a5; font-weight: 600; letter-spacing: 0; }}
  .grafik {{ margin-top: 10px; }}
  .alt {{ position: absolute; left: 52px; right: 52px; bottom: 22px; display: flex; justify-content: space-between; align-items: center; }}
</style>
</head>
<body>
  <div class="ust"><div class="marka">🌯 Tantuni Endeksi</div><div class="tarih">{tarih} · tantuni ₺{fiyat}</div></div>
  <div class="orta">
    <div>
      <h1>Asgari ücretle <span>kaç tantuni?</span></h1>
      <div class="alt-yazi">Net asgari ücretle alınabilen et tantuni sayısı, Ankara, aynı işletme</div>
    </div>
    <div class="sayi"><span class="eski">{round(baz)}</span><span class="ok">→</span><span class="yeni">{round(son)}</span></div>
  </div>
  <div class="grafik">{svg(1096, 430, yazi=1.0)}</div>
  <div class="alt">
    <div class="lejant"><span><i style="background:#ff8c42"></i>tantuni sayısı</span><span><i style="background:#ff4757"></i>her yılın en yüksek değeri</span></div>
    <div class="site">tantuni.oguzergin.net</div>
  </div>
</body>
</html>
"""

li_html = HEAD + f"""<style>{ORTAK_CSS}
  html, body {{ width: 1200px; height: 1500px; }}
  body {{ padding: 56px 60px 0; }}
  .marka {{ font-size: 23px; }} .tarih {{ font-size: 19px; }}
  h1 {{ font-size: 60px; margin-top: 26px; }}
  .alt-yazi {{ font-size: 22px; margin-top: 16px; }}
  .kutular {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 40px; }}
  .kutu {{ background: rgba(255,255,255,0.035); border: 1px solid rgba(255,255,255,0.07); border-radius: 16px; padding: 24px 28px; }}
  .kutu-ad {{ font-size: 19px; color: #9a9ab8; font-weight: 600; margin-bottom: 8px; }}
  .kutu .sayi {{ font-size: 64px; }}
  .kutu .tek {{ font-size: 64px; font-weight: 900; letter-spacing: -2px; color: #ff6b78; }}
  .grafik {{ margin-top: 34px; }}
  .lejant {{ margin-top: 14px; font-size: 17px; }}
  .not {{ margin-top: 30px; padding: 20px 24px; background: rgba(255,140,66,0.08); border-left: 3px solid #ff8c42;
         border-radius: 10px; font-size: 22px; color: #d8d8ea; line-height: 1.55; }}
  .not b {{ color: #ffb347; }}
  .alt {{ position: absolute; left: 60px; right: 60px; bottom: 44px; border-top: 1px solid rgba(255,255,255,0.08);
         padding-top: 20px; text-align: center; font-size: 25px; }}
</style>
</head>
<body>
  <div class="ust"><div class="marka">🌯 Tantuni Endeksi</div><div class="tarih">{tarih}</div></div>
  <h1>Asgari ücretle<br><span>kaç tantuni alınıyor?</span></h1>
  <div class="alt-yazi">Net asgari ücretle alınabilen et tantuni sayısı. Ankara'da aynı işletme, Ekim 2020'den beri kayıt altında.</div>
  <div class="kutular">
    <div class="kutu"><div class="kutu-ad">Aralık 2020 → {AYLAR[son_d.month - 1]} {son_d.year}</div>
      <div class="sayi"><span class="eski">{round(baz)}</span><span class="ok">→</span><span class="yeni">{round(son)}</span></div></div>
    <div class="kutu"><div class="kutu-ad">Yıllık ortalama kayıp</div><div class="tek">%{tr(-yillik, 0)}</div></div>
  </div>
  <div class="grafik">{svg(1080, 680, yazi=1.15)}</div>
  <div class="lejant"><span><i style="background:#ff8c42"></i>tantuni sayısı</span><span><i style="background:#ff4757"></i>her yılın en yüksek değeri</span></div>
  <div class="not">Her yılbaşı zammı sayıyı yukarı çekiyor, ama her yılın zirvesi bir öncekinin altında kalıyor.
    2021'de <b>{round(zirve[2021][1])}</b> olan zirve 2026'da <b>{round(zirve[2026][1])}</b>'e indi. Altı yılda asgari ücretlinin alım gücü <b>yarının altına</b> indi.</div>
  <div class="alt"><span class="site">tantuni.oguzergin.net</span></div>
</body>
</html>
"""

ig_html = HEAD + f"""<style>{ORTAK_CSS}
  html, body {{ width: 1080px; height: 1080px; }}
  body {{ padding: 46px 48px 0; }}
  .marka {{ font-size: 21px; }} .tarih {{ font-size: 18px; }}
  h1 {{ font-size: 52px; margin-top: 20px; }}
  .alt-yazi {{ font-size: 19px; margin-top: 10px; }}
  .satir {{ display: flex; align-items: baseline; gap: 22px; margin-top: 22px; }}
  .satir .sayi {{ font-size: 76px; }}
  .satir .donem {{ font-size: 19px; color: #9a9ab8; font-weight: 600; }}
  .grafik {{ margin-top: 14px; }}
  .sonuc {{ margin-top: 22px; padding: 18px 24px; background: rgba(255,140,66,0.09); border-left: 3px solid #ff8c42;
           border-radius: 10px; font-size: 27px; font-weight: 600; color: #f0f0f5; }}
  .sonuc b {{ color: #ffb347; }}
  .alt {{ position: absolute; left: 48px; right: 48px; bottom: 30px; display: flex; justify-content: space-between; align-items: center; }}
</style>
</head>
<body>
  <div class="ust"><div class="marka">🌯 Tantuni Endeksi</div><div class="tarih">{tarih} · tantuni ₺{fiyat}</div></div>
  <h1>Asgari ücretle <span>kaç tantuni?</span></h1>
  <div class="alt-yazi">Net asgari ücretle alınabilen et tantuni sayısı, Ankara, aynı işletme</div>
  <div class="satir"><div class="sayi"><span class="eski">{round(baz)}</span><span class="ok">→</span><span class="yeni">{round(son)}</span></div>
    <div class="donem">Aralık 2020 → {AYLAR[son_d.month - 1]} {son_d.year}</div></div>
  <div class="grafik">{svg(984, 600, yazi=1.1)}</div>
  <div class="sonuc">Altı yılda asgari ücretlinin alım gücü <b>yarının altına</b> indi.</div>
  <div class="alt">
    <div class="lejant"><span><i style="background:#ff8c42"></i>tantuni sayısı</span><span><i style="background:#ff4757"></i>her yılın en yüksek değeri</span></div>
    <div class="site">tantuni.oguzergin.net</div>
  </div>
</body>
</html>
"""

(KOK / 'tools' / 'alim-gucu-karti-instagram.html').write_text(ig_html, encoding='utf-8', newline='\n')
(KOK / 'tools' / 'alim-gucu-karti.html').write_text(x_html, encoding='utf-8', newline='\n')
(KOK / 'tools' / 'alim-gucu-karti-linkedin.html').write_text(li_html, encoding='utf-8', newline='\n')
print(f'baz {baz:.1f} son {son:.1f} kayip %{kayip:.1f} yillik %{yillik:.1f} ({yil:.2f} yil) zirveler {zirveler}')
