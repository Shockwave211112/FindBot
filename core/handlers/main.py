from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.settings import settings
from core.handlers.helpers import button_parser, Ascii2dCallbackData, ascii2d_keyboard
from core.handlers.searches import main_search

router = Router()

@router.message(F.text == "/start", F.chat.type == "private")
async def get_start(message: Message, bot: Bot):
    await message.answer(f'Пришли картинку, я попробую найти оригинал и автора')
    
@router.message(F.photo, F.chat.type == "private")
async def get_photo(message: Message, bot: Bot):
    file = await bot.get_file(message.photo[-1].file_id)
    # searchResultsKeyboard, title, author = await main_search('saucenao', file.file_path)
    searchResultsKeyboard = 0
    if searchResultsKeyboard:
        answer = "<b>Название: </b>" + title + "\n<b>Автор: </b>" + author + "\n"
        answer += "\n<i>Если нету того, что нужно, попробуй вручную:</i>\n<b>saucenao.com | ascii2d.net | images.google.ru | yandex.ru/images/</b>"
        await message.reply(answer, 
                            reply_markup=searchResultsKeyboard.as_markup(), 
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview = True)
    else:
        await message.reply('Поиск по <b>SauceNao</b> ничего не дал.\nПопробовать <b>ASCII2D</b>?\n\n<i>Нужно будет немного подождать.</i>', 
                            parse_mode=ParseMode.HTML,
                            reply_markup=ascii2d_keyboard(file.file_path),
                            resize_keyboard=True)

@router.callback_query(Ascii2dCallbackData.filter(F.action == 'start_ascii2d_search'))    
async def ascii2d_search(callback: CallbackQuery, callback_data: Ascii2dCallbackData):
    answer = "<b><i>Минутку...</i></b>"
    await callback.message.edit_text(answer,
                            parse_mode=ParseMode.HTML, 
                            disable_web_page_preview = True)
    searchResultsKeyboard, title, author = await main_search('ascii2d', callback_data.file_path)
    if searchResultsKeyboard:
        answer = "<b>Название: </b>" + title + "\n<b>Автор: </b>" + author + "\n"
        answer += "\n<i>Если нету того, что нужно, попробуй вручную:</i>\n<b>saucenao.com | ascii2d.net | images.google.ru | yandex.ru/images/</b>"
        
        await callback.message.edit_text(answer,
                            reply_markup=searchResultsKeyboard.as_markup(), 
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview = True)
    else:
        answer = "К сожалению, ничего не найдено 😞\n\nМожешь попробовать сам на сайтах:\n<b>saucenao.com | ascii2d.net | images.google.ru | yandex.ru/images/</b>"
        await callback.message.edit_text(answer,
                                parse_mode=ParseMode.HTML, 
                                disable_web_page_preview = True)
      
@router.callback_query(Ascii2dCallbackData.filter(F.action == 'cancel_ascii2d_search'))    
async def ascii2d_search(callback: CallbackQuery):
    answer = "К сожалению, ничего не найдено 😞\n\nМожешь попробовать сам на сайтах:\n<b>saucenao.com | ascii2d.net | images.google.ru | yandex.ru/images/</b>"
    await callback.message.edit_text(answer,
                            parse_mode=ParseMode.HTML, 
                            disable_web_page_preview = True)
    
@router.message(F.chat.type == "private")         
async def get_anything(message: Message, bot: Bot):
    await message.answer(f'Такие сообщения я не понимаю.')

async def get_group_message(message: Message, bot: Bot):
    await message.answer(f'-')