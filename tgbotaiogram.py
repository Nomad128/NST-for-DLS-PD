import logging
import transfer
from PIL import Image
import torchvision.transforms as transforms
import os.path
import torch
import PIL
import os
# import torch, torchvision
# import io
# from settings import TOKEN
from aiogram import Bot, Dispatcher, executor, types
# from boto.s3.connection import S3Connection

# import torchvision.transforms as transforms
# from aiogram.types import I
# from aiogram.types import Buffer

device = "cpu"

# Configure logging
logging.basicConfig(level=logging.INFO)

# TOKEN = str(S3Connection(os.environ["TOKEN"]))

# Initialize bot and dispatcher
bot = Bot(token=str("TOKEN"))
dp = Dispatcher(bot)

imsize = 181
loader = transforms.Compose([
    transforms.Resize(imsize),  # нормируем размер изображения
    transforms.CenterCrop(imsize)])  # превращаем в удобный формат


def image_loader(image_name):
    # image = Image.open(io.BytesIO(image_name))
    image = Image.open(image_name)
    image = loader(image).unsqueeze(0)
    return image.to(device, torch.float)


unloader = transforms.ToPILImage()  # тензор в кратинку


def imshow(tensor, title=None):
    image = tensor.cpu().clone()
    image = image.squeeze(0)  # функция для отрисовки изображения
    image = unloader(image)
    return image
    # plt.imshow(images)
    # if title is not None:
    #     plt.title(title)
    # plt.pause(0.001)


def image(tensor):
    if type(tensor) == torch.Tensor:
        tensor = transfer.unloader(tensor.cpu().clone().squeeze(0))
    elif type(tensor) == str:
        tensor = Image.open(tensor)
    buffer = transfer.io.BytesIO()
    tensor.save(buffer, format="PNG")
    return (buffer.getvalue())


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nНапиши мне что-нибудь!\n"
                        "3: наличие приватных изображений\n"
                        "4: общие фото\n"
                        "5: процесс с приватом\n"
                        "6: процесс с общими\n")


@dp.message_handler(content_types=["photo"])
async def get_photo(message: types.Message):
    if str(message.caption).lower() in ["1", "контент"]:
        img_path = "images/content" + str(message.from_user.id) + ".jpg"
        await message.photo[-1].download(img_path)
        # await bot.send_photo(message.from_user.id, photo=img)

    if str(message.caption).lower() in ["2", "стиль"]:
        img_path = "images/style" + str(message.from_user.id) + ".jpg"
        await message.photo[-1].download(img_path)

    if str(message.caption).lower() in ["11", "контент"]:
        img_path = "images/content.jpg"
        await message.photo[-1].download(img_path)
        # await bot.send_photo(message.from_user.id, photo=img)

    if str(message.caption).lower() in ["12", "стиль"]:
        img_path = "images/style.jpg"
        await message.photo[-1].download(img_path)


@dp.message_handler(commands=["го","go"])
async def start(message: types.Message):
    user = str(message.from_user.id)
    # print(message.from_user.id)
    # print("images/style" + str(message.from_user.id) + ".jpg")
    # print(transfer.image_loader("images/content"+str(message.from_user.id)+".jpg"))
    img = transfer.start_transfer(style_img="images/style" + user + ".jpg",
                                  content_img="images/content" + user + ".jpg")
    # print(type(img.run_style_transfer()))
    img = image(img.run_style_transfer())
    await bot.send_message(message.from_user.id, "Готово")
    await bot.send_photo(message.from_user.id, img)


# @dp.message_handler(commands=["старт"], commands_prefix="")
# async def start(message: types.Message):
#     user = str(message.from_user.id)
    # print(message.from_user.id)
    # print("images/style" + str(message.from_user.id) + ".jpg")
    # print(transfer.image_loader("images/content"+str(message.from_user.id)+".jpg"))
    # img = transfer.start_transfer(style_img="images/style.jpg",
    #                               content_img="images/content.jpg")
    # await bot.send_message(message.from_user.id, "Начал")


@dp.message_handler(content_types=["text"])
async def text(message: types.Message):
    if message.text == "3":
        style_path = "images/style" + str(message.from_user.id) + ".jpg"
        content_path = "images/content" + str(message.from_user.id) + ".jpg"
        if os.path.exists(style_path) == True and os.path.exists(content_path) == True:
            await bot.send_photo(message.from_user.id, image(style_path), caption="Стиль")
            await bot.send_photo(message.from_user.id, image(content_path), caption="Контент")
            print("3:приватные фото найдены")
        if os.path.exists(content_path) == False and os.path.exists(content_path) == False:
            await bot.send_message(message.from_user.id, "Нечего выводить")
            print("3:приватные фото не найдены")
        # await bot.send_message(message.from_user.id, "Я работаю")

    if message.text == "4":
        style_path = "images/style.jpg"
        content_path = "images/content.jpg"
        if os.path.exists(style_path) == True and os.path.exists(content_path) == True:
            await bot.send_photo(message.from_user.id, image(style_path), caption="Стиль")
            await bot.send_photo(message.from_user.id, image(content_path), caption="Контент")
            print("4:общие фото найдены")
        if os.path.exists(content_path) == False and os.path.exists(content_path) == False:
            await bot.send_message(message.from_user.id, "Нечего выводить")
            print("4:общие фото не найдены")
        # await bot.send_message(message.from_user.id, "Я работаю")

    if message.text == "5":
        user = str(message.from_user.id)
        if os.path.exists("images/style" + user + ".jpg" ) == False:
            await bot.send_message(message.from_user.id,"Не найдено")
            print("5:приват не найден")
        # print(message.from_user.id)
        # print("images/style" + str(message.from_user.id) + ".jpg")
        # print(transfer.image_loader("images/content"+str(message.from_user.id)+".jpg"))
        else:
            img = transfer.start_transfer(style_img="images/style" + user + ".jpg",
                                          content_img="images/content" + user + ".jpg")
            # print(type(img.run_style_transfer()))
            # img = image(img.run_style_transfer())
            print("5:приват найден")
            await bot.send_message(message.from_user.id, "Нашел")
        # await bot.send_message(message.from_user.id, "Конец")

    if message.text == "6":
        if os.path.exists("images/style.jpg") == True:
            img = transfer.start_transfer(style_img="images/style.jpg",
                                      content_img = "images/content.jpg")
            print("6:общие фото найдены")
            await bot.send_message(message.from_user.id, "Конец")
        else:
            print("6: общие фото не найдены")
            await bot.send_message(message.from_user.id, "Конец")

if __name__ == '__main__':
    # executor.start_polling(dp, skip_updates=True)
    executor.start_polling(dp)
