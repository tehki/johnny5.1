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

global Allowed, Admins, Orders#, Requests
# Requests = {} # Input requests from { 'chat.id' : '' }

Admins = [1194526536, 317386736]
Allowed = [] # Chats where bot is allowed to talk and delete messages
Orders = {} # Order { 'id' : [ 'user', 'category', 'model', 'size', 'status' }

# Creating global bot
global jewelcrafter
# Creating global jewelry dictionary
global jewelry

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
    global jewelry
    jewelry = {}
    # Path to the main folder
    main_folder = 'jewelcrafter' 

    # Iterate through the items in jewelry to find out categories
    for category in os.listdir(main_folder):
        category_folder = os.path.join(main_folder, category)
        if os.path.isdir(category_folder):
            # Iterate through category models available
            for model in os.listdir(category_folder):
                model_folder = os.path.join(category_folder, model)
                if os.path.isdir(model_folder):
                    # Iterate through sizes of the model available
                    for size in os.listdir(model_folder):
                        size_folder = os.path.join(model_folder, size)
                        if os.path.isdir(size_folder):
                            # Read the contents of the final folder
                            for file_name in os.listdir(size_folder):
                                file_path = os.path.join(size_folder, file_name)
                                if os.path.isfile(file_path):
                                    with open(file_path, 'rb') as file:
                                        # file_data = file.read() We do not need to read file data, only name.
                                        # Here we have a final point to populate out jewelry dictionary.
                                        file_name = file.name
                                        
                                        if not category in jewelry:
                                            jewelry = {f'{category}': {f'{model}': {f'{size}': [file_name]}}}
                                        else:
                                            if not model in jewelry[f'{category}']:
                                                    jewelry[f'{category}'][f'{model}'] = {f'{size}': [file_name]}
                                            else:
                                                if not size in jewelry[f'{category}'][f'{model}']:
                                                    jewelry[f'{category}'][f'{model}'][f'{size}'] = [file_name]
                                                else:
                                                    jewelry[f'{category}'][f'{model}'][f'{size}'].append(file_name)
                                        
    return jewelry

# Keyboard part.

# Create a button
def create_button(emoji):
    return types.InlineKeyboardButton(text=f'{emoji}', callback_data=f'{emoji}')

# Create a default keyboard
def keyboard(roll=False, web=False, ring=False, category_choose=False, model_choose=False, category = '',
             size_choose=False, model = '', confirm_order = False):
    global jewelry
    # Create an inline keyboard
    keyboard = types.InlineKeyboardMarkup()
    # Adding buttons
    if roll:
        keyboard.add(create_button('🎲'))
    if web:
        keyboard.add(create_button('🕸️'))
    if category_choose:
        if len(jewelry) > 0:
            for category in jewelry:
                keyboard.add(create_button(category))
                # keyboard.add(create_button('💍')) TODO: rings
    if model_choose:
        if len(jewelry[category]) > 0:
            for model in jewelry[category]:
                keyboard.add(create_button(model))
    if size_choose:
        if len(jewelry[category][model]) > 0:
            for size in jewelry[category][model]:
                keyboard.add(create_button(size))
    if confirm_order:
        keyboard.add(create_button('✅'))
        keyboard.add(create_button('❌'))
    return keyboard

def is_float(s):
    parts = s.split('.')
    if len(parts) != 2:
        return False
    if all(part.isdigit() for part in parts):
        return True
    return False


'''        

                        
  




                print(f'Done... {len(sizes_list)} files')
                await jewelcrafter.send_message(message.chat.id, f'Готово... {len(sizes_list)} файлов НЕ отправлено на почту {receiver_email}')

        await jewelcrafter.send_message(message.chat.id, f'Полный список файлов:\n{rings_list}')
'''

