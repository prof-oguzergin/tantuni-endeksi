# -*- coding: utf-8 -*-
"""Aylık enflasyon paylaşım kartlarını (X 1200x675, LinkedIn 1200x1500) sitedeki veriden üretir.

Kullanım: python tools/enflasyon_kart.py "<bugünün tarihi>" "<X vurgu cümlesi>" "<LinkedIn not cümlesi>"
Vurgu ve not HTML içerebilir (<b>...</b>). Kartların <head> bölümü (biçem) korunur, gövde yeniden yazılır.
Sonra başsız Chrome ile çek ve kırp (ayrıntı kart dosyalarının başındaki yorumda).
"""
import re, sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
t = (KOK / 'index.html').read_text(encoding='utf-8')

def dizi(ad):
    s = re.search(r'const ' + ad + r' = \[(.*?)\];', t, re.S).group(1)
    return [x.strip().strip("'") for x in s.replace('\n', '').split(',') if x.strip()]

etiketler = dizi('inflationLabels')
seri = {'tantuni': list(map(float, dizi('tantuniInflation'))),
        'tuik': list(map(float, dizi('tuikInflation'))),
        'enag': list(map(float, dizi('enagInflation')))}
n = len(etiketler)

AYLAR = {'Oca': 'Ocak', 'Şub': 'Şubat', 'Mar': 'Mart', 'Nis': 'Nisan', 'May': 'Mayıs', 'Haz': 'Haziran',
         'Tem': 'Temmuz', 'Ağu': 'Ağustos', 'Eyl': 'Eylül', 'Eki': 'Ekim', 'Kas': 'Kasım', 'Ara': 'Aralık'}
def uzun(e):
    a, y = e.split()
    return f'{AYLAR[a]} 20{y}'
ilk_ay, son_ay = uzun(etiketler[0]), uzun(etiketler[-1])

satirlar = re.findall(r"\{date:'([\d-]+)', price:(\d+), usd:([\d.]+), minWage:\d+, count:([\d.]+), goldTL:([\d.]+)\}", t)
baz = next(s for s in satirlar if s[0] == '2020-12-17')
son = satirlar[-1]
def virgul(x, b=1):
    return f'{x:.{b}f}'.replace('.', ',')

bugun, vurgu, not_ = sys.argv[1], sys.argv[2], sys.argv[3]

ADLAR = {'enag': ('ENAG', 'bağımsız ölçüm'), 'tuik': ('TÜİK', 'resmî ölçüm')}
RENK = {'enag': '#ffd700', 'tuik': '#ff4757', 'tantuni': '#ff8c42'}
sira = sorted(seri, key=lambda k: -seri[k][-1])  # en yüksek oran en üstte

def satir_html(k, tantuni_alt):
    ad, alt = ADLAR.get(k, ('Tantuni', tantuni_alt))
    v = seri[k][-1]
    return (f'    <div class="satir {k}">\n'
            f'      <div class="ad">{ad}<small>{alt}</small></div>\n'
            f'      <div class="yol"><div class="bar" style="width:{min(v / 50 * 100, 100):.1f}%"></div></div>\n'
            f'      <div class="deger">%{virgul(v)}</div>\n'
            f'    </div>\n')

def cizgiler(gen, y0, k_olcek, kalin, ince, op):
    xy = lambda i, v: (i * gen / (n - 1), y0 - k_olcek * v)
    out = []
    for k in ('enag', 'tuik', 'tantuni'):  # tantuni en üstte çizilir
        pts = ' '.join(f'{x:.1f},{y:.1f}' for x, y in (xy(i, v) for i, v in enumerate(seri[k])))
        ek = '' if k == 'tantuni' else f' opacity="{op}"'
        out.append(f'      <polyline points="{pts}" fill="none" stroke="{RENK[k]}" stroke-width="{kalin if k == "tantuni" else ince}" stroke-linejoin="round"{ek}/>')
    for k in ('enag', 'tantuni', 'tuik'):
        out.append(f'      <circle cx="{gen}" cy="{y0 - k_olcek * seri[k][-1]:.1f}" r="5" fill="{RENK[k]}"/>')
    return '\n'.join(out), y0 - k_olcek * 100

# X kartı
cz, y100 = cizgiler(1088, 128, 0.59, 3.4, 2.4, 0.9)
x_govde = f'''<body>
  <div class="ust">
    <div class="ay">{son_ay} <span>yıllık enflasyon</span></div>
    <div class="etiket">🌯 Tantuni Endeksi</div>
  </div>

  <div class="satirlar">
{''.join(satir_html(k, 'Ankara, tek işletme') for k in sira)}  </div>

  <div class="vurgu">
    {vurgu}
  </div>

  <div class="gidisat">
    <div class="gidisat-ust">
      <span><b>{n} ayın gidişatı</b> · {ilk_ay} - {son_ay}</span>
      <span>kesikli çizgi %100</span>
    </div>
    <svg class="trend" viewBox="0 0 1088 150" preserveAspectRatio="none" aria-hidden="true">
      <line x1="0" y1="{y100:.1f}" x2="1088" y2="{y100:.1f}" stroke="rgba(255,255,255,0.08)" stroke-width="1" stroke-dasharray="5 5"/>
{cz}
    </svg>
  </div>

  <div class="alt">
    <div>{bugun} · tantuni <b>₺{son[1]}</b> · 2020'de ₺{baz[1]} idi</div>
    <div class="marka">tantuni.oguzergin.net</div>
  </div>
</body>
</html>
'''

