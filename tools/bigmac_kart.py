"""Tantuni ile Big Mac karşılaştırma kartı (1200x675): Türkiye, Dubai (BAE), Zürih (İsviçre), ABD.

Big Mac verisi The Economist'in açık verisi (github.com/TheEconomist/big-mac-data,
source-data/big-mac-source-data-v2.csv). Her Big Mac ölçüm tarihinde (Ocak ve Temmuz)
o gün geçerli tantuni fiyatı tantuniData'dan alınır; dolar karşılıkları için iki ürüne de
Economist'in o tarihteki kuru uygulanır. Asgari ücret o tarihte yürürlükteki net ücrettir.

Kullanım: python tools/bigmac_kart.py <big-mac-source-data-v2.csv>
"""
import csv
import re
import sys
import datetime as dt
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
src = (KOK / 'index.html').read_text(encoding='utf-8')
rows = [(dt.date.fromisoformat(d), float(p))
        for d, p in re.findall(r"\{date:'(\d{4}-\d\d-\d\d)', price:([\d.]+)", src)]

# Net asgari ücret, yürürlüğe giriş tarihiyle
UCRET = [(dt.date(2021, 1, 1), 2825), (dt.date(2022, 1, 1), 4253), (dt.date(2022, 7, 1), 5500),
         (dt.date(2023, 1, 1), 8506), (dt.date(2023, 7, 1), 11402), (dt.date(2024, 1, 1), 17002),
         (dt.date(2025, 1, 1), 22104), (dt.date(2026, 1, 1), 28075)]


def ucret(d):
    return [w for t, w in UCRET if t <= d][-1]


def tantuni(d):
    return [p for t, p in rows if t <= d][-1]


bm = {}
for r in csv.DictReader(open(sys.argv[1], encoding='utf-8')):
    if r['iso_a3'] in ('TUR', 'USA', 'ARE', 'CHE') and r['date'] >= '2021-01-01':
        bm.setdefault(r['date'], {})[r['iso_a3']] = (float(r['local_price']), float(r['dollar_ex']))

veri = []
for d in sorted(bm):
    if set(bm[d]) != {'TUR', 'USA', 'ARE', 'CHE'}:
        continue
    D = dt.date.fromisoformat(d)
    (p, k), (pu, _) = bm[d]['TUR'], bm[d]['USA']
    t = tantuni(D)
    are = bm[d]['ARE'][0] / bm[d]['ARE'][1]
    che = bm[d]['CHE'][0] / bm[d]['CHE'][1]
    veri.append(dict(d=D, bm=p, kur=k, bm_usd=p / k, us=pu, are=are, che=che, t=t, t_usd=t / k, w=ucret(D)))

ilk, son = veri[0], veri[-1]
AY = {1: 'Ocak', 7: 'Temmuz'}


def tr(x, nd=2):
    s = f'{x:,.{nd}f}'
    return s.replace(',', 'X').replace('.', ',').replace('X', '.')


def svg(W=720, H=440, pl=44, pr=96, pt=22, pb=36):
    n = len(veri)
    ymax = 10.0
    X = lambda i: pl + i * (W - pl - pr) / (n - 1)
    Y = lambda v: pt + (1 - v / ymax) * (H - pt - pb)
    o = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">']
    for v in (2, 4, 6, 8, 10):
        o.append(f'<line x1="{pl}" x2="{W - pr + 20}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="rgba(255,255,255,0.07)" stroke-dasharray="4 6"/>')
        o.append(f'<text x="0" y="{Y(v) + 5:.1f}" fill="#6e6e8c" font-size="14">${v}</text>')
    o.append(f'<line x1="{pl}" x2="{W - pr + 20}" y1="{Y(0):.1f}" y2="{Y(0):.1f}" stroke="rgba(255,255,255,0.14)"/>')
    for i, v in enumerate(veri):
        if v['d'].month == 1:
            o.append(f'<text x="{X(i):.1f}" y="{H - 10}" text-anchor="middle" fill="#8585a5" font-size="15" font-weight="600">{v["d"].year}</text>')
    seriler = [('are', '#2ed573', 'Big Mac Dubai'), ('us', '#4aa3ff', 'Big Mac ABD'), ('che', '#c08cff', 'Big Mac Zürih'),
               ('bm_usd', '#ffd700', 'Big Mac Türkiye'), ('t_usd', '#ff8c42', 'Tantuni')]
    for key, renk, ad in seriler:
        kal = 4.4 if key == 't_usd' else (3.4 if key == 'bm_usd' else 2.6)
        o.append('<polyline points="' + ' '.join(f'{X(i):.1f},{Y(v[key]):.1f}' for i, v in enumerate(veri)) +
                 f'" fill="none" stroke="{renk}" stroke-width="{kal}" stroke-linejoin="round"/>')
        for i, v in enumerate(veri):
            o.append(f'<circle cx="{X(i):.1f}" cy="{Y(v[key]):.1f}" r="3.6" fill="{renk}"/>')
        y_son = Y(son[key])
        o.append(f'<text x="{X(n - 1) + 12:.1f}" y="{y_son + 6:.1f}" fill="{renk}" font-size="19" font-weight="800">${tr(son[key])}</text>')
    o.append('</svg>')
    return '\n'.join(o)


