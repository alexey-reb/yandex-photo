#!/usr/bin/env python3
"""
Скрипт для получения списка фото из папки Яндекс Диска
"""

import requests
import json
import os
from datetime import datetime

def get_photos_from_yadisk(yandex_token, folder_path="disk:/"):
    """
    Получает список фото из указанной папки Яндекс Диска
    Возвращает список словарей с информацией о фото
    """
    headers = {"Authorization": f"OAuth {yandex_token}"}
    base_url = "https://cloud-api.yandex.net/v1/disk/resources"
    
    photos = []
    
    try:
        # 1. Получаем список файлов в папке
        params = {"path": folder_path, "limit": 100}
        response = requests.get(
            f"{base_url}/files",
            headers=headers,
            params=params,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"Ошибка при получении файлов: {response.status_code}")
            print(response.text)
            return photos
        
        files = response.json().get("items", [])
        
        # 2. Фильтруем только изображения
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        
        for file in files:
            if any(file['name'].lower().endswith(ext) for ext in image_extensions):
                # 3. Публикуем файл (делаем доступным по ссылке)
                publish_url = f"{base_url}/publish"
                publish_params = {"path": file['path']}
                
                publish_response = requests.put(
                    publish_url,
                    headers=headers,
                    params=publish_params,
                    timeout=30
                )
                
                if publish_response.status_code in [200, 202]:
                    # 4. Получаем публичную ссылку
                    file_info = requests.get(
                        f"{base_url}?path={file['path']}",
                        headers=headers,
                        timeout=30
                    ).json()
                    
                    public_url = file_info.get("public_url")
                    
                    if public_url:
                        # Конвертируем в прямую ссылку для скачивания
                        # Яндекс Диск использует такой формат
                        file_id = public_url.split('/')[-1]
                        direct_url = f"https://downloader.disk.yandex.ru/disk/{file_id}"
                        
                        photos.append({
                            "name": file['name'],
                            "url": direct_url,
                            "preview_url": public_url,  # Для просмотра в браузере
                            "size": file.get('size', 0),
                            "modified": file.get('modified', ''),
                            "mime_type": file.get('mime_type', ''),
                            "path": file.get('path', '')
                        })
                        print(f"✓ Добавлено: {file['name']}")
        
        return photos
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return photos

def save_to_json(photos, output_file="data/photos.json"):
    """Сохраняет список фото в JSON файл"""
    data = {
        "last_updated": datetime.now().isoformat(),
        "total_photos": len(photos),
        "photos": photos
    }
    
    # Создаем директорию, если ее нет
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n✅ Сохранено {len(photos)} фото в {output_file}")
    return data

if __name__ == "__main__":
    # Получаем токен из переменных окружения
    token = os.getenv("YANDEX_TOKEN")
    
    if not token:
        print("❌ Ошибка: YANDEX_TOKEN не установлен")
        exit(1)
    
    # Укажите путь к вашей папке на Яндекс Диске
    # Пример: "disk:/Фотографии" или "disk:/test_photos"
    FOLDER_PATH = os.getenv("YANDEX_FOLDER", "disk:/")
    
    print(f"🔍 Сканируем папку: {FOLDER_PATH}")
    
    # Получаем фото
    photos_list = get_photos_from_yadisk(token, FOLDER_PATH)
    
    # Сохраняем в JSON
    if photos_list:
        save_to_json(photos_list)
    else:
        print("⚠️ Фото не найдены в указанной папке")
        # Создаем пустой файл
        save_to_json([])
