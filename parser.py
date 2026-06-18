import requests
import json
import os

def transform_product(product):
    """
    Преобразует один товар: категория, цена +2000, размеры.
    """
    # Ключевые слова для категорий
    t_shirt_keywords = ["t-рубашка", "футболка", "tee", "t-shirt", "джерси"]
    hoodie_keywords = ["свитшот", "худи", "толстовка"]
    jacket_keywords = ["куртка", "пуховик", "пальто"]
    shorts_keywords = ["шорты"]

    def detect_clothing_category(name):
        name_lower = name.lower()
        for kw in t_shirt_keywords:
            if kw in name_lower:
                return "Футболки"
        for kw in hoodie_keywords:
            if kw in name_lower:
                return "Худи"
        for kw in jacket_keywords:
            if kw in name_lower:
                return "Куртки"
        for kw in shorts_keywords:
            if kw in name_lower:
                return "Шорты"
        return "Одежда"

    size_map = {
        "Кроссовки": ["36", "37", "38", "39", "40", "41", "42", "43", "44"],
        "Обувь": ["36", "37", "38", "39", "40", "41", "42", "43", "44"],
        "Футболки": ["S", "M", "L", "XL"],
        "Куртки": ["S", "M", "L", "XL"],
        "Худи": ["S", "M", "L", "XL"],
        "Штаны": ["S", "M", "L", "XL"],
        "Шорты": ["S", "M", "L", "XL"],
        "Одежда": ["S", "M", "L", "XL"],
        "Аксессуары": ["OS"],
        "Сумки": ["OS"],
        "Игрушки": ["OS"]
    }

    # Цена +2000
    if "price_rub" in product and isinstance(product["price_rub"], (int, float)):
        product["price_rub"] += 2000

    # Категория
    original_category = product.get("category", "Одежда")
    new_category = original_category
    if original_category == "Одежда":
        new_category = detect_clothing_category(product.get("name", ""))
    product["category"] = new_category

    # Размеры
    product["sizes"] = size_map.get(new_category, ["S", "M", "L", "XL"])

    return product

def main():
    local_file = "data/poizon_products_with_rub.json"
    os.makedirs("data", exist_ok=True)

    # 1. ЧИТАЕМ ЛОКАЛЬНЫЙ ФАЙЛ (ваши товары)
    print(f"📂 Читаю локальный файл: {local_file}")
    local_data = []
    if os.path.exists(local_file):
        try:
            with open(local_file, "r", encoding="utf-8") as f:
                local_data = json.load(f)
            print(f"✅ В локальном файле {len(local_data)} товаров")
        except (json.JSONDecodeError, FileNotFoundError):
            print("⚠️ Файл повреждён или пуст, начинаю с нуля")
            local_data = []
    else:
        print("⚠️ Файл не существует, создам новый")

    # 2. ЗАГРУЖАЕМ С CDN
    url = "https://cdn.jsdelivr.net/gh/Danya524/pin-up@main/poizon_products_with_rub.json"
    print(f"⬇️ Пробую загрузить CDN...")
    cdn_data = []
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        cdn_data = response.json()
        print(f"✅ С CDN загружено {len(cdn_data)} товаров")
    except Exception as e:
        print(f"⚠️ CDN недоступен: {e}")

    # 3. ДОБАВЛЯЕМ ТОЛЬКО НОВЫЕ ТОВАРЫ (по name)
    existing_names = {p.get("name") for p in local_data}
    added_count = 0
    
    for cdn_product in cdn_data:
        if cdn_product.get("name") not in existing_names:
            # Применяем преобразования к новому товару
            transformed = transform_product(cdn_product)
            local_data.append(transformed)
            existing_names.add(transformed["name"])
            added_count += 1
            print(f"➕ Новый: {transformed['name'][:80]}")

    if added_count == 0:
        print("ℹ️ Новых товаров не найдено")

    # 4. СОХРАНЯЕМ ПОЛНЫЙ ФАЙЛ
    with open(local_file, "w", encoding="utf-8") as f:
        json.dump(local_data, f, ensure_ascii=False, indent=2)

    print(f"💾 Сохранено ВСЕГО {len(local_data)} товаров (добавлено {added_count})")

if __name__ == "__main__":
    main()
