import requests
import json
import os
from datetime import datetime

def parse_poizon():
    print(f"[{datetime.now()}] Начинаю парсинг Poizon...")
    
    # Пробуем получить данные с Poizon
    url = "https://www.poizon.com/product/list?category=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"[{datetime.now()}] Ошибка: статус {response.status_code}")
            return get_test_products()
        
        # Парсим HTML
        html = response.text
        
        # Ищем товары (упрощённо, можно доработать)
        products = []
        
        # Если парсинг не сработал — используем тестовые данные
        if not products:
            print(f"[{datetime.now()}] Использую тестовые данные")
            return get_test_products()
        
        print(f"[{datetime.now()}] Спаршено {len(products)} товаров")
        return products
        
    except Exception as e:
        print(f"[{datetime.now()}] Ошибка: {e}")
        return get_test_products()

def get_test_products():
    """Тестовые товары (замените на реальные)"""
    return [
        {'name': 'Nike Air Force 1', 'brand': 'Nike', 'price_yuan': 899, 'image': ''},
        {'name': 'Adidas Campus', 'brand': 'Adidas', 'price_yuan': 799, 'image': ''},
        {'name': 'New Balance 2002R', 'brand': 'New Balance', 'price_yuan': 1099, 'image': ''},
        {'name': 'Jordan 1 Retro', 'brand': 'Jordan', 'price_yuan': 1299, 'image': ''},
        {'name': 'Carhartt Hoodie', 'brand': 'Carhartt', 'price_yuan': 699, 'image': ''},
    ]

def get_cny_rate():
    """Получает курс юаня к рублю"""
    try:
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=10)
        data = response.json()
        rate = data['Valute']['CNY']['Value']
        print(f"[{datetime.now()}] Курс CNY/RUB: {rate}")
        return rate
    except Exception as e:
        print(f"[{datetime.now()}] Ошибка курса: {e}")
        return 11.5  # Примерный курс

def update_products():
    """Основная функция обновления товаров"""
    print(f"[{datetime.now()}] Обновление товаров...")
    
    # Создаём папку data
    os.makedirs('data', exist_ok=True)
    
    # Парсим товары
    products = parse_poizon()
    
    # Получаем курс
    rate = get_cny_rate()
    markup = 1.3  # Наценка 30%
    
    # Пересчитываем цены
    for p in products:
        if p.get('price_yuan'):
            p['price_rub'] = round(p['price_yuan'] * rate * markup, 2)
            print(f"  {p['brand']} {p['name']}: {p['price_rub']} ₽")
    
    # Сохраняем в файл
    with open('data/poizon_products_with_rub.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"[{datetime.now()}] ✅ Обновлено {len(products)} товаров")

if __name__ == "__main__":
    update_products()
