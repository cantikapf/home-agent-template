import json
import asyncio
import aiohttp
import argparse
import sys

# Default keywords for Indonesian recipes
DEFAULT_KEYWORDS = ['resep', 'masak', 'menu', 'ayam', 'kue', 'food', 'cook', 'cooking', 'bikin', 'goreng', 'panggang', 'sambal']

async def fetch_title(session, url, sem, keywords):
    async with sem:
        video_id = url.rstrip('/').split('/')[-1]
        oembed_url = f'https://www.tiktok.com/oembed?url=https://www.tiktok.com/video/{video_id}'
        try:
            async with session.get(oembed_url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    title = data.get('title', '')
                    if any(keyword in title.lower() for keyword in keywords):
                        return {'url': url, 'title': title}
        except Exception:
            pass
        return None

async def main():
    parser = argparse.ArgumentParser(description='Scan TikTok data export for recipe videos.')
    parser.add_argument('--input', type=str, default='user_data_tiktok.json', help='Path to user_data_tiktok.json')
    parser.add_argument('--output', type=str, default='tiktok_recipes_found.json', help='Output JSON file')
    args = parser.parse_args()

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {args.input} tidak ditemukan.")
        print("Silakan request data TikTok Anda (JSON) dan letakkan di folder ini.")
        sys.exit(1)
    
    videos = data.get('Likes and Favorites', {}).get('Favorite Videos', {}).get('FavoriteVideoList', [])
    urls = [v.get('Link') for v in videos if v.get('Link')]
    
    if not urls:
        print("Tidak ada video favorit yang ditemukan di dalam file JSON tersebut.")
        sys.exit(0)
        
    print(f"Ditemukan {len(urls)} video Favorit. Mulai memindai judul (estimasi 1-3 menit)...")
    
    sem = asyncio.Semaphore(50)
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_title(session, url, sem, DEFAULT_KEYWORDS) for url in urls]
        results = await asyncio.gather(*tasks)
        
    valid_recipes = [r for r in results if r is not None]
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(valid_recipes, f, indent=4, ensure_ascii=False)
        
    print(f"Selesai! Ditemukan {len(valid_recipes)} video resep.")
    print(f"Data resep telah disimpan di {args.output}")
    print("Selanjutnya, jalankan: python import_tiktok_recipes.py")

if __name__ == '__main__':
    asyncio.run(main())
