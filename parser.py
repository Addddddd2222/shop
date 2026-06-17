import requests
import json
import os
from datetime import datetime

def get_cny_rate():
    try:
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=10)
        data = response.json()
        rate = data['Valute']['CNY']['Value']
        print(f"[{datetime.now()}] Курс CNY/RUB: {rate}")
        return rate
    except Exception as e:
        print(f"[{datetime.now()}] Ошибка курса: {e}")
        return 11.5

def get_products_from_poizon():
    """Пытается получить товары с Poizon (заглушка)"""
    # В реальности здесь был бы парсинг Poizon
    # Но так как Poizon блокирует запросы, используем тестовые
    return None

def get_default_products():
    """Товары по умолчанию (вы можете их менять)"""
    return [
        {'name': 'Nike Air Force 1', 'brand': 'Nike', 'price_yuan': 899, 'image': ''},
        {'name': 'Adidas Campus', 'brand': 'Adidas', 'price_yuan': 799, 'image': ''},
        {'name': 'New Balance 2002R', 'brand': 'New Balance', 'price_yuan': 1099, 'image': ''},
        {'name': 'Jordan 1 Retro', 'brand': 'Jordan', 'price_yuan': 1299, 'image': ''},
        {'name': 'Carhartt Hoodie', 'brand': 'Carhartt', 'price_yuan': 699, 'image': ''},
        {'name': 'Supreme Box Logo', 'brand': 'Supreme', 'price_yuan': 999, 'image': ''},
        {'name': 'Yeezy 350', 'brand': 'Yeezy', 'price_yuan': 1499, 'image': ''},
        {'name': 'Nike Dunk Low', 'brand': 'Nike', 'price_yuan': 1099, 'image': ''},
    ]

def update_products():
    print(f"[{datetime.now()}] Обновление товаров...")
    
    # Создаём папку data
    os.makedirs('data', exist_ok=True)
    
    # Получаем товары
    products = get_default_products()
    
    # Получаем курс
    rate = get_cny_rate()
    markup = 1.3
    
    # Пересчитываем цены
    for p in products:
        if p.get('price_yuan'):
            p['price_rub'] = round(p['price_yuan'] * rate * markup, 2)
            print(f"  {p['brand']} {p['name']}: {p['price_rub']} ₽")
    
    # Сохраняем в файл
    with open('data/poizon_products_with_rub.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"[{datetime.now()}] ✅ Сохранено {len(products)} товаров")

if __name__ == "__main__":
    update_products()
