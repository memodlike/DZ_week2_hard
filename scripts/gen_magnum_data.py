#!/usr/bin/env python3
"""Reproducible synthetic Magnum Go teaching data; no real customer records."""

import json
import math
import random
from collections import Counter
from datetime import date, timedelta
from pathlib import Path


ANALYSIS_DATE = date(2026, 10, 19)
START_DATE = date(2025, 11, 1)
CITIES = [
    "Алматы", "Астана", "Шымкент", "Караганда", "Актобе", "Атырау",
    "Павлодар", "Усть-Каменогорск",
]
CATEGORIES = [
    "молочная продукция", "мясо и птица", "напитки", "бакалея",
    "овощи и фрукты", "бытовая химия", "хлеб и выпечка", "детские товары",
]
NAMES = [
    "Айгерим", "Аружан", "Динара", "Мадина", "Алия", "Асем", "Жанар",
    "Сауле", "Гульназ", "Назерке", "Акбота", "Томирис", "Дана", "Айсулу",
    "Ерлан", "Нурлан", "Данияр", "Алихан", "Арман", "Бауыржан", "Азамат",
    "Руслан", "Аскар", "Тимур", "Мирас", "Ерасыл", "Олжас", "Санжар",
    "Анна", "Мария", "Елена", "Ольга", "Наталья", "Татьяна", "Ирина",
    "Светлана", "Екатерина", "Юлия", "Дарья", "Анастасия", "Виктория",
    "Александр", "Дмитрий", "Сергей", "Андрей", "Алексей", "Михаил",
    "Иван", "Павел", "Николай", "Владимир", "Евгений", "Максим",
]


def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))


def regular_orders():
    # Most customers buy only 1–3 times; fewer reach the middle of the tail.
    if random.random() < 0.65:
        return random.choices([1, 2, 3], weights=[55, 28, 17])[0]
    return random.choices(range(4, 25), weights=[1 / n for n in range(4, 25)])[0]


def make_customer(index, cohort, city):
    if cohort in ("september", "october"):
        month = 9 if cohort == "september" else 10
        first = random_date(date(2026, month, 1), date(2026, month, 19))
        # Deliberate fall in observed repeats for the two newest cohorts.
        repeat_probability = 0.12 if month == 9 else 0.05
        orders = random.choices([2, 3], weights=[85, 15])[0] if (
            random.random() < repeat_probability
        ) else 1
        last = random_date(first + timedelta(days=1), ANALYSIS_DATE) if (
            orders > 1 and first < ANALYSIS_DATE
        ) else first
    else:
        orders = random.randint(25, 60) if cohort == "frequent" else regular_orders()
        if cohort == "dormant":
            last = random_date(START_DATE, ANALYSIS_DATE - timedelta(days=121))
        else:
            # Single-order customers must also have joined before September.
            end = date(2026, 8, 31) if orders == 1 else ANALYSIS_DATE
            last = random_date(date(2026, 7, 1), end)
        first = last if orders == 1 else random_date(
            START_DATE, min(last, date(2026, 8, 31))
        )

    order_dates = [first] if orders == 1 else [first, last]
    order_dates.extend(random_date(first, last) for _ in range(orders - 2))
    monthly = [0] * 12
    for ordered_at in order_dates:
        monthly[(ordered_at.year - 2025) * 12 + ordered_at.month - 11] += 1

    # Rejection sampling preserves a truncated lognormal without boundary spikes.
    while True:
        avg_check = round(random.lognormvariate(math.log(14000), 0.32))
        if 8000 <= avg_check <= 25000:
            break
    category_index = random.randrange(8)
    return {
        "id": f"C{index:04d}",
        "name": f"{random.choice(NAMES)} {random.choice('АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЭЮЯ')}.",
        "city": city,
        "channel": random.choices(["Kaspi", "Приложение Magnum"], weights=[86, 14])[0],
        "first_order": first.isoformat(),
        "last_order": last.isoformat(),
        "recency_days": (ANALYSIS_DATE - last).days,
        "orders": orders,
        "revenue": orders * avg_check,
        "avg_check": avg_check,
        "top_category": CATEGORIES[category_index],
        "top_distributor": f"D{category_index + 1}",
        "monthly": monthly,
    }


