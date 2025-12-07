#!/usr/bin/env python3
"""
Скрипт для получения списка фото с Яндекс.Диска
"""
import os
import json
import requests
from datetime import datetime

def get_yandex_disk_files(token, folder_path="/"):
    """Получает список файлов из указанной папки Яндекс.Диска"""
    headers = {
        "Authorization": f"OAuth {token}",
        "Accept": "application/json"
    }
    
    params = {
        "path": folder_path,
        "limit": 1000,
        "preview_size": "XXXL",  # Максимальный размер превью
        "fields": "_embedded.items.name,_embedded.items.path,_embedded.items.preview,_embedded.items.type,_embedded.items.mime_type"
    }
    
    try:
        response = requests.get(
            "https://cloud-api.yandex.net/v1/disk/resources",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        return None

def process_photos_data(raw_data):
    """Обрабатывает сырые данные и формирует структурированный список фото"""
    if not raw_data or "_embedded" not in raw_data:
        return []
    
    photos = []
    for item in raw_data["_embedded"]["items"]:
        # Фильтруем только изображения
        if item.get("type") == "file" and item.get("mime_type", "").startswith("image/"):
            photo_info = {
                "name": item["name"],
                "path": item["path"],
                "preview_url": item.get("preview", ""),
                "size": item.get("size", 0),
                "modified": item.get("modified", ""),
                "media_type": item.get("mime_type", "image/jpeg")
            }
            photos.append(photo_info)
    
    return photos

def main():
    # Получаем токен из переменных окружения
    token = os.getenv("YANDEX_DISK_TOKEN")
    if not token:
        print("Ошибка: YANDEX_DISK_TOKEN не установлен")
        return
    
    # Папки для сканирования (можно расширить список)
    folders_to_scan = ["/Test/model_001", "/Test/model_002"]
    
    all_photos = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "folders": {}
    }
    
    for folder in folders_to_scan:
        print(f"Сканирую папку: {folder}")
        raw_data = get_yandex_disk_files(token, folder)
        
        if raw_data:
            photos = process_photos_data(raw_data)
            if photos:
                folder_name = folder.strip("/") or "root"
                all_photos["folders"][folder_name] = photos
                print(f"  Найдено фото: {len(photos)}")
    
    # Сохраняем результат
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "photos.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_photos, f, ensure_ascii=False, indent=2)
    
    print(f"Данные сохранены в {output_file}")
    print(f"Всего папок: {len(all_photos['folders'])}")
    
    # Создаем сводный файл для быстрого доступа
    summary = {
        "total_folders": len(all_photos["folders"]),
        "total_photos": sum(len(photos) for photos in all_photos["folders"].values()),
        "last_updated": all_photos["last_updated"]
    }
    
    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
