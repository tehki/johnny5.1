import config
import os
import telebot
from selenium import webdriver

#telegram_bot_token = os.environ.get('sensei_bot_token')

sensei = telebot.TeleBot(config.sensei_bot_token)

photo_pic = './pics/sensei.jpg'

caption_pic = './sensei-sitting-room.jpg'
caption_text = """Даже путь в тысячу ли начинается с первого шага.\n«Дао Дэ Цзин»"""

about_pic = './pics/sensei-sitting.jpg'
about_text = """Наставник - хранитель опыта и знаний.

Помогает спекулянтам заработать себе на хлеб и колбасу,
стать профессиональным трейдером, пройти стажировку и
продвигаться далее по карьерной лестнице, достигать своих целей.

Ведёт ранги и награждения, следит за развитием карьеры.
Анализирует сделки, помогает исправлять ошибки,
Помогает вести дневник, наставляет на Путь истинный.

Независимая роль."""


#/start
@sensei.message_handler(commands=['start'])
def send_welcome(message):
    sensei.send_message(message.chat.id, "Хац!")

def send_photo(chatid, pic, caption):
    photo = open(pic, 'rb')
    # Send the photo with the text message
    sensei.send_photo(chatid, photo, caption=caption)
    # Close the photo file
    photo.close()

#/about
@sensei.message_handler(commands=['about'])
def send_welcome(message):
    chatid = message.chat.id
    send_photo(chatid, about_pic, about_text)

#/study
@sensei.message_handler(commands=['study'])
def send_welcome(message):
    chatid = message.chat.id
    send_photo(chatid, caption_pic, caption_text)

#/sensei
@sensei.message_handler(commands=['sensei'])
def send_welcome(message):
    photo = open(photo_pic, 'rb')
    caption = 'Ку!'
    # Send the photo with the text message
    sensei.send_photo(message.chat.id, photo, caption=caption)
    # Close the photo file
    photo.close()

    sensei.send_message(message.chat.id,
"""/about - обо мне
/study - начать обучение""")

#Сенсей Сатоши Satoshi Sensei
@sensei.message_handler(func=lambda message: message.text.startswith('Сенсей') or message.text.startswith('Сатоши') or message.text.startswith('Satoshi') or message.text.startswith('Sensei'))
def echo_all(message):
    send_welcome(message)
    text = message.text
    # sensei.reply_to(message, message.text, disable_notification=True, protect_content=True)

sensei.infinity_polling()