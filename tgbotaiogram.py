import io
import logging
import os
import os.path

import torch
from PIL import Image
# from settings import TOKEN
TOKEN = str(os.environ.get('TOKEN'))

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from torchvision import transforms

import transfer

device = "cpu"

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

imsize = transfer.imsize
loader = transforms.Compose([
    transforms.Resize(imsize),  # нормируем размер изображения
    transforms.CenterCrop(imsize)])  # превращаем в удобный формат

check_photo_keyboard = InlineKeyboardMarkup(  # Кнопки для проверки изображений
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="check_photo:yes"),
            InlineKeyboardButton(text="Нет", callback_data="check_photo:no"),
        ]
    ]
)

transfer_keyboard = InlineKeyboardMarkup(  # Кнопки для старта переноса
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="transfer:yes"),
            InlineKeyboardButton(text="Нет", callback_data="transfer:no"),
        ]
    ]
)

check_photo_callback = CallbackData("check_photo", "answer")
transfer_callback = CallbackData("transfer", "answer")

unloader = transforms.ToPILImage()  # тензор в кратинку


async def download_resize_image(img_path: str):
    """Рисайзим и пересохраняем изображения для экономии памяти"""
    image = Image.open(img_path)
    image = loader(image)
    image.save(img_path)
    return image


async def get_image(tensor):
    """Используяется для отправки изображений 2-ух различных типов
    (по директории или из тензора в результате преобразования"""
    if type(tensor) == torch.Tensor:
        tensor = transfer.unloader(tensor.cpu().clone().squeeze(0))
    elif type(tensor) == str:
        tensor = Image.open(tensor)
    buffer = io.BytesIO()
    tensor.save(buffer, format="PNG")
    return (buffer.getvalue())


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await bot.send_message(message.from_user.id, "Добрый день {}.\n"
                                                 "Пришлите мне 2 отдельных фотографии с подписями.\n"
                                                 "Изображение контента подпишите как 'Контент' или '1'.\n"
                                                 "Изображение стиля подпишите 'Стиль' или '2'.\n"
                                                 "В силу небольшого размера по памяти, изображения сжимаются до {}."
                           .format(message.from_user.first_name, imsize))


@dp.message_handler(content_types=["photo"])
async def download_photo(message: types.Message):
    """Скачивает присланные фото"""
    content_path = "images/content" + str(message.from_user.id) + ".jpg"
    style_path = "images/style" + str(message.from_user.id) + ".jpg"

    if str(message.caption).lower() in ["1", "контент"]:
        await message.photo[-1].download(content_path)
        await download_resize_image(content_path)
        await bot.send_message(message.from_user.id, "Контент принят")

    if str(message.caption).lower() in ["2", "стиль"]:
        await message.photo[-1].download(style_path)
        await download_resize_image(style_path)
        await bot.send_message(message.from_user.id, "Стиль принят")

    if str(message.caption).lower() not in ["1", "2", "стиль", "контент"]:
        await bot.send_message(message.from_user.id, "Что то пошло не так.\n"
                                                     "Повторите попытку.")

    elif os.path.isfile(content_path) and os.path.isfile(style_path):
        await bot.send_message(message.from_user.id, "Оба изображения успешно приняты.\n"
                                                     "Хотите их просмотреть?", reply_markup=check_photo_keyboard)


@dp.callback_query_handler(check_photo_callback.filter(answer="yes"))
async def print_photo(call: CallbackQuery):
    """Выводит фото, если нажали кнопку вывода изображений"""
    content_path = "images/content" + str(call.from_user.id) + ".jpg"
    style_path = "images/style" + str(call.from_user.id) + ".jpg"
    await call.answer(cache_time=15)
    await bot.send_photo(call.from_user.id, await get_image(content_path), caption="Контент")
    await bot.send_photo(call.from_user.id, await get_image(style_path), caption="Стиль")
    await bot.send_message(call.from_user.id, "Надеюсь всё верно.\n"
                                              "Если что то не так, перешлите другие изображения\n"
                                              "Начать перенос?", reply_markup=transfer_keyboard)


@dp.callback_query_handler(check_photo_callback.filter(answer="no"))
async def dont_print_photo(call: CallbackQuery):
    """Не согласились на проверку изображений
    Предлагает начать перенос стиля"""
    await bot.send_message(call.from_user.id, "Начать перенос стиля?", reply_markup=transfer_keyboard)


@dp.callback_query_handler(transfer_callback.filter(answer="yes"))
@dp.message_handler(commands=["го", "go", "transfer"])
async def start_transfer(message):
    """Начинает перенос стиля"""
    content_path = "images/content" + str(message.from_user.id) + ".jpg"
    style_path = "images/style" + str(message.from_user.id) + ".jpg"
    if os.path.isfile(content_path) and os.path.isfile(style_path):
        if isinstance(message, types.Message):
            user_id = str(message.from_user.id)
        elif isinstance(message, CallbackQuery):
            user_id = str(message.from_user.id)
        # user_id = str(message.from_user.id)
        img = transfer.start_transfer(style_img=style_path,
                                      content_img=content_path)
        os.remove(style_path), os.remove(content_path)
        await bot.send_message(user_id, "Начал перенос стиля. Ожидайте\n"
                                        "Процесс может занять от 3-ех до 15-ти минут.")
        img = await get_image(img.run_style_transfer())
        await bot.send_photo(user_id, img, caption="Готово")
    elif os.path.isfile(content_path):
        await bot.send_message(message.from_user.id, "Изображение стиля не найдено")
    elif os.path.isfile(style_path):
        await bot.send_message(message.from_user.id, "Изображение контента не найдено")
    else:
        await bot.send_message(message.from_user.id, "Изображения не найдены")


@dp.callback_query_handler(transfer_callback.filter(answer="no"))
async def not_start_transfer(call: CallbackQuery):
    await bot.send_message(call.from_user.id, "Ну как хотите. Я предлагал")


if __name__ == '__main__':
    executor.start_polling(dp)
