from core.handlers.helpers import difference_images, PictureItem
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import ClientSession
from validators import url as urlValidator
from saucenao_api import AIOSauceNao 
from core.settings import settings
from core.handlers.helpers import button_parser, dataPattern, requestHeader
from saucenao_api.errors import *
from bs4 import BeautifulSoup
from io import BytesIO

async def main_search(website: str, photo_url: str):
    fileUrl = "https://api.telegram.org/file/bot" + settings.tokens.bot_token + "/" + photo_url
    attachedUrls = []
    linksKeyboard = InlineKeyboardBuilder()
    match website:
        case 'saucenao':
            searchResults = await saucenao_handler(fileUrl)
        case 'ascii2d':
            searchResults = await ascii2d_handler(fileUrl)

    if searchResults:
        await button_parser(searchResults, linksKeyboard, attachedUrls)

        for item in searchResults:
            if 'title' in locals() and 'author' in locals():
                break
            if item.title != '':
                title = item.title
            if item.author != '':
                author = item.author
        if 'title' not in locals():
            title = 'Unknown'
        if 'author' not in locals():
            author = 'Unknown'

        return linksKeyboard, title, author
    else:
        return False, '404', '404'

async def ascii2d_handler(photo_url: str):
    async with ClientSession() as session:
        try:
            ascii2dResults = []
            payloadData = dataPattern
            async with session.get(photo_url) as response:
                photo_file = await response.content.read()
            payloadData.add_field('file', photo_file, content_type='image/jpg', filename='temp.jpg')

            url = "https://ascii2d.net/search/multi"
            async with session.post(url, headers=requestHeader, data=payloadData) as response:
                html = await response.text()

            soup = BeautifulSoup(html, 'html.parser')
            for item in soup.find_all('div', attrs={'class': 'row item-box'})[:5]: 
                sourceDiv = item.find_all('div', attrs={'class': 'detail-box gray-link'})
                if sourceDiv[0].text in ['', '\n']:
                    continue
                sourceLinks = sourceDiv[0].find_all('a')
                title = sourceLinks[0].get_text()
                source = sourceLinks[0]["href"]
                author = sourceLinks[1].get_text()
                img = 'https://ascii2d.net' + item.find_all('img')[0]['src']

                async with session.get(img) as response:
                    img = await response.content.read()
                    if await difference_images(photo_file, img) == False:
                        ascii2dResults.append(PictureItem(title, author, source))
            
            if not ascii2dResults:
                return False
            else:
                return ascii2dResults
        except Exception as e:
            print(f'Error via ASCII2D search - {e}')
            return False
    
async def saucenao_handler(photo_url: str):
    async with ClientSession() as session:
        async with AIOSauceNao(settings.tokens.sauce_token) as aio:
            try:
                saucenaoResults = []
                async with session.get(photo_url) as response:
                    photo_file = await response.content.read()
                results = await aio.from_file(BytesIO(photo_file))
                attachedUrls = []
                
                if results[0].similarity < 65:
                    return False
                
                for item in results:
                    if item.similarity >= 65:
                        if item.urls:
                            for url in item.urls:
                                if url not in attachedUrls:
                                    attachedUrls.append(url)
                                    saucenaoResults.append(PictureItem(item.title, item.author, url))
                        if 'source' in item.raw['data']:
                            if urlValidator(item.raw['data']['source']):
                                if item.raw['data']['source'] not in attachedUrls:
                                    attachedUrls.append(item.raw['data']['source'])
                                    saucenaoResults.append(PictureItem(item.title, item.author, item.raw['data']['source']))
                                
                return saucenaoResults
            except Exception as e:
                print(f'Error via SauceNao search - {e}')
                return False    