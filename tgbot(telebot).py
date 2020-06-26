import telebot
from telebot.types import Message
# import io
import transfer
from settings import TOKEN
#
style_pic = None
content_pic = None

bot = telebot.TeleBot(TOKEN)
@bot.message_handler(commands=['help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

def image(tensor):
	output = transfer.unloader(tensor.cpu().clone().squeeze(0))
	buffer = transfer.io.BytesIO()
	output.save(buffer, format="PNG")
	return (buffer.getvalue())
#
# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
# 	bot.reply_to(message, message.text)
@bot.message_handler(commands=['pic1'])
def start_pic(message: Message):
	bot.send_message(message.chat.id, "Начало")



@bot.message_handler(commands=['start'])
def start(message):
	bot.reply_to(message, "Начнем. Первая картинка")
# 	bot.register_next_step_handler(message, first_pic)
#
# def first_pic(message):
# 	global style_img
# 	style_img = image_loader(message)
# 	bot.reply_to(message, "А теперь вторую")
# 	bot.register_next_step_handler(message, second_pic)
#
# def second_pic(message):
# 	global content_img
# 	content_img = image_loader(message)
# 	bot.reply_to(message, "Отлично")
# 	bot.register_next_step_handler(message, end)

# @bot.message_handler(content_types=["photo"])
# def photo(message: Message):
# 	bot.send_message(message.chat.id, "Картинку получил")
# 	bot.send_photo(message.chat.id, message.photo)
# 	print(message.photo)

@bot.message_handler(content_types=['photo'])
def photo(message: Message):
	if message.caption == "1":
		bot.send_message(message.chat.id, "Контент есть")
		# print ('message.photo =', message.photo)

		fileID = message.photo[-1].file_id
		file_info = bot.get_file(fileID)
		global content_pic
		content_pic = bot.download_file(file_info.file_path)
		bot.send_photo(message.chat.id, content_pic, caption="Контент")

	if message.caption == "2":
		bot.send_message(message.chat.id, "Стиль")
		fileID = message.photo[-1].file_id
		file_info = bot.get_file(fileID)
		global style_pic
		style_pic = bot.download_file(file_info.file_path)
		bot.send_photo(message.chat.id, style_pic, caption="Стиль")

@bot.message_handler(commands=['go'])
def start(message: Message):
	img = transfer.start_transfer(style_img= style_pic, content_img= content_pic)
	# bot.send_photo(message.chat.id, output)
	img = img.run_style_transfer()
	img = image(img)
	# output = transfer.unloader(output.cpu().clone().squeeze(0))
	# buffer = transfer.io.BytesIO()
	# output.save(buffer, format="PNG")

	# print("imshow",transfer.imshow(output))
	# img = transfer.imshow(output)
	# print("img",img)
	bot.send_message(message.chat.id, "Готово")
	bot.send_photo(message.chat.id, img)




# bot.send_photo(message.chat.id, message.text)
	# print("message", message)
	# print ('message.photo =', message.photo)
	# fileID = message.photo[-1].file_id
	# print ('fileID =', fileID)
	# file_info = bot.get_file(fileID)
	# print( 'file.file_path =', file_info.file_path)
	# downloaded_file = bot.download_file(file_info.file_path)
	# print(type(downloaded_file))
	# with open("images.jpg", 'wb') as new_file:
	# 	new_file.write(downloaded_file)
	#

def end(message):
	output = run_style_transfer(cnn, cnn_normalization_mean, cnn_normalization_std,
                            content_img, style_img, input_img)
	bot.send_photo(output)


bot.polling(none_stop=True)