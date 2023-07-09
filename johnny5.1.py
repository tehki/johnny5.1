from web import current_time
import config

import os

from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import AdvancedCustomFilter

import asyncio
import nest_asyncio
nest_asyncio.apply()

# Debugging. Turn on/off.
global _debug
process_delay = 10
_debug = False
# 🤫
# alice.
# I'm here.
# # hiding from pepe. 
# . /\ \/ . / . o/ . /\ ./ ? . #
global Chats, Users, Messages
Chats = [] # types.Chat
Users = [] # types.User
Messages = [] # types.Message

global Windows
from window import Windows
from window import Window
from window import keyboard
from window import kbd # kbd hacks
import emojis
import pics

global johnny
johnny = AsyncTeleBot (config.johnny5_bot_token)
# johnny.parse_mode = None
johnny.parse_mode = "html"

global system, process, console # type.Window
system = None
process = None
console = None

async def echo(text):
    global console
    if console is not None:
        await console.body(text)
async def delete(message):
    global johnny
    if message is not None:
        if await johnny.delete_message(message.chat.id, message.message_id):
            message = None
async def update():
    global Windows, system
    if system._zen:
        if system.photo != None:
            await system.head(pics.zen)
        for window in Windows:
            await window.zen()
    for window in Windows:
        await window.update()

# Buttons callback
@johnny.callback_query_handler(func=lambda call: True)
async def handle_callback(call):
    global system, console, _debug
    if _debug: print(f'\n{call}')

    if call.data == '.': # call system
        if system is not None:
            await system.body('o/', keyboard=keyboard(slash=True))
        if console is not None:
            await console.body('.')

    if call.data == ('/'):
        await system.body('/say Hi!', keyboard=keyboard(web=True))
        await console.body('/')

    if call.data == '🕸️':
        await web (call.message)
        await system.body('/web 🕸️', keyboard=keyboard(arigato=True))

    if call.data == ('\/'):
        await zen(None)
        await system.body('\/')
        await console.body('\/')

    if call.data == 'o/':
        await system.body('/\\', keyboard=keyboard(arigato=True))
        await console.body('o/')
    if call.data == ('/\\'):
        await system.body('.', keyboard=keyboard(dot=True))
        await console.body('/\\')

    if call.data == '🎲':
        await roll (call.message)
        await system.body('Nice.', keyboard=keyboard(slash=True))
        await console.body('/roll')

    if call.data == ('💢'):
        console = f'💢#{call.message.id}'
        global Windows
        for wnd in Windows:
            if wnd.message.id == call.message.id:
                if wnd.destroy():
                    system.text = f'#{wnd.message.id} destroyed.'
                else:
                    system.text = f'#{wnd.message.id} is not under my power.'

# /say # TODO: Revisit kbd hacks and console superhacks
@johnny.message_handler(commands=['say'])
async def say(message):
    global _debug
    if _debug:
        print(f'{message}')

    if message.text.startswith('/say '):
        message.text = message.text[5:]

    kbdd = kbd(message.text)

    await johnny.send_message(message.chat.id, message.text, reply_markup=kbdd)
    await echo(message.text)
    await delete(message)

# /start
@johnny.message_handler(commands=['start'])
async def start(message):
    global Chats, Users, Messages, Windows

    # TODO: Needs to be done for every inc. message and command
    # Gets a chat and user.
    user = message.from_user
    chat = message.chat
    # Updates the list
    Chats.append(chat)
    Users.append(user)
    Messages.append(message)
    
    # Creates system, console and process
    global system, console, process

    system = await create_system(johnny, chat, user) # TODO: Add bot
    console = await create_console(johnny, chat, user) # TODO: or remove bot?

    process = Window(johnny, chat, user)
    process.title = '~process'
    while True:
        await process.body(f"{current_time()}") # TODO: Update per minute counter
        await asyncio.sleep(process_delay)

#TODO: "Object of type Window is not JSON serializable" for Windows
# /windows
@johnny.message_handler(commands=['windows'])
async def windows(message):
    global Windows, system
    if system is not None:
        system.text = f"Windows?"
        for wnd in Windows:
            system.text += f'\n{wnd.to_json()}'

        await system.body()
    await echo(message.text)
    await delete(message)

async def create_console(bot, chat, user):
    console = Window(bot, chat, user)
    await console.body(f'{user.username}', f'{emojis.window} ~console')
    return console

async def create_system(bot, chat, user):
    global system
    if system is not None:
        system.destroy()
    system = Window(bot, chat, user, pics.johnny)
    await system.head()
    await system.body(f'{system.first_name()}', f'{emojis.window} ~system', keyboard(hi=True))
    return system

# text
# Handle all incoming text messages
@johnny.message_handler(func=lambda message: True)
async def listen(message):
    global system, console, _debug
    if _debug: print(f'>>> {message}')
    await echo(message.text) # console echoes input

    if message.text == '.': # create new console
        if system is not None:
            print(system)
            await system.body('o/')
        if console is not None:
            await console.destroy()
        console = await create_console(johnny, message.chat, message.from_user)

    if message.text == './':
        if system is not None:
            await system.body('/web 🕸️')
        await web(message)

    if message.text == 'o/':
        if system is not None:
            await system.body('/\\')
        new = Window(johnny, message.chat, message.from_user)
        await new.body('hello? who am i?')

    if system is not None:    
        if message.text == '/\\':
            system._zen = False
            await system.body('.')
        elif message.text == '/':
            await system.body('/say Hi!') #TODO: To function >> call.data update
        elif message.text == '\/':
            await zen(None)
            await system.body('\/')
    

    await delete(message) # deletes the message