def validate(data):
    customers = data["customers"]
    assert len(customers) == 2400
    assert len({c["id"] for c in customers}) == 2400
    assert len(data["distributors"]) == 8
    distributors = {d["id"]: d["category"] for d in data["distributors"]}
    for customer in customers:
        monthly = customer["monthly"]
        first = date.fromisoformat(customer["first_order"])
        last = date.fromisoformat(customer["last_order"])
        assert len(monthly) == 12 and all(type(n) is int and n >= 0 for n in monthly)
        assert 1 <= customer["orders"] == sum(monthly) <= 60
        assert 8000 <= customer["avg_check"] <= 25000
        assert customer["revenue"] == customer["orders"] * customer["avg_check"]
        assert START_DATE <= first <= last <= ANALYSIS_DATE
        assert customer["recency_days"] == (ANALYSIS_DATE - last).days >= 0
        nonzero = [i for i, count in enumerate(monthly) if count]
        assert nonzero[0] == (first.year - 2025) * 12 + first.month - 11
        assert nonzero[-1] == (last.year - 2025) * 12 + last.month - 11
        assert customer["orders"] != 1 or first == last
        assert customer["city"] in CITIES
        assert customer["channel"] in ("Kaspi", "Приложение Magnum")
        assert distributors[customer["top_distributor"]] == customer["top_category"]
    assert sum(c["recency_days"] > 120 for c in customers) == 720
    assert sum(c["orders"] >= 25 for c in customers) == 192
    repeat_rates = []
    for month in (8, 9, 10):
        cohort = [c for c in customers if c["first_order"].startswith(f"2026-{month:02d}")]
        repeat_rates.append(sum(c["orders"] > 1 for c in cohort) / len(cohort))
    assert repeat_rates[0] > repeat_rates[1] > repeat_rates[2]


def main():
    random.seed(42)
    cohorts = ["dormant"] * 720 + ["frequent"] * 192 + ["regular"] * 1008
    cohorts += ["september"] * 240 + ["october"] * 240
    random.shuffle(cohorts)
    cities = [city for city, count in zip(CITIES, [912, 648, 240, 168, 144, 120, 96, 72])
              for _ in range(count)]
    random.shuffle(cities)
    data = {
        "meta": {
            "note": "Синтетические рандомизированные данные для учебного RFM-анализа, не реальные данные Magnum или Kaspi",
            "seed": 42,
            "analysis_date": ANALYSIS_DATE.isoformat(),
            "currency": "KZT",
        },
        "cities": CITIES,
        "distributors": [
            {"id": f"D{i + 1}", "name": f"Вымышленный поставщик «Учебный-{i + 1}»",
             "category": category}
            for i, category in enumerate(CATEGORIES)
        ],
        "customers": [make_customer(i, cohort, city)
                      for i, (cohort, city) in enumerate(zip(cohorts, cities), 1)],
    }
    validate(data)
    output = Path(__file__).resolve().parents[1] / "dashboard" / "data.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert json.loads(output.read_text(encoding="utf-8")) == data
    customers = data["customers"]
    print("Проверки согласованности: OK (2400 клиентов, даты, месяцы, суммы, категории, JSON)")
    print(f"Клиенты: {len(customers):,}; заказы: {sum(c['orders'] for c in customers):,}; "
          f"выручка: {sum(c['revenue'] for c in customers):,} KZT")
    print("Города:", dict(Counter(c["city"] for c in customers)))
    print("Не покупали >120 дней: 720 (30%); 25+ заказов: 192 (8%)")
    print(f"1–3 заказа: {sum(c['orders'] <= 3 for c in customers) / len(customers):.1%}")
    for month in (8, 9, 10):
        cohort = [c for c in customers if c["first_order"].startswith(f"2026-{month:02d}")]
        repeats = sum(c["orders"] > 1 for c in cohort)
        print(f"Когорта 2026-{month:02d}: {len(cohort)} клиентов; "
              f"повторные покупки {repeats / len(cohort):.1%}")
    print("Повторы наблюдаются по 2026-10-19; октябрь неполный, сроки наблюдения когорт различаются.")
    print(f"Записан {output}")


if __name__ == "__main__":
    main()
