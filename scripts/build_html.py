"""Собирает build/slides.html (8 слайдов 1920×1080) из model/model.json.

Оформление — по брендбуку bcc insurance: белый фон, чёрный текст, акцент
Green только в крупных словах, мелкий акцентный текст — Dark Green,
Inter Bold + Medium, всё по левому краю, без капса и эмодзи.
"""

from __future__ import annotations

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
M = json.loads((ROOT / "model" / "model.json").read_text(encoding="utf-8"))
T = M["totals"]
SEG = M["segments"]
ACQ = M["acquisition"]
TOTAL_SLIDES = 8

NBSP = " "


def num(v: float, digits: int = 1) -> str:
    s = f"{v:,.{digits}f}".replace(",", NBSP).replace(".", ",")
    return s


def pct(v: float, digits: int = 1, sign: bool = False) -> str:
    s = num(abs(v) * 100, digits)
    if sign:
        s = ("+" if v >= 0 else "−") + s
    elif v < 0:
        s = "−" + s
    return s + "%"


def signed(v: float, digits: int = 1) -> str:
    return ("+" if v >= 0 else "−") + num(abs(v), digits)


def slide(n: int, body: str, cls: str = "") -> str:
    return f"""
<section class="slide {cls}">
  <header class="top">
    <img class="logo" src="../assets/brand/bcc-insurance-logo.svg" alt="bcc insurance">
    <span class="meta">Product Masters · неделя 2 · уровень 3</span>
  </header>
  {body}
  <footer class="foot"><span>RFM-анализ: меньше бюджета, больше повторных покупок</span><span>{n:02d} / {TOTAL_SLIDES:02d}</span></footer>
</section>"""


# ---------------------------------------------------------------- 01 обложка
import re
_house = (ROOT / "assets" / "brand" / "house-mask.svg").read_text(encoding="utf-8")
_d = " ".join(re.findall(r"d='([^']+)'|d=\"([^\"]+)\"", _house)[0]).strip()
HOUSE_SVG = (
    '<svg class="house-shape" viewBox="0 0 873 970" preserveAspectRatio="none">'
    '<defs><linearGradient id="hg" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#62CDA8" stop-opacity=".55"/>'
    '<stop offset=".7" stop-color="#DAFFED"/></linearGradient></defs>'
    f'<path d="{_d}" fill="url(#hg)"/></svg>'
)
cover = f"""
<div class="cover">
  <div class="cover-text">
    <span class="rubric">Расчётный кейс · e-commerce</span>
    <h1 class="h-xl">RFM-анализ: на&nbsp;<em>20%</em> меньше маркетинга, на&nbsp;<em>10%</em> больше выручки</h1>
    <p class="lead">Как перестать платить за покупки, которые случились бы и без нас, и вложить сэкономленное туда, где теряется повторная покупка</p>
    <p class="small">Product Masters · неделя 2 · уровень 3 (сложный) · октябрь 2026</p>
  </div>
  <div class="house">
    {HOUSE_SVG}
    <div class="house-stats">
      <div class="stat-card"><div class="stat">{pct(T['budget_change'], 0, True)}</div><p>маркетинговый бюджет<br>{num(T['budget_before'])} → {num(T['budget_after'])} млн ₸ в месяц</p></div>
      <div class="stat-card"><div class="stat">{pct(T['revenue_growth'], 1, True)}</div><p>выручка в базовом сценарии<br>{num(T['revenue_before'])} → {num(T['revenue_after'])} млн ₸ в месяц</p></div>
      <div class="stat-card"><div class="stat">{signed(T['margin_effect'])}</div><p>млн ₸ валовой прибыли в месяц<br>экономия + маржа с роста</p></div>
    </div>
  </div>
</div>"""

