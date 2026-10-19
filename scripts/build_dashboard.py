"""Собирает dashboard/index.html: шаблон + данные (dashboard/data.json) + источники (dashboard/sources.html)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "dashboard"

# Читаемые вымышленные названия поставщиков (в данных — технические «Учебный-N»).
NAMES = {
    "молочная продукция": "Сүт Дала",
    "мясо и птица": "Ет Базар",
    "напитки": "Bulaq Drinks",
    "бакалея": "Астық Бакалея",
    "овощи и фрукты": "Жасыл Бақша",
    "бытовая химия": "Таза Үй",
    "хлеб и выпечка": "Нан Үйі",
    "детские товары": "Балапан Kids",
}

data = json.loads((D / "data.json").read_text(encoding="utf-8"))
for d in data["distributors"]:
    d["name"] = NAMES.get(d["category"].lower(), d["name"]) + " (вымышл.)"

# ---- достраиваем историю: январь 2024 — октябрь 2025 (рандомизация, seed 7)
import math, random
rng = random.Random(7)
OFF, N = 22, 34  # индекс ноября 2025 в шкале янв-2024..окт-2026


def poisson(lam):
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= L:
            return k
        k += 1


def month_idx(date):
    y, m = int(date[:4]), int(date[5:7])
    return (y - 2024) * 12 + m - 1


def date_in(i):
    y, m = 2024 + i // 12, i % 12 + 1
    return f"{y}-{m:02d}-{rng.randint(1, 28):02d}"


growth = lambda i: 0.5 + 0.5 * i / 21  # бизнес рос: в начале 2024 частота ниже
customers = data["customers"]
for c in customers:
    m = [0] * OFF + c["monthly"]
    fi = month_idx(c["first_order"])
    span = max(1, N - fi)
    rate = c["orders"] / span
    if fi <= OFF + 1 and c["orders"] >= 3 and rng.random() < 0.75:
        join = rng.randint(0, 21)
        for i in range(join, OFF):
            m[i] = poisson(rate * growth(i))
        m[join] = max(1, m[join])
        c["first_order"] = date_in(join)
    c["monthly"] = m
    c["orders"] = sum(m)

templates = list(customers)
for k in range(700):  # клиенты, которые ушли до ноября 2025
    t = rng.choice(templates)
    join = rng.randint(0, 18)
    end = min(OFF - 1, join + rng.randint(1, 9))
    rate = rng.uniform(0.3, 1.6)
    m = [0] * N
    for i in range(join, end + 1):
        m[i] = poisson(rate * growth(i))
    m[join] = max(1, m[join])
    last = max(i for i, v in enumerate(m) if v)
    customers.append({**t, "id": f"C{2401 + k:04d}", "monthly": m, "orders": sum(m),
                      "first_order": date_in(join), "last_order": date_in(last)})
data["meta"]["note"] += "; история 2024–2025 достроена рандомизацией (seed 7)"
data["meta"]["start"] = "2024-01"

sources_file = D / "sources.html"
sources = sources_file.read_text(encoding="utf-8") if sources_file.exists() else "<p class='muted'>Открытые источники не найдены.</p>"

html = (D / "template.html").read_text(encoding="utf-8")
html = html.replace("/*DATA*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
html = html.replace("/*SOURCES*/null", json.dumps(sources, ensure_ascii=False).replace("</", "<\\/"))
(D / "index.html").write_text(html, encoding="utf-8")
print(f"dashboard/index.html: {len(html.encode()) / 1024:.0f} KB")