# Buttons callback
@jewelcrafter.callback_query_handler(func=lambda call: True)
async def handle_callback(call):
    global console, _debug, jewelry, Orders
    if _debug: print(f'\n{call}')

    if call.data == ('✅'):
        # Отправляем заказ
        Orders[len(Orders)]['status'] = 1
        await jewelcrafter.send_message(call.message.chat.id, Orders[len(Orders)])
        await jewelcrafter.delete_message(call.message.chat.id, call.message.message_id)

        main_folder = os.path.join('jewelcrafter', Orders[len(Orders)]['category'],
                                   Orders[len(Orders)]['model'], Orders[len(Orders)]['size'])

        files = []
        if os.path.isdir(main_folder):
            # Read the contents of the final folder
            for file_name in os.listdir(main_folder):
                file_path = os.path.join(main_folder, file_name)
                if os.path.isfile(file_path):
                    with open(file_path, 'rb') as file:
                        file_name = file.name
                        file_data = file.read()
                        files.append((file_name, file_data))

        # Send the contents via email
        sender_email = config.sender_email
        receiver_email = config.receiver_email
        subject = f"Новый заказ: Ювелирка" # TODO: Change subject
        body = "Пожалуйста найдите файлы во вложении к письму."
        
        await jewelcrafter.send_message(call.message.chat.id, f'Отправляю письмо от {sender_email} к {receiver_email} с вложениями...')
        for file in files:
            await jewelcrafter.send_message(call.message.chat.id, f'{file[0]}')
        
        await send_email_with_attachments(sender_email, receiver_email, subject, body, files)
        await jewelcrafter.send_message(call.message.chat.id, f'Отправлено ✅')
        return

    if call.data == ('❌'):
        # Отменяем заказ
        Orders[len(Orders)]['status'] = -1
        await jewelcrafter.send_message(call.message.chat.id, Orders[len(Orders)])
        await jewelcrafter.delete_message(call.message.chat.id, call.message.message_id)
        return
    
    if call.data == ('🎲'):
        await jewelcrafter.send_dice(call.message.chat.id, emoji='🎲')
        await jewelcrafter.delete_message(call.message.chat.id, call.message.message_id)
        return
    
    #if call.data == ('💍'):
    if call.data in jewelry:
        # Создаём новый ордер, выбрали категорию
        # Order { 'id' : { 'user', 'category', 'model', 'size', 'status' }
        Orders[len(Orders)+1] =  { 'user': f'{call.message.chat.id}', 'category': f'{call.data}', 'status': 0 }
        print(f'\nOrders: {Orders}')

        # Выбираем модель
        await jewelcrafter.send_message(call.message.chat.id, 'Выберите модель', reply_markup=keyboard(model_choose=True, category=call.data))
        await jewelcrafter.delete_message(call.message.chat.id, call.message.message_id)
        return
    
    for category in jewelry:
        if call.data in jewelry[category]:
            # Выбрали модель, запрашиваем размер
            Orders[len(Orders)]['model'] = call.data
            print(f'\nOrders: {Orders}')
            await jewelcrafter.send_message(call.message.chat.id, 'Выберите размер', reply_markup=keyboard(size_choose=True, category=category, model=call.data))
            await jewelcrafter.delete_message(call.message.chat.id, call.message.message_id)
            return

    Orders[len(Orders)]['size'] = call.data
    print(f'\nOrders: {Orders}')
    # Выбрали размер, завершаем ордер
    await jewelcrafter.send_message(call.message.chat.id,
                                    f'{call.from_user.first_name} {call.from_user.username} {call.from_user.last_name} - {Orders[len(Orders)]["user"]}\n'
                                    f'Выбрал {Orders[len(Orders)]["category"]} > {Orders[len(Orders)]["model"]} > '
                                    f'размер {Orders[len(Orders)]["size"]} \nОтправляем заказ?', reply_markup=keyboard(confirm_order=True))
    await jewelcrafter.delete_message(call.message.chat.id, call.message.message_id)

'''
        for size in sizes:
            print(f'\nsize: {size}')
            if is_float(size) or size.isdigit():
                if not size in sizes_current:
                    sizes_current.append(size)

        print(f'\nsizes_current: {sizes_current}')

        await jewelcrafter.send_message(call.message.chat.id, f'Выберите размер', reply_markup=keyboard(rings_size_choose=True, sizes_current = sizes_current))
        await jewelcrafter.delete_message(call.message.chat.id, call.message.message_id)
'''
### end of keyboard part

# /start
@jewelcrafter.message_handler(commands=['start'])
async def start(message = None):
    global _debug, Admins
    if _debug:
        print(message)

    if message.chat.id in Admins:
        jewelry = await search_for_jewelry(message)
        # await jewelcrafter.send_message(message.chat.id, f'Полный список файлов:\n{jewelry}')
        # await jewelcrafter.send_message(message.chat.id, 'Проверяем клавиатуру', reply_markup=keyboard(roll=True, ring=False))
        # await jewelcrafter.send_message(message.chat.id, 'Отправляю содержимое Ювелирки на почту')

        # await jewelcrafter.send_message(message.chat.id, f'Реклама.\nСтань профессональным трейдером: http://13-трейдеров.рф/\nПолучи счёт от 25.000$ до 400.000$ для торговли на биржах США.')

        # await jewelcrafter.send_message(message.chat.id, f'Выберите категорию', reply_markup=keyboard(category_choose=True, jewelry=jewelry))

        await jewelcrafter.send_photo(message.chat.id, photo=open('.\pics\img-meteor.jpg', 'rb'),
                                    caption=f'Выберите категорию',  reply_markup=keyboard(category_choose=True))
    else:
        await jewelcrafter.send_message(message.chat.id, 'Проверяем клавиатуру', reply_markup=keyboard(roll=True))
        #TODO: Decline message

# /restart
@jewelcrafter.message_handler(commands=['restart'])
async def restart(message = None):
    global _debug, Admins
    if _debug:
        print(message)
    if message.chat.id in Admins:
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