# ---------------------------------------------------------------- 02 ситуация
A = M["assumptions"]
s2 = f"""
<h2 class="h">Новые клиенты приходят, но <em>не возвращаются</em></h2>
<div class="cols-3">
  <div>
    <span class="rubric">Ситуация</span>
    <ul class="dots">
      <li>12 месяцев истории продаж, приток новых стабилен</li>
      <li>Последние 2 месяца падает доля повторных покупок</li>
      <li>Бюджет тратится «на всех одинаково»: массовые промокоды, рассылки и ретаргет по всей базе</li>
    </ul>
    <span class="rubric">Гипотезы падения — проверить за 2 недели</span>
    <ul class="dots">
      <li>Новые когорты хуже: сменился канал привлечения, пришли охотники за промо</li>
      <li>Первая покупка разочаровала: доставка, наличие, возвраты</li>
      <li>Клиенты устали от массовых рассылок и ждут скидку</li>
    </ul>
  </div>
  <div>
    <span class="rubric">Допущения модели</span>
    <p class="note">В кейсе нет транзакций, поэтому строю прозрачную модель: каждое число можно заменить фактом в Excel, остальное пересчитается.</p>
    <table class="kv">
      <tr><td>Клиентов с покупкой за 12 мес.</td><td>{num(A['customers_12m'], 0)}</td></tr>
      <tr><td>Выручка в месяц</td><td>{num(T['revenue_before'])} млн ₸</td></tr>
      <tr><td>Маркетинг в месяц</td><td>{num(T['budget_before'])} млн ₸</td></tr>
      <tr><td>Доля маркетинга в выручке</td><td>{pct(T['crr_before'])}</td></tr>
      <tr><td>Новых клиентов в месяц</td><td>{num(A['new_customers_month'], 0)}</td></tr>
      <tr><td>Валовая маржа</td><td>{pct(A['gross_margin'], 0)}</td></tr>
    </table>
  </div>
  <div>
    <span class="rubric">Как считаю RFM</span>
    <table class="grid-t">
      <tr><th>Балл</th><th>R — дней с покупки</th><th>F — заказов за год</th></tr>
      <tr><td>5</td><td>до 14</td><td>8 и больше</td></tr>
      <tr><td>4</td><td>15–30</td><td>5–7</td></tr>
      <tr><td>3</td><td>31–60</td><td>3–4</td></tr>
      <tr><td>2</td><td>61–120</td><td>2</td></tr>
      <tr><td>1</td><td>больше 120</td><td>1</td></tr>
    </table>
    <p class="note">M — квинтили суммы покупок за 12 месяцев: внутри сегмента задаёт приоритет (кому звонить, кому дать лучший оффер). Пересчёт — раз в месяц, чтобы видеть переходы между сегментами.</p>
  </div>
</div>"""

# ---------------------------------------------------------------- 03 сегменты
budget_share = {s["id"]: s["budget_before"] / T["budget_before"] for s in SEG}
rows = []
for s in SEG:
    bars = "".join(
        f'<div class="mini"><span class="mini-l">{label}</span>'
        f'<span class="mini-bar {cls}" style="width:{v * 100 * 6:.0f}px"></span>'
        f'<span class="mini-v">{pct(v, 0)}</span></div>'
        for label, v, cls in (
            ("клиенты", s["share_customers"], "b1"),
            ("выручка", s["share_revenue"], "b2"),
            ("бюджет", budget_share[s["id"]], "b3"),
        )
    )
    rows.append(
        f"<tr><td><b>{escape(s['name'])}</b><br><span class='muted'>{s['rule']}</span></td>"
        f"<td>{escape(s['who'])}</td><td>{bars}</td><td>{escape(s['goal'])}</td></tr>"
    )
hib = next(s for s in SEG if s["id"] == "hibernating")
s3 = f"""
<h2 class="h">Пять сегментов — <em>пять разных задач</em></h2>
<p class="sub">Главный вывод: спящие клиенты — {pct(hib['share_customers'], 0)} базы и {pct(hib['share_revenue'], 0)} выручки, но получают {pct(budget_share['hibernating'], 0)} маркетингового бюджета. Новые клиенты — 38% месячной выручки, здесь не показаны.</p>
<table class="seg">
  <colgroup><col style="width:330px"><col style="width:430px"><col style="width:520px"><col></colgroup>
  <tr><th>Сегмент</th><th>Кто это</th><th>Доля клиентов, выручки и бюджета</th><th>Цель</th></tr>
  {''.join(rows)}
</table>
<div class="legend"><span><i class="b1"></i>доля клиентов</span><span><i class="b2"></i>доля общей выручки</span><span><i class="b3"></i>доля бюджета сейчас</span></div>"""

