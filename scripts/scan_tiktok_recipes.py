import json
import asyncio
import aiohttp
import re

# Keywords to filter recipe videos
RECIPE_KEYWORDS = ['resep', 'masak', 'menu', 'ayam', 'kue', 'food', 'cook', 'cooking', 'bikin', 'goreng', 'panggang', 'sambal']

async def fetch_title(session, url, sem):
    async with sem:
        video_id = url.rstrip('/').split('/')[-1]
        oembed_url = f'https://www.tiktok.com/oembed?url=https://www.tiktok.com/video/{video_id}'
        try:
            async with session.get(oembed_url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    title = data.get('title', '')
                    # check if title matches keywords
                    if any(keyword in title.lower() for keyword in RECIPE_KEYWORDS):
                        return {'url': url, 'title': title}
        except Exception as e:
            pass
        return None

async def main():
    print('Membaca file data TikTok...')
    with open('tiktok_data/user_data_tiktok.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    videos = data.get('Likes and Favorites', {}).get('Favorite Videos', {}).get('FavoriteVideoList', [])
    urls = [v.get('Link') for v in videos if v.get('Link')]
    print(f'Ditemukan {len(urls)} video Favorit. Sedang memproses (ini akan memakan waktu sekitar 1-2 menit)...')
    
    sem = asyncio.Semaphore(50) # 50 concurrent requests
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_title(session, url, sem) for url in urls]
        results = await asyncio.gather(*tasks)
        
    valid_recipes = [r for r in results if r is not None]
    
    print(f'Selesai! Ditemukan {len(valid_recipes)} video yang kemungkinan adalah resep masakan.')
    
    with open('data/tiktok_recipes_found.json', 'w', encoding='utf-8') as f:
        json.dump(valid_recipes, f, indent=4, ensure_ascii=False)
        
    print('Data resep telah disimpan di tiktok_recipes_found.json')

if __name__ == '__main__':
    asyncio.run(main())
