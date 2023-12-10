import os
import smtplib
from email.message import EmailMessage

from telebot.async_telebot import AsyncTeleBot
from telebot import types

import sys
import config
import emojis
import pics
import asyncio
import nest_asyncio
nest_asyncio.apply()

# Debugging. Turn on/off.
global _debug
process_delay = 10
_debug = True

global Windows
#from window import Windows
#from window import Window
#from window import keyboard, kbd # kbd hacks
#from window import current_time

global Allowed, Requests
Allowed = [] # Chats where bot is allowed to talk and delete messages
Requests = {} # Input requests from { 'chat.id' : '' }

global jewelcrafter
print('Starting up.')
jewelcrafter = AsyncTeleBot (config.jewelcrafter_bot_token)
jewelcrafter.parse_mode = "html"

global forefront, console
forefront = None
console = None

async def echo(text):
    global console
    if console is not None:
        await console.body(text)
async def delete(message):
    global jewelcrafter
    if message is not None:
        if await jewelcrafter.delete_message(message.chat.id, message.message_id):
            message = None

# Function to send email
async def send_email_with_attachments(sender_email, receiver_email, subject, body, files):
    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.set_content(body)

    for filename, file_data in files:
        msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=filename)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(config.gmail_login, config.gmail_password)
        smtp_server.send_message(msg)
        smtp_server.quit()

async def search_for_jewelry(message):
    # Path to the main folder
    main_folder = 'jewelcrafter'
    rings_list = []
    # Iterate through the ring names
    for ring_name in os.listdir(main_folder):
        ring_folder = os.path.join(main_folder, ring_name)
        if os.path.isdir(ring_folder):
            # Iterate through the sizes
            for size in os.listdir(ring_folder):
                sizes_list = []
                size_folder = os.path.join(ring_folder, size)
                if os.path.isdir(size_folder):
                    # Read the contents of the final folder
                    for file_name in os.listdir(size_folder):
                        file_path = os.path.join(size_folder, file_name)
                        if os.path.isfile(file_path):
                            with open(file_path, 'rb') as file:
                                file_name = file.name
                                file_data = file.read()
                                sizes_list.append((file_name, file_data))
                                rings_list.append((ring_name, size, file_name))
  
                # Send the contents via email
                await jewelcrafter.send_message(message.chat.id, f'НЕ Отправляю письмо... {size_folder}')

                sender_email = "ilia.gruntal@gmail.com"
                receiver_email = "finderlink.id@gmail.com"
                subject = f"Ювелирка {size_folder}"
                body = "Пожалуйста найдите файлы во вложении к письму."
                # await send_email_with_attachments(sender_email, receiver_email, subject, body, sizes_list)

                print(f'Done... {len(sizes_list)} files')
                await jewelcrafter.send_message(message.chat.id, f'Готово... {len(sizes_list)} файлов НЕ отправлено на почту {receiver_email}')

    await jewelcrafter.send_message(message.chat.id, f'Полный список файлов:\n{rings_list}')
    return rings_list

# Keyboard part.

# Create a button
def create_button(emoji):
    return types.InlineKeyboardButton(text=f'{emoji}', callback_data=f'{emoji}')

# Create a default keyboard
def keyboard(roll=False, close=False, web=False, ring=True, rings_choose=False):
    # Create an inline keyboard
    keyboard = types.InlineKeyboardMarkup()
    # Adding buttons
    if close:
        keyboard.add(create_button('💢') )
    if roll:
        keyboard.add(create_button('🎲'))
    if web:
        keyboard.add(create_button('🕸️'))
    if ring:
        keyboard.add(create_button('💍'))
    if rings_choose:
        global rings
        for ring in rings:
            keyboard.add(create_button(ring))
    return keyboard

# Buttons callback
@jewelcrafter.callback_query_handler(func=lambda call: True)
async def handle_callback(call):
    global console, _debug
    if _debug: print(f'\n{call}')
    if call.data == ('🎲'):
        await jewelcrafter.send_dice(call.message.chat.id, emoji='🎲')
    if call.data == ('💍'):
        await jewelcrafter.send_message(call.message.chat.id, 'Выберите кольцо', reply_markup=keyboard(rings_choose=True))
    if call.data == ('💢'):
        global Windows
        await Windows[call.message.id].destroy()
### end of keyboard part