# ---------------------------------------------------------------- 04 бюджет
lines = [*SEG, ACQ]
scale = 30  # px за 1 млн ₸
brows = []
for s in lines:
    d = s["budget_after"] - s["budget_before"]
    brows.append(f"""
<div class="brow">
  <div class="bname">{escape(s['name'])}</div>
  <div class="bbars">
    <div class="bar was" style="width:{s['budget_before'] * scale:.0f}px"><span>{num(s['budget_before'])}</span></div>
    <div class="bar now" style="width:{s['budget_after'] * scale:.0f}px"><span>{num(s['budget_after'])}</span></div>
  </div>
  <div class="bdelta {'up' if d > 0 else 'down'}">{signed(d)}</div>
</div>""")
s4 = f"""
<h2 class="h">Бюджет: <em>{num(T['budget_before'])} → {num(T['budget_after'])}</em> млн ₸ в месяц</h2>
<div class="cols-2w">
  <div>
    <div class="legend top-legend"><span><i class="was"></i>было, млн ₸</span><span><i class="now"></i>стало, млн ₸</span><span>Δ</span></div>
    {''.join(brows)}
  </div>
  <div class="logic">
    <span class="rubric">Логика</span>
    <ol class="steps">
      <li><b>Снимаем деньги там, где нет инкремента.</b> Чемпионы купят и без скидки (−3,0), спящие не реагируют на массовые акции (−5,0), в платном трафике не платим за своих же клиентов (−1,5).</li>
      <li><b>Вкладываем туда, где решается повтор.</b> Вторая покупка новичков (+2,5) и возврат ценных клиентов под угрозой оттока (+2,0).</li>
      <li><b>Итог:</b> −{num(-sum(min(0, s['budget_after'] - s['budget_before']) for s in lines))} снято, +{num(sum(max(0, s['budget_after'] - s['budget_before']) for s in lines))} вложено, чистая экономия {num(T['budget_before'] - T['budget_after'])} млн ₸ = {pct(-T['budget_change'], 0)}.</li>
    </ol>
    <div class="stat-card soft"><div class="stat sm">{pct(T['crr_before'])} → {pct(T['crr_after'])}</div><p>доля маркетинга в выручке (CRR)</p></div>
  </div>
</div>"""

# ---------------------------------------------------------------- 05 каналы
kpi = {
    "champions": "Частота не ниже 0,85 заказа/мес; конверсия приглашений",
    "loyal": "Средний чек 16 000 → 16 800 ₸; частота 0,45 → 0,47",
    "potential": "Вторая покупка за 60 дней; частота 0,25 → 0,35",
    "at_risk": "Доля вернувшихся за 60 дней; частота 0,12 → 0,18",
    "hibernating": "Бюджет 6 → 1 млн ₸ при потере выручки до 1 млн ₸",
}
crow = "".join(
    f"<tr><td><b>{escape(s['name'])}</b></td><td>{escape(s['lever'])}</td>"
    f"<td>{escape(s['channels'])}</td><td>{escape(kpi[s['id']])}</td></tr>"
    for s in SEG
)
s5 = f"""
<h2 class="h"><em>Своё действие</em> для каждого сегмента</h2>
<table class="seg ch">
  <colgroup><col style="width:300px"><col style="width:560px"><col style="width:520px"><col></colgroup>
  <tr><th>Сегмент</th><th>Механика</th><th>Каналы</th><th>KPI сегмента</th></tr>
  {crow}
  <tr><td><b>Привлечение</b></td><td>{escape(ACQ['lever'])}</td><td>Performance-каналы с исключением базы, look-alike</td><td>CAC и LTV/CAC не хуже текущих; приток новых не ниже −5%</td></tr>
</table>
<p class="note wide">Общие правила: не больше двух сообщений в неделю на клиента, бесплатные каналы (push, e-mail) раньше платных (SMS, ретаргет), в каждом сегменте 10% клиентов — контрольная группа без воздействия.</p>"""

# ---------------------------------------------------------------- 06 эффект
start = T["revenue_before"]
steps = [(s["name"], s["delta"]) for s in SEG]
end = T["revenue_after"]
lo, hi = 290.0, 335.0
H = 520