tl_t = son['t'] / ilk['t']
tl_b = son['bm'] / ilk['bm']
html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ width: 1200px; height: 675px; }}
  body {{ font-family: 'Inter', sans-serif; color: #f0f0f5; position: relative; padding: 36px 48px 0;
    background: radial-gradient(ellipse 60% 60% at 30% 40%, rgba(255,140,66,0.11) 0%, transparent 62%),
                linear-gradient(150deg, #0f0f13 0%, #1a0f05 52%, #0f0a05 100%); }}
  .ust {{ display: flex; justify-content: space-between; align-items: baseline; }}
  .marka {{ font-size: 20px; font-weight: 700; color: #ff8c42; }}
  .tarih {{ font-size: 17px; color: #8585a5; }}
  h1 {{ font-size: 40px; font-weight: 900; letter-spacing: -1px; margin-top: 8px; }}
  h1 span {{ color: #ff8c42; }}
  .alt-yazi {{ font-size: 17px; color: #a8a8c4; margin-top: 4px; }}
  .govde {{ display: flex; gap: 30px; margin-top: 14px; }}
  .lejant {{ display: flex; gap: 22px; font-size: 15px; color: #c7c7dd; margin-bottom: 2px; }}
  .lejant i {{ display: inline-block; width: 16px; height: 4px; border-radius: 2px; margin-right: 7px; vertical-align: middle; }}
  .yan {{ flex: 1; display: flex; flex-direction: column; gap: 12px; padding-top: 4px; }}
  .kutu {{ background: rgba(255,255,255,0.035); border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; padding: 14px 18px; }}
  .kutu-ad {{ font-size: 14.5px; color: #9a9ab8; font-weight: 600; margin-bottom: 8px; }}
  .sat {{ display: flex; justify-content: space-between; align-items: baseline; font-size: 17px; color: #c7c7dd; margin-top: 3px; }}
  .sat b {{ font-size: 22px; font-weight: 800; }}
  .sat .t {{ color: #ff8c42; }} .sat .b {{ color: #ffd700; }}
  .not {{ font-size: 15.5px; color: #d8d8ea; line-height: 1.45; background: rgba(74,163,255,0.08);
          border-left: 3px solid #4aa3ff; border-radius: 10px; padding: 12px 16px; }}
  .not b {{ color: #8cc4ff; }}
  .alt {{ position: absolute; left: 48px; right: 48px; bottom: 20px; display: flex; justify-content: space-between;
          font-size: 14.5px; color: #8585a5; }}
  .alt .site {{ color: #ff8c42; font-weight: 700; font-size: 17px; }}
</style>
</head>
<body>
  <div class="ust"><div class="marka">🌯 Tantuni Endeksi × 🍔 Big Mac</div><div class="tarih">{AY[ilk['d'].month]} {ilk['d'].year} - {AY[son['d'].month]} {son['d'].year}</div></div>
  <h1>Türkiye'de Big Mac, <span>Dubai'yi ve ABD'yi geçti</span></h1>
  <div class="alt-yazi">Dolar karşılığı fiyatlar, The Economist'in yılda iki Big Mac ölçümünde. Tantuni Ankara'da aynı işletme.</div>
  <div class="govde">
    <div>
      <div class="lejant"><span><i style="background:#ff8c42"></i>Tantuni</span><span><i style="background:#ffd700"></i>Big Mac Türkiye</span><span><i style="background:#c08cff"></i>Zürih</span><span><i style="background:#4aa3ff"></i>ABD (ulusal fiyat)</span><span><i style="background:#2ed573"></i>Dubai</span></div>
      {svg()}
    </div>
    <div class="yan">
      <div class="kutu"><div class="kutu-ad">TL fiyatı, {AY[ilk['d'].month]} {ilk['d'].year} → {AY[son['d'].month]} {son['d'].year}</div>
        <div class="sat"><span>Tantuni ₺{tr(ilk['t'], 0)} → ₺{tr(son['t'], 0)}</span><b class="t">{tr(tl_t, 1)} kat</b></div>
        <div class="sat"><span>Big Mac ₺{tr(ilk['bm'])} → ₺{tr(son['bm'], 0)}</span><b class="b">{tr(tl_b, 1)} kat</b></div></div>
      <div class="kutu"><div class="kutu-ad">Net asgari ücretle kaç tane?</div>
        <div class="sat"><span>Tantuni</span><b class="t">{round(ilk['w'] / ilk['t'])} → {round(son['w'] / son['t'])}</b></div>
        <div class="sat"><span>Big Mac</span><b class="b">{round(ilk['w'] / ilk['bm'])} → {round(son['w'] / son['bm'])}</b></div></div>
      <div class="not">Türkiye'de Big Mac Ocak 2021'de Dubai'dekinin <b>yarı fiyatınaydı</b>, Temmuz 2026'da <b>%{tr((son['bm_usd'] / son['are'] - 1) * 100, 0)} pahalı</b>.
        Big Mac Endeksi'ne göre TL 2014'ten beri ilk kez değerinin üstünde (+%{tr((son['bm_usd'] / son['us'] - 1) * 100, 0)}).</div>
    </div>
  </div>
  <div class="alt"><span>Big Mac verisi: The Economist, ülke fiyatı (Dubai için BAE, Zürih için İsviçre)</span><span class="site">tantuni.oguzergin.net</span></div>
</body>
</html>
"""
(KOK / 'tools' / 'bigmac-karti.html').write_text(html, encoding='utf-8', newline='\n')
for v in veri:
    print(v['d'], f"ARE ${v['are']:.2f} CHE ${v['che']:.2f} BM {v['bm']:.2f} ${v['bm_usd']:.2f} US ${v['us']:.2f} | T {v['t']:.0f} ${v['t_usd']:.2f} | t/BM {v['t']/v['bm']:.2f} | ucret {v['w']} BM {v['w']/v['bm']:.0f} T {v['w']/v['t']:.0f}")
print('TL kat: tantuni', round(tl_t, 2), 'bigmac', round(tl_b, 2))
