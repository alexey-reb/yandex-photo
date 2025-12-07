#!/usr/bin/env python3
"""
Простой скрипт для скачивания и отображения фото
"""
import os
import json
import requests
from datetime import datetime
from pathlib import Path

def main():
    token = os.getenv("YANDEX_DISK_TOKEN")
    if not token:
        return
    
    # Настройки
    output_dir = Path("docs")
    output_dir.mkdir(exist_ok=True)
    
    # Получаем список фото
    headers = {"Authorization": f"OAuth {token}"}
    
    try:
        # Ищем в тестовых папках
        photos = []
        
        # Папка из вашего примера
        folder_path = "/Test/model_001"
        
        response = requests.get(
            "https://cloud-api.yandex.net/v1/disk/resources",
            headers=headers,
            params={
                "path": folder_path,
                "limit": 10,
                "fields": "_embedded.items.name,_embedded.items.path,_embedded.items.type,_embedded.items.mime_type"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            for item in data.get("_embedded", {}).get("items", []):
                if item.get("type") == "file" and item.get("mime_type", "").startswith("image/"):
                    
                    # Получаем прямую ссылку для скачивания
                    download_resp = requests.get(
                        "https://cloud-api.yandex.net/v1/disk/resources/download",
                        headers=headers,
                        params={"path": item["path"]}
                    )
                    
                    if download_resp.status_code == 200:
                        download_url = download_resp.json().get("href")
                        
                        # Пробуем скачать миниатюру
                        try:
                            img_response = requests.get(download_url, timeout=10)
                            if img_response.status_code == 200:
                                # Сохраняем изображение локально
                                img_name = f"photo_{len(photos)}.jpg"
                                img_path = output_dir / img_name
                                
                                with open(img_path, "wb") as f:
                                    f.write(img_response.content)
                                
                                photos.append({
                                    "name": item["name"],
                                    "local_path": img_name,
                                    "size": len(img_response.content)
                                })
                                print(f"✅ Скачано: {item['name']}")
                        except:
                            print(f"❌ Ошибка скачивания: {item['name']}")
        
        # Генерируем HTML
        generate_html_page(photos, output_dir)
        
        print(f"\n🎉 Готово! Скачано {len(photos)} фото")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def generate_html_page(photos, output_dir):
    """Создает HTML страницу с фотографиями"""
    
    # Создаем список изображений для HTML
    images_html = ""
    for photo in photos:
        images_html += f'''
        <div style="margin: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 8px;">
            <h3>{photo["name"]}</h3>
            <img src="{photo['local_path']}" 
                 alt="{photo['name']}" 
                 style="max-width: 100%; height: auto; border-radius: 4px;">
            <p>Размер: {photo['size']:,} байт</p>
        </div>
        '''
    
    html_content = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Фото с Яндекс.Диска</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f9f9f9;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .gallery {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        .photo-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
        }}
        .info {{
            margin-top: 30px;
            padding: 15px;
            background: #e8f4fd;
            border-radius: 8px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🖼️ Фотогалерея</h1>
        <p>Фото загружены с Яндекс.Диска</p>
        <p>Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
        <p>Всего фото: {len(photos)}</p>
    </div>
    
    <div class="gallery">
        {images_html if photos else '<p style="text-align: center;">Нет фотографий</p>'}
    </div>
    
    <div class="info">
        <p><strong>Как это работает:</strong></p>
        <ol>
            <li>GitHub Actions запускает скрипт</li>
            <li>Скрипт скачивает фото с Яндекс.Диска</li>
            <li>Фото сохраняются прямо в репозиторий</li>
            <li>Страница обновляется автоматически</li>
        </ol>
        <p>Для обновления фото запустите workflow вручную в разделе Actions.</p>
    </div>
</body>
</html>'''
    
    # Сохраняем HTML
    with open(output_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    main()