# /start
@jewelcrafter.message_handler(commands=['start'])
async def start(message = None):
    await jewelcrafter.send_message(message.chat.id, 'Отправляю содержимое Ювелирки на почту')
    global rings_list
    rings_list = await search_for_jewelry(message)
    global rings
    rings = {}
    for ring in rings_list:
        if not ring[0] in rings:
            rings[ring[0]] = list(ring[1:])
        else:
            rings[ring[0]].append(ring[1:])
    await jewelcrafter.send_message(message.chat.id, f'Полный список колец (сортировка / размеры):\n{rings}')
    await jewelcrafter.send_message(message.chat.id, f'Реклама.\nСтань профессональным трейдером: http://13-трейдеров.рф/\nПолучи счёт от 25.000$ до 400.000$ для торговли на биржах США.')
    await jewelcrafter.send_message(message.chat.id, 'Проверяем клавиатуру', reply_markup=keyboard(roll=True, ring=False))
    await jewelcrafter.send_message(message.chat.id, 'Заказать кольцо', reply_markup=keyboard())

# /restart
@jewelcrafter.message_handler(commands=['restart'])
async def restart(message = None):
    os.execvp('python', ['python', sys.argv[0]])

'''
# /update
@jewelcrafter.message_handler(commands=['update'])
async def update(message = None):
    print("* Update *")
    global Windows

    if message is not None:
        await echo(message.text)
        await delete(message)
    
    for window in Windows.values():
        if window.page is None:
            await window.body()
        else:
            await window.body(f'{current_time()} {await window.screen()}', f'{emojis.spider} ~spider')

# /say # TODO: Revisit kbd hacks and console superhacks
@jewelcrafter.message_handler(commands=['say'])
async def say(message):
    global _debug
    if _debug:
        print(f'/say:\n{message}')

    if message.text.startswith('/say '):
        message.text = message.text[5:]

    kbdd = kbd(message.text)
    await jewelcrafter.send_message(message.chat.id, message.text, reply_markup=kbdd)

# /request
@jewelcrafter.message_handler(commands=['request'])
async def request(message):
    global _debug, Requests
    if _debug:
        print(f'/request:\n{message}')

    if message.text.startswith('/request '):
        message.text = message.text[9:]

    force_reply = types.ForceReply()
    await jewelcrafter.send_message(message.chat.id, message.text, reply_markup=force_reply)

    Requests[message.chat.id] = ''
    while Requests[message.chat.id] == '':
        await asyncio.sleep(1)

    return Requests[message.chat.id]

# /windows
@jewelcrafter.message_handler(commands=['windows'])
async def windows(message):
    await echo(message.text)
    await delete(message)
    global Windows, system
    if system is not None:
        system.text = f"Windows?"
        for wnd in Windows.values():
            system.text += f'\n{wnd.to_json()}'
        await system.body()
async def create_console(bot, chat, user):
    console = Window(bot, chat, user)
    await console.body(f'{emojis.user} {user.username}', f'{emojis.window} ~console')
    return console
async def create_system(bot, chat, user):
    system = Window(bot, chat, user, pics.enso)
    await system.head()
    await system.body(f'{system.first_name()}', f'{emojis.window} ~system', keyboard(web=True))
    return system

#TODO: Message on delete
#await context.close()
#await browser.close()

# text
# Handle all incoming text messages
@jewelcrafter.message_handler(func=lambda message: True)
async def listen(message):
    global console, _debug
    print(f'>>> incomming message {message.text}')
    if _debug: print(f'>>> {message}')
    user: types.User = message.from_user
    chat: types.Chat = message.chat

    global Allowed
    if chat.id not in Allowed:
        if message.text == '.':
            print(f"Now I am allowed at {chat.id}")
            Allowed.append(chat.id)
        else:
            print(f"I'm not allowed at {chat.id}")
            return
        
    global Requests
    if chat.id in Requests:
        if Requests[chat.id] == '':
            Requests[chat.id] = message.text
            print(f'Request {chat.id} is filled with {message.text}')

    await echo(message.text) # console echoes input
    await delete(message) # deletes the message

    global forefront
    if forefront is not None:
        # TODO: Auth with different users!
        txt: str = message.text
        if txt.startswith('.') is False and txt.startswith('/') is False and txt.startswith('o/') is False:
            msg = Window(jewelcrafter, chat, user)
            await msg.body(txt, f'{emojis.speech}')
            await jewelcrafter.send_chat_action(message.chat.id, 'typing', message_thread_id=message.message_id)

    if message.text == '.': # create new console
        if console is not None:
            print(f'>> destroying console:\n{console}')
            await console.destroy()
        print(f'>> creating new console...')
        console = await create_console(jewelcrafter, message.chat, message.from_user)
        if _debug: print(f'>> Done!\n{console}')
        if forefront is not None:
            await console.body(f'{console.text}\n{emojis.speech} Forefront is running')

    if message.text == 'o/':
        spider = Window(jewelcrafter, message.chat, message.from_user)
        await spider.body(title=emojis.spider)


'''
asyncio.run(jewelcrafter.infinity_polling())