# LinkedIn kartı: dikey grafik solda, Aralık 2020 kutuları sağda
LG, LY = 690, 500                      # grafik alanı (piksel, svg ölçeğiyle bire bir)
ust_v = max(max(s) for s in seri.values()) + 4
alt_v = min(min(s) for s in seri.values()) - 6
li_k = (LY - 40) / (ust_v - alt_v)     # altta yıl etiketlerine yer kalır
li_y0 = 8 + ust_v * li_k
cz, _ = cizgiler(LG - 8, li_y0, li_k, 4.0, 2.8, 0.92)
izgara = '\n'.join(
    f'      <line x1="34" y1="{li_y0 - li_k * v:.1f}" x2="{LG - 8}" y2="{li_y0 - li_k * v:.1f}" stroke="rgba(255,255,255,{0.12 if v == 100 else 0.06})" stroke-width="1" stroke-dasharray="6 6"/>\n'
    f'      <text x="0" y="{li_y0 - li_k * v + 4:.1f}">%{v}</text>'
    for v in (50, 100, 150) if alt_v < v < ust_v)
izgara += '\n' + '\n'.join(
    f'      <text x="{34 + i * (LG - 42) / (n - 1):.1f}" y="{LY - 4}" text-anchor="middle">20{e.split()[1]}</text>'
    for i, e in enumerate(etiketler) if e.startswith('Oca'))
cz = cz.replace('<polyline points="', '<polyline transform="translate(34 0) scale(%.4f 1)" points="' % ((LG - 42) / (LG - 8)))
cz = re.sub(r'<circle cx="[\d.]+"', f'<circle cx="{LG - 8}"', cz)
kutu = lambda ad, eski, yeni: (f'      <div class="kutu">\n        <div class="kutu-ad">{ad}</div>\n'
                               f'        <div class="kutu-deger"><span class="eski">{eski}</span><span class="ok">→</span>{yeni}</div>\n      </div>\n')
li_govde = f'''<body>
  <div class="ust">
    <div class="marka">🌯 Tantuni Endeksi</div>
    <div class="tarih">{bugun}</div>
  </div>

  <h1>{son_ay} enflasyonu<br><span>ve bir dürümün altı yılı</span></h1>
  <div class="girus">
    Ankara'da aynı işletmenin et tantunisi, Ekim 2020'den beri kayıt altında.
  </div>

  <div class="bolum">
    <div class="bolum-ad">{son_ay} · yıllık enflasyon</div>
{''.join(satir_html(k, 'bu endeks') for k in sira)}    <div class="not">
      {not_}
    </div>
  </div>

  <div class="alt-blok">
    <div class="bolum">
      <div class="bolum-ad">{n} ayın gidişatı</div>
      <div class="trend-ust"><span>{ilk_ay} - {son_ay}</span></div>
      <svg class="trend" viewBox="0 0 {LG} {LY}" aria-hidden="true">
{izgara}
{cz}
      </svg>
      <div class="lejant">
        <span><i style="background:#ffd700"></i>ENAG</span>
        <span><i style="background:#ff8c42;height:4.5px"></i>Tantuni</span>
        <span><i style="background:#ff4757"></i>TÜİK</span>
      </div>
    </div>

    <div class="bolum">
      <div class="bolum-ad">Aralık 2020'den bugüne</div>
      <div class="kutular">
{kutu('Fiyat', '₺' + baz[1], '₺' + son[1])}{kutu('Dolar karşılığı', '$' + virgul(float(baz[2]), 2), '$' + virgul(float(son[2]), 2))}{kutu('Asgari ücretle adet', round(float(baz[3])), round(float(son[3])))}{kutu('1 gram altınla adet', virgul(float(baz[4]) / int(baz[1])), virgul(float(son[4]) / int(son[1])))}      </div>
    </div>
  </div>

  <div class="alt">tantuni.oguzergin.net</div>
</body>
</html>
'''

for ad, govde in (('enflasyon-karti.html', x_govde), ('enflasyon-karti-linkedin.html', li_govde)):
    p = KOK / 'tools' / ad
    bas = p.read_text(encoding='utf-8').split('<body>')[0]
    p.write_text(bas + govde, encoding='utf-8', newline='\n')
    print('yazıldı', p.name)