def y(v: float) -> float:
    return H - (v - lo) / (hi - lo) * H


bw, gap, x0 = 140, 30, 0
svg = []
bars = [("Сейчас", start, None)] + [(n, d, "d") for n, d in steps] + [("После", end, None)]
level = start
for i, (name, v, kind) in enumerate(bars):
    x = x0 + i * (bw + gap)
    if kind is None:
        top, bottom, fill, label = y(v), y(lo), "#006A4E", num(v)
    else:
        a, b = level, level + v
        top, bottom = y(max(a, b)), y(min(a, b))
        fill = "#62CDA8" if v >= 0 else "#000000"
        label = signed(v)
        level = b
    h = max(bottom - top, 3)
    svg.append(f'<rect x="{x}" y="{top:.1f}" width="{bw}" height="{h:.1f}" rx="10" fill="{fill}"/>')
    svg.append(f'<text x="{x}" y="{top - 16:.1f}" class="wl">{label}</text>')
    words = name.split(" ")
    words = [" ".join(words[:-1]), words[-1]] if len(words) > 2 else words
    for j, w in enumerate(words):
        svg.append(f'<text x="{x}" y="{H + 46 + j * 36}" class="wn">{escape(w)}</text>')
svg_w = len(bars) * (bw + gap)
waterfall = f'<svg viewBox="0 -50 {svg_w} {H + 150}" width="100%">{"".join(svg)}</svg><p class="muted">Шкала начинается с {num(lo, 0)} млн ₸, чтобы были видны вклады сегментов</p>'

SC = M["scenarios"]
sc_names = {"pessimistic": "Пессимистичный", "base": "Базовый", "optimistic": "Оптимистичный"}
sc_cards = "".join(
    f"""<div class="sc {'on' if k == 'base' else ''}"><b>{sc_names[k]}</b>
<span class="sc-n">{pct(v['revenue_growth'], 1, True)}</span>
<span class="muted">выручка, {pct(v['share_of_uplift'], 0)} целевого эффекта</span>
<span class="muted">{signed(v['margin_effect'])} млн ₸ прибыли/мес</span></div>"""
    for k, v in SC.items()
)
s6 = f"""
<h2 class="h">Выручка: <em>{num(start)} → {num(end)}</em> млн ₸ в месяц</h2>
<div class="cols-2w">
  <div class="wf">{waterfall}</div>
  <div class="logic">
    <span class="rubric">Откуда рост</span>
    <ul class="dots">
      <li>Главный вклад — вторая покупка новичков: частота 0,25 → 0,35 даёт {signed(SEG[2]['delta'])} млн ₸</li>
      <li>Чемпионы без скидок покупают чуть реже (−1,4), но реферальная программа даёт +2,8</li>
      <li>Спящие теряют 1,0 млн ₸ выручки, зато экономят 5,0 млн ₸ бюджета</li>
    </ul>
    <div class="scs">{sc_cards}</div>
    <p class="note">Пессимистичный сценарий цели по выручке не достигает: если через 6 недель инкремент ниже половины плана, добавляем рычаги (порог доставки, подписка на расходники).</p>
  </div>
</div>"""

