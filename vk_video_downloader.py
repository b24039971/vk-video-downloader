#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для скачивания видео из ВКонтакте и TikTok с использованием yt-dlp
Использование: python vk_video_downloader.py [url]
"""

import yt_dlp
import os
import sys
import argparse
from typing import Dict, Any

class VideoDownloader:
    def __init__(self) -> None:
        self.base_dir: str = os.path.dirname(os.path.abspath(__file__))
        self.download_dir = os.path.join(self.base_dir, 'downloads')
        self._ensure_download_dir()

    def _ensure_download_dir(self) -> None:
        """Создает папку для загрузок, если она не существует."""
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            print(f"Создана папка для загрузок: {self.download_dir}")

    def get_platform(self, url: str) -> str:
        """Определяет платформу по URL."""
        if 'vk.com' in url or 'vkontakte.ru' in url:
            return 'vk'
        elif 'tiktok.com' in url or 'vm.tiktok.com' in url or 'vt.tiktok.com' in url:
            return 'tiktok'
        else:
            return 'unknown'

    def get_opts(self, platform: str) -> Dict[str, Any]:
        """Возвращает настройки yt-dlp для конкретной платформы."""
        # Общие настройки
        opts = {
            'format': 'bestvideo[ext=mp4][height>=720][width>=1280]+bestaudio[ext=m4a]/best[ext=mp4][height>=720]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            # Сохраняем в папку downloads
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'progress_hooks': [self._progress_hook],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            },
            'prefer_free_formats': False,
            'retries': 10,
            'fragment_retries': 100,
            'continuedl': True,
            # Устранение возможных проблем с путями в Windows (ограничение длины имени файла)
            'trim_file_name': 100,
        }

        # Специфичные настройки для TikTok
        if platform == 'tiktok':
            opts.update({
                'extractor_args': {'tiktok': {'aid': '1988'}},
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Referer': 'https://www.tiktok.com/',
                }
            })
        
        return opts

    def _progress_hook(self, d: Dict[str, Any]) -> None:
        """Отображает прогресс скачивания."""
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)

            if total > 0:
                percent = (downloaded / total) * 100
                downloaded_mb = downloaded / (1024 * 1024)
                total_mb = total / (1024 * 1024)
                speed = d.get('speed', 0) or 0
                speed_mb = speed / (1024 * 1024)

                sys.stdout.write(f"\rПрогресс: {percent:.1f}% ({downloaded_mb:.1f} MB / {total_mb:.1f} MB) | Скорость: {speed_mb:.2f} MB/s")
                sys.stdout.flush()

        elif d['status'] == 'finished':
            print("\nЗагрузка завершена, обработка файла...")

    def show_info(self, url: str, platform: str) -> None:
        """Показывает информацию о видео перед загрузкой."""
        print(f"\nПолучаем информацию о видео с {platform.upper()}...")
        print("=" * 60)

        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                title = info.get('title', 'Без названия')
                # Безопасный вывод названия
                try:
                    print(f"Название: {title}")
                except UnicodeEncodeError:
                    print("Название: [Содержит спецсимволы]")

                duration = info.get('duration', 0)
                print(f"Длительность: {duration // 60} мин {duration % 60} сек")
                
                # Показ форматов (упрощенно)
                if 'formats' in info:
                    print(f"Доступно форматов: {len(info['formats'])}")
                    
        except Exception as e:
            print(f"Не удалось получить полную информацию: {e}")

    def download(self, url: str) -> bool:
        """Основной метод загрузки. Возвращает True в случае успеха."""
        if not url:
            print("Ошибка: Пустой URL")
            return False

        platform = self.get_platform(url)
        if platform == 'unknown':
            print("Ошибка: Неподдерживаемая ссылка. Используйте VK или TikTok.")
            return False

        self.show_info(url, platform)

        print("\n" + "=" * 60)
        print(f"Начинаем загрузку в папку '{os.path.basename(self.download_dir)}'...")
        print("=" * 60)

        opts = self.get_opts(platform)

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            
            print("\n" + "=" * 60)
            print("Готово! Видео успешно сохранено.")
            print(f"Папка: {self.download_dir}")
            return True

        except Exception as e:
            print(f"\nОшибка при скачивании: {e}")
            return False

def interactive_mode() -> None:
    downloader = VideoDownloader()
    
    print("=" * 60)
    print("VK & TikTok Video Downloader")
    print("=" * 60)
    print(f"Папка для сохранения: {downloader.download_dir}")

    while True:
        url = input("\nВставьте ссылку (или 'q' для выхода): ").strip()
        
        if url.lower() in ['q', 'exit', 'quit', 'выход']:
            break
            
        if not url:
            continue
            
        downloader.download(url)
        
        print("\n" + "-" * 60)

def main() -> None:
    parser = argparse.ArgumentParser(description='Скачивание видео из VK и TikTok')
    parser.add_argument('url', nargs='?', help='URL видео для скачивания')
    args = parser.parse_args()

    if args.url:
        # Режим командной строки (для одного файла)
        downloader = VideoDownloader()
        downloader.download(args.url)
    else:
        # Интерактивный режим
        try:
            interactive_mode()
        except KeyboardInterrupt:
            print("\n\nПрограмма остановлена пользователем.")

if __name__ == "__main__":
    main()