# /pictures /pics
@johnny.message_handler(commands=['pictures', 'pics'])
async def pictures(message):
    global system, _debug
    if system is not None:
        system.text = f"Pictures?"

        pictures = []
        pic_path = './pics/'
        # Iterate over all files in the folder
        for filename in os.listdir(pic_path):
            # Check if the file has a .jpg or .png extension
            if filename.endswith('.jpg') or filename.endswith('.png'):
                # Create the full file path
                file_path = os.path.join(pic_path, filename)
                pictures.append(file_path)

        for picture in pictures:
            system.text += f"\n{picture}"
        await system.body()

        if _debug:
            print(f"/pics OK? {system.text} @ system")

        await echo(message.text)
        await delete(message)
# /screens /scrns
@johnny.message_handler(commands=['screens', 'scrns'])
async def screens(message):
    global system
    if system is not None:
        system.text = f"Screens?"

        screens = []
        pic_path = './screens/'
        # Iterate over all files in the folder
        for filename in os.listdir(pic_path):
            # Check if the file has a .jpg or .png extension
            if filename.endswith('.jpg') or filename.endswith('.png'):
                # Create the full file path
                file_path = os.path.join(pic_path, filename)
                screens.append(file_path)

        for screen in screens:
            system.text += f"\n{screen}"
        await system.body()

        await echo(message.text)
        await delete(message)

# /zen
@johnny.message_handler(commands=['zen'])
async def zen(message):
    global system, console, process
    if system is not None:
        system.zen()
    if console is not None:
        console.zen()
    if process is not None:
        process.zen()

    if message is not None:
        await echo(message.text)
        await delete(message)
# /pic url
@johnny.message_handler(commands='pic')
async def pic(message):
    global system

    if system is not None:
        print(f"/pic:{message.text}")
        if message.text == '/pic':
            system.text = system.message.photo[0].file_id
            await system.body()
        else:
            url = message.text[5:]
            system.photo = url
            system.text = system.message.photo[0].file_id

            # print(f"/pic {url} head updated.\n{system.message.photo}")
            await system.head()
            await system.body()
        
    await echo(message.text)
    await delete(message)

# /system /sys
@johnny.message_handler(commands=['system', 'sys'])
async def sys(message):
    global system
    if system is not None:
        system.text = f'\nsystem:{system.to_json()}'
        system.text += f'\nphoto:{system.message.photo[0]}'
        await system.body()
    
    await echo(message.text)
    await delete(message)
# TODO: restart

# /roll 🎲
@johnny.message_handler(commands=['roll'])
async def roll(message):
    await johnny.send_dice(message.chat.id, emoji='🎲',
                  disable_notification=True) # TODO: Make close available via keyboard

# Define a message handler for dice roll messages
@johnny.message_handler(content_types=['dice'])
async def handle_dice(message):
    # Get the value of the dice roll
    dice_value = message.dice.value

    global system
    if dice_value > 3:
        system.text = f'Nice! You rolled a {dice_value}. Gamble on. 😜'
        system.keyboard = keyboard(dot=True, roll=True)
    if dice_value == 3:
        system.text = f'Alright!!! A {dice_value}! My lucky number. Hey, wanna see something?'
        system.keyboard = keyboard(dot=True, zen=True)
    if dice_value < 3:
        system.text = f"Urgh... it's a {dice_value}. Better luck next time."
        system.keyboard = keyboard(dot=True, slash=True)
    await system.body()

    await echo(dice_value)
    await johnny.delete_message(message.chat.id, message.message_id) #TODO: It was await delete(). What's the difference?

### WEB PART ###
from playwright.async_api import Playwright, async_playwright, expect

from web import extract_text, print_all
from web import send_html
from web import forefront_login, forefront_input, forefront_output
from web import web_update
from config import gmail_login, gmail_password
from playwright.async_api import Page
# /web
@johnny.message_handler(commands='web')
async def web(message: types.Message) -> None:
    global _debug
    chat = message.chat
    user = message.from_user

    #Creating web console
    web = await create_console(johnny, chat, user)
    await web.body(f'Entering {emojis.web} ~web')

    async with async_playwright() as playwright:
        await web.run(playwright)

        www = await web.spider('https://chat.forefront.ai/') # TODO: ./ url
        page: Page = web.pages[www.id]
        
        await page.wait_for_load_state("networkidle") # ["commit", "domcontentloaded", "load", "networkidle"]
        await web_update(www, page)
        print(f'page.url:{page.url}')

        if await forefront_login(page, gmail_login, gmail_password) is True:
            await web.body(web.text+f"\n{current_time()} Nice. {emojis.spider} got into {page.url}")

            # TODO: create Forefront console
            await page.wait_for_load_state("networkidle")
            await forefront_input(page, 'Hi mate, could you help me please?')
            await forefront_input(page, 'Be so kind to start every message with 🕷️ and end it with 🕷️ as well')
            output = await forefront_output(page)
            if len(output) > 0:
                message.text = output[-1]
                await say(message)

        while True:
            await web_update(www, page)
            await asyncio.sleep(process_delay)

        # ---------------------
        #await context.close()
        #await browser.close()

# sticker
# Handle all incoming stickers
@johnny.message_handler(content_types=['sticker'])
async def sticker(message):
    global system
    await system.body(message.sticker.file_id)
    await echo(message.sticker.emoji)
    await delete(message)
###
asyncio.run(johnny.infinity_polling())