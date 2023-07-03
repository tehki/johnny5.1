import re
import config
import emojis
import telebot
from telebot import types
import functions

about_pic = "./pics/pepe.png"
about_text = "Чё, как?"

owner_chat_id = '317386736'
admin_chat_id = '2051537651'

pepe = telebot.TeleBot(config.pepe_bot_token)

# Create a button
def create_button(emoji):
    return types.InlineKeyboardButton(text=f'{emoji}', callback_data=f'{emoji}')
# Create a default keyboard
def keyboard():
    # Create an inline keyboard
    keyboard = types.InlineKeyboardMarkup()
    # Adding buttons
    roll_button = create_button(emojis.dice_emoji)
    keyboard.add(roll_button)
    return keyboard
# Buttons callback
@pepe.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == emojis.dice_emoji:
        functions.roll (pepe, call.message)

# /roll 🎲
@pepe.message_handler(commands=['roll'])
def roll(message):
    functions.roll(pepe, message)

# /start
@pepe.message_handler(commands=['start'])
def start(message):
    # Send a message with the inline keyboard
    # functions.send_pic(pepe, message.chat.id, about_pic, about_text, disable_notification=True, reply_markup=keyboard())
    pepe.send_message(owner_chat_id, f'#{message.message_id}:#{message.chat.id} /start by {message.from_user.username}' )
    
# /chatid
@pepe.message_handler(commands=['chatid'])
def send_chatid(message):
    functions.send_chatid(pepe, message)

# /sticker #chatid sticker_id
@pepe.message_handler(commands=['sticker'])
def sticker(message):

    # If sticker message has a reply - search for #chatid in a reply and send sticker back to #chatid
    if message.reply_to_message != None:
        hashtags = re.findall(r'#\w+', message.reply_to_message.text)
        for tag in hashtags:
            pepe.send_sticker(tag[1:], message.sticker.file_id)
    else:
        #Trace all incoming messages
        print(f"sticker:{message.text}")
        #Send sticker info to owner chat
        if owner_chat_id != '':
            functions.send_sticker_to_owner(pepe, message, owner_chat_id)

#/re #chatid text
@pepe.message_handler(commands=['re'])
def reply(message):
    functions.reply(pepe, message)

#/fund
@pepe.message_handler(commands=['fund'])
def fund(message):
    text_message = message.text[6:]
    pepe.send_message(config.fund13_general_chatid, text_message, disable_notification=True)

#/vojd
@pepe.message_handler(commands=['vojd'])
def vojd(message):
    text_message = message.text[6:]
    pepe.send_message(config.vojd_chatid, text_message, disable_notification=True)

#/send_to
@pepe.message_handler(commands=['send_to'])
def send_to(message):
    words = message.text.split(' ')
    cmd = words[0]
    to_chat_id = words[1]
    msg = words[2]

    pepe.send_message(to_chat_id, msg, disable_notification=True)
    print(f'{cmd}:{to_chat_id}:{msg}')

#Pepe Рере Пепе Пэпэ
@pepe.message_handler(func=lambda message: message.text.startswith('Pepe') or message.text.startswith('Рере') or message.text.startswith('Пепе') or message.text.startswith('Пэпэ'))
def welcome(message):
    pepe.reply_to(message, "А?")

# text
# Handle all incoming text messages
@pepe.message_handler(func=lambda message: True)
def listen(message):
    #Trace all incoming messages to console
    print(f"pepe:{message}")
    #Send message info to owner chat
    if owner_chat_id != '':
        functions.send_message_to_owner(pepe, message, owner_chat_id)
    if admin_chat_id != '':
        functions.send_message_to_owner(pepe, message, admin_chat_id)
        print(f'>> sent to admin\n>>\n{message.text}')

# sticker
# Handle all incoming stickers
@pepe.message_handler(content_types=['sticker'])
def handle_sticker(message):
    # If sticker message has a reply - search for #chatid in a reply and send sticker back to #chatid
    if message.reply_to_message != None:
        hashtags = re.findall(r'#\w+', message.reply_to_message.text)
        for tag in hashtags:
            pepe.send_sticker(tag[1:], message.sticker.file_id)
    else:
        #Trace all incoming messages
        print(f"sticker:{message}")
        #Send sticker info to owner chat
        if owner_chat_id != '':
            functions.send_sticker_to_owner(pepe, message, owner_chat_id)


# TODO: Send keyboard
# Start the bot
pepe.infinity_polling()