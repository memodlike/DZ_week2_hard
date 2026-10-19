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

sources_file = D / "sources.html"
sources = sources_file.read_text(encoding="utf-8") if sources_file.exists() else "<p class='muted'>Открытые источники не найдены.</p>"

html = (D / "template.html").read_text(encoding="utf-8")
html = html.replace("/*DATA*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
html = html.replace("/*SOURCES*/null", json.dumps(sources, ensure_ascii=False).replace("</", "<\\/"))
(D / "index.html").write_text(html, encoding="utf-8")
print(f"dashboard/index.html: {len(html.encode()) / 1024:.0f} KB")
