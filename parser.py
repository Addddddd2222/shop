import json
import os

def update_products():
    print("Обновление товаров...")
    os.makedirs('data', exist_ok=True)
    
    test_products = [
        {"name": "Nike Air Force 1", "brand": "Nike", "price_rub": 11990, "image": ""},
        {"name": "Adidas Campus", "brand": "Adidas", "price_rub": 10990, "image": ""},
        {"name": "New Balance 2002R", "brand": "New Balance", "price_rub": 14990, "image": ""},
        {"name": "Jordan 1 Retro", "brand": "Jordan", "price_rub": 17990, "image": ""}
    ]
    
    with open('data/poizon_products_with_rub.json', 'w', encoding='utf-8') as f:
        json.dump(test_products, f, ensure_ascii=False, indent=2)
    
    print("✅ Товары обновлены!")

if __name__ == "__main__":
    update_products()
