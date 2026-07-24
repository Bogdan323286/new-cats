import requests
import os
from datetime import datetime

# === Ваш токен Яндекс.Диска (уже вставлен) ===
YANDEX_TOKEN = "y0__wgBENrModsDGNuWAyCaqI-1GBcUQutyxFlEp8DRH6TISOrP5H5q"

class YandexDiskClient:
    BASE_URL = 'https://cloud-api.yandex.net/v1/disk/'

    def __init__(self, token):
        self.token = token
        self.headers = {'Authorization': f'OAuth {token}'}

    def create_folder(self, path):
        url = self.BASE_URL + 'resources'
        params = {'path': path}
        response = requests.put(url, headers=self.headers, params=params)
        if response.status_code == 201:
            print(f'✅ Папка "{path}" создана.')
            return True
        elif response.status_code == 409:
            print(f'ℹ️ Папка "{path}" уже существует.')
            return True
        else:
            print(f'❌ Ошибка создания папки: {response.status_code}')
            return False

    def upload_file(self, disk_path, file_content):
        url = self.BASE_URL + 'resources/upload'
        params = {'path': disk_path, 'overwrite': True}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code != 200:
            print(f'❌ Ошибка получения URL: {response.status_code}')
            return False
        upload_url = response.json().get('href')
        if not upload_url:
            print('❌ Не удалось получить URL для загрузки')
            return False
        response = requests.put(upload_url, data=file_content, headers={'Content-Type': 'image/jpeg'})
        if response.status_code == 201:
            print(f'✅ Файл "{disk_path}" загружен.')
            return True
        else:
            print(f'❌ Ошибка загрузки: {response.status_code}')
            return False

class CatAPI:
    BASE_URL = 'https://cataas.com/cat/says/'

    @staticmethod
    def get_cat_image(text, width=400, height=500, color='white', size=20):
        url = f"{CatAPI.BASE_URL}{text}?width={width}&height={height}&color={color}&size={size}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.content
            else:
                print(f'⚠️ Ошибка получения картинки: {response.status_code}')
                return None
        except requests.exceptions.RequestException as e:
            print(f'⚠️ Ошибка сети: {e}')
            return None

def main():
    print("🐱 === Резервное копирование картинок с котами ===")
    text = input('Введите текст для изображений (например, "кот"): ').strip()
    if not text:
        text = 'кот'
        print(f'ℹ️ Используем текст по умолчанию: "{text}"')

    disk = YandexDiskClient(YANDEX_TOKEN)
    cat_api = CatAPI()

    folder_name = 'котики'
    if not disk.create_folder(folder_name):
        print('❌ Не удалось создать папку, завершаем.')
        return

    print('\n📸 Начинаем загрузку 10 картинок...')
    success_count = 0
    for i in range(1, 11):
        print(f'\n--- Картинка #{i} ---')
        img_data = cat_api.get_cat_image(text)
        if img_data:
            disk_path = f'{folder_name}/{i}.jpg'
            if disk.upload_file(disk_path, img_data):
                success_count += 1
        else:
            print(f'⚠️ Пропускаем картинку #{i} из-за ошибки')

    print(f'\n📊 Загружено {success_count} из 10 картинок в папку "{folder_name}".')
    if success_count == 10:
        print('🎉 Все картинки успешно загружены!')
    else:
        print('⚠️ Некоторые картинки не загружены.')

if __name__ == '__main__':
    main()