# ---------------------------------------------------------------- 07 метрики
s7 = f"""
<h2 class="h">Как доказать эффект: <em>инкремент</em>, а не корреляция</h2>
<div class="cols-2e">
  <div>
    <div class="ns">
      <span class="rubric">North Star</span>
      <p class="ns-t">Доля новых клиентов, сделавших вторую покупку за 60 дней</p>
      <p class="muted">Двигает её именно продукт и CRM, она опережает выручку и прямо отвечает на проблему кейса</p>
    </div>
    <table class="grid-t met">
      <tr><th>Метрика</th><th>Сейчас</th><th>Цель</th></tr>
      <tr><td>Маркетинговый бюджет, млн ₸/мес</td><td>{num(T['budget_before'])}</td><td>{num(T['budget_after'])}</td></tr>
      <tr><td>Выручка, млн ₸/мес</td><td>{num(T['revenue_before'])}</td><td>{num(T['revenue_after'])}</td></tr>
      <tr><td>Доля маркетинга в выручке (CRR)</td><td>{pct(T['crr_before'])}</td><td>{pct(T['crr_after'])}</td></tr>
      <tr><td>Выручка на 1 ₸ маркетинга</td><td>{num(T['romi_before'])} ₸</td><td>{num(T['romi_after'])} ₸</td></tr>
      <tr><td>Переход «потенциальные → лояльные» за месяц</td><td colspan="2">замерить в неделю 1–2, цель +30%</td></tr>
      <tr><td>Инкрементальная выручка к контролю</td><td>—</td><td>≥ 31 млн ₸/мес</td></tr>
    </table>
  </div>
  <div>
    <span class="rubric">Дизайн эксперимента</span>
    <ul class="dots">
      <li><b>Контроль 10% в каждом сегменте</b> — живёт по старой механике. Эффект = разница выручки на клиента «тест − контроль», умноженная на размер сегмента</li>
      <li><b>8 недель</b> и сравнение завершённых 60-дневных когорт, а не календарных месяцев</li>
      <li><b>Матрица переходов</b> между RFM-сегментами раз в месяц: кто вырос, кто скатился</li>
    </ul>
    <span class="rubric">Защитные метрики</span>
    <ul class="dots">
      <li>Валовая маржа после скидок не ниже {pct(A['gross_margin'], 0)}</li>
      <li>Отписки от рассылок не выше 0,3% на отправку, жалобы не растут</li>
      <li>Приток новых клиентов не падает больше чем на 5%</li>
      <li>Частота у чемпионов не ниже 0,85 — иначе возвращаем персональный оффер</li>
    </ul>
  </div>
</div>"""

# ---------------------------------------------------------------- 08 план
s8 = """
<h2 class="h">План на 90 дней и <em>риски</em></h2>
<div class="road">
  <div class="phase"><span class="ph-n">Недели 1–2</span><b>Данные и диагноз</b><p>RFM-скоринг базы, когорты по месяцу и каналу первой покупки, дашборд метрик, замер базовых значений вместо допущений</p></div>
  <div class="phase"><span class="ph-n">Недели 3–4</span><b>Быстрая экономия</b><p>Снять общие скидки чемпионам, исключить спящих и текущих клиентов из платного трафика, запустить цепочку второй покупки</p></div>
  <div class="phase"><span class="ph-n">Недели 5–8</span><b>Рост повтора</b><p>Win-back для «под угрозой», кросс-селл лояльным, тесты офферов, еженедельный разбор метрик</p></div>
  <div class="phase"><span class="ph-n">Недели 9–12</span><b>Масштаб</b><p>Оставить механики с доказанным инкрементом, отключить остальные, закрепить новый бюджет</p></div>
</div>
<table class="seg risk">
  <colgroup><col style="width:640px"><col></colgroup>
  <tr><th>Риск</th><th>Как управляем</th></tr>
  <tr><td>Чемпионы уйдут без скидок</td><td>Контрольная группа и стоп-правило: если частота падает больше чем на 5%, возвращаем персональный оффер</td></tr>
  <tr><td>Платим за покупки, которые были бы и так</td><td>Эффект считаем только к контрольной группе, без неё механика не масштабируется</td></tr>
  <tr><td>Сокращение привлечения уменьшит приток</td><td>Режем только показы своим клиентам и кампании с CAC выше LTV, приток новых — защитная метрика</td></tr>
  <tr><td>Допущения модели не совпадут с фактом</td><td>В неделю 2 подставляем реальные данные в Excel-модель и пересматриваем цели до запуска</td></tr>
</table>"""

CSS = (ROOT / "scripts" / "slides.css").read_text(encoding="utf-8")
html = f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><title>RFM-кейс · неделя 2 · уровень 3</title>
<style>{CSS}</style></head><body>
{slide(1, cover, 'cover-slide')}
{slide(2, s2)}
{slide(3, s3)}
{slide(4, s4)}
{slide(5, s5)}
{slide(6, s6)}
{slide(7, s7)}
{slide(8, s8)}
</body></html>"""
(ROOT / "build").mkdir(exist_ok=True)
(ROOT / "build" / "slides.html").write_text(html, encoding="utf-8")
print("build/slides.html written")
