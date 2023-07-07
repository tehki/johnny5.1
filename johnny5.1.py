import time
import config

import json
import re
import os
# import emojis
# import functions

from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import AdvancedCustomFilter

import asyncio

from typing import Dict, List, Optional, Union

import nest_asyncio
nest_asyncio.apply()

# Debugging. Turn on/off.
global _debug
process_delay = 10
_debug = False

# Returns a dictionary of devices to be used with `browser.new_context()` or `browser.new_page()`.
from playwright.async_api._context_manager import PlaywrightContextManager
from playwright._impl._browser_context import BrowserContext
from playwright._impl._browser_type import BrowserType
###
from web import scrns
class Window(types.Message):
    title = ''
    text = ''
    output = ''
    _zen = False

    browser: BrowserType = None
    context: BrowserContext = None
    pages = {}

    async def run(self, playwright: PlaywrightContextManager): # runs a new browser context
        chrome = playwright.chromium
        firefox = playwright.firefox
        webkit = playwright.webkit

        # iphone = playwright.devices["iPhone 6"] # TODO: to emulate different devices
        self.browser = await firefox.launch(headless=False) # TODO: implement browsers
        self.context = await self.browser.new_context() # **iphone  TODO: many different contexts with vpn
        await self.body(f'', f'{emojis.web} ~web')

    async def spider(self, url = ''): # returns window of a spider
        if self.context is not None:

            await self.body(self.text+f'\n{current_time()} {emojis.spider} sending a spider to {url}') # logging an action to web.body
            #TODO: may be a bad idea due to message size restriction. check text size of the message
            page = await self.context.new_page()
            www = Window(johnny, self.chat, self.user, pics.enso, keyboard(close=True))
            await www.body('', f'{emojis.spider} ~spider')
            self.pages[www.id] = page
            
            await page.set_viewport_size({'width': 800, 'height': 600})
            await page.goto(url)
            return www

    async def visiting(self, www, message): #TODO: Do we need message here or use self.message?
        screen_path = await scrns(message)
        print(f"VISITING www:{www}\nMESSAGE:\n{message}\nSELF.message:\n{self.message}")

        page = self.pages[www.id]
        if page is not None:
            if www is not None:
                await page.screenshot(path=screen_path)
                await www.head(screen_path)
                await www.body(f'{current_time()} {screen_path}', f'{emojis.spider} ~spider {page.url}')

    def __init__(self, bot, chat, user, photo = None, keyboard = None, parse_mode = None):
        self.id: int = None

        self.loop = asyncio.get_event_loop()

        self.bot: AsyncTeleBot = bot
        self.chat: types.Chat = chat
        self.user: types.User = user
        self.message: types.Message = None
        self.parse_mode = parse_mode

        self.photo: Optional[str] = photo
        self.pic: types.InputMediaPhoto = None

        self.keyboard: Optional[types.ReplyKeyboardMarkup] = keyboard
        self.create()

        global Windows
        Windows.append(self)

    def name(self):
        return self.message.from_user.full_name
    def first_name(self):
        return self.message.from_user.first_name
    def create(self):
        create_task = self.loop.create_task(self.async_create())
        self.loop.run_until_complete(asyncio.gather(create_task))
    def destroy(self): # TODO: Test
        success = False
        global Windows, _debug
        if _debug:
            print(f'{self.message.message_id}:destroy\nwindows:\n{Windows}')  
        # Find and remove an instance from the list
        for win in Windows:
            if win.message.id == self.message.message_id:
                destroy_task = self.loop.create_task(self.async_destroy())
                self.loop.run_until_complete(asyncio.gather(destroy_task))
                Windows.remove(win)
                success = True
                break
        return success   
    async def body(self, text=None, title=None, keyboard=None):
        output = ''
        
        if not self._zen:
            if title != None:
                self.title = title
            if text != None:
                self.text = text
            if keyboard != None:
                self.keyboard = keyboard
            if self.title != None:
                output += f"<b>{self.title}</b>\n"
            if self.text != None:
                output += f'<code>{self.text}</code>'
            self.output = output
        else:
            self.output = None

        await self.update()

    async def head(self, photo=None):
        if photo != None:
            self.photo = photo
        await self.upload()

    async def zen(self):
        self._zen = True
        await self.head()
        await self.body()

    async def update(self):
        update_task = self.loop.create_task(self.async_update())
        self.loop.run_until_complete(asyncio.gather(update_task))

    async def upload(self):
        upload_task = self.loop.create_task(self.async_upload()) 
        self.loop.run_until_complete(asyncio.gather(upload_task))

    def to_json(self):
        return json.dumps(self.to_dict())
    def to_dict(self):
        return {"messageid": self.message.id,
                "user": self.user.username,
                "chatid": self.chat.id,
                "text": self.text}
    async def async_update(self):
        global _debug
        if self.message is not None:
            if _debug:
                print(f'{self.message.message_id}:async_update:output({len(self.output)}):\n{self.output}')

            if self.photo is not None:
                if strip_html(self.message.caption) != strip_html(self.output):
                    keyboard = None if self._zen else self.keyboard
                    # if _debug: print(f'UPDATING:\n{self.output}')
                    self.message = await self.bot.edit_message_caption(self.output, self.chat.id, self.message.id, parse_mode=self.parse_mode, reply_markup=keyboard)
            elif self.output != '':
                if strip_html(self.message.text) != strip_html(self.output):
                    keyboard = None if self._zen else self.keyboard
                    # if _debug: print(f'UPDATING:\n{self.output}')
                    self.message = await self.bot.edit_message_text(self.output, self.chat.id, self.message.message_id, parse_mode=self.parse_mode, reply_markup=keyboard)

    async def async_upload(self):
        if self.message is not None:
            if self.photo is not None: #TODO: Check content-types
                if isinstance(self.photo, str):
                    if self.photo.startswith('./'): #local file
                        with open(self.photo, 'rb') as photo:
                            self.pic = types.InputMediaPhoto(photo)
                            self.message = await self.bot.edit_message_media(self.pic, self.chat.id, self.message.id)
                    elif self.photo.startswith('https://') or self.photo.startswith('http://'): #url
                        self.pic = types.InputMediaPhoto(self.photo)
                        self.message = await self.bot.edit_message_media(self.pic, self.chat.id, self.message.id)
                    else: #fileid?
                        self.pic = types.InputMediaPhoto(self.photo)
                        self.message = await self.bot.edit_message_media(self.pic, self.chat.id, self.message.id)
                else: # TODO: ?
                    self.message = await self.bot.edit_message_media(photo, self.message.chat.id, self.message.message_id) 
    async def async_create(self):
        if self.message is None:
            if self.photo is not None:
                with open(self.photo, 'rb') as photo:
                    self.pic = photo
                    self.message = await self.bot.send_photo(self.chat.id, self.pic, emojis.window, parse_mode=self.parse_mode)
            else:
                self.message = await self.bot.send_message(self.chat.id, emojis.window, parse_mode=self.parse_mode)
        if self.message is not None:
            self.id = self.message.message_id

    async def async_destroy(self):
        if self.message is not None:
            await self.bot.delete_message(self.chat.id, self.message.message_id)
            self.message = None
        if self.browser is not None: # TODO: Many browsers and contextes
            await self.browser.close()
            self.context = None
            self.browser = None

# 🤫
# alice.
# I'm here.
# # hiding from pepe. 
# . /\ \/ . / . o/ . /\ ./ ? . #

global johnny
johnny = AsyncTeleBot (config.johnny5_bot_token)
# johnny.parse_mode = None
johnny.parse_mode = "html"

global system, process, console # type.Window
system = None
process = None
console = None

global Chats, Users, Messages, Windows
Chats = [] # types.Chat
Users = [] # types.User
Messages = [] # types.Message

Windows = [] # Window()

#TODO: check for more tags to add
""" TODO: add more html filters
            <a href = 'http://www.example.com/'> inline URL </a>
            <a href = 'tg://user?id=123456789'> inline mention of a user</a>
            <pre> pre - formatted fixed-width code block</pre>
"""

def strip_html(text):
    if text is not None and text != '':
        output = text
        output = re.sub(r'<b>', '', output)
        output = re.sub(r'</b>', '', output)
        output = re.sub(r'<i>', '', output)
        output = re.sub(r'</i>', '', output)
        output = re.sub(r'<em>', '', output)
        output = re.sub(r'</em>', '', output)
        output = re.sub(r'<pre>', '', output)
        output = re.sub(r'</pre>', '', output)
        output = re.sub(r'<code>', '', output)
        output = re.sub(r'</code>', '', output)
        output = re.sub(r'<strong>', '', output)
        output = re.sub(r'</strong>', '', output)
        output = re.sub(r'\n', '', output)
        output = output.strip('\n')
        output = output.strip()

        # if _debug: print(f"output[0]:'{output[0]}' output[{len(output)}]:{output}")
        return output
    return text

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

import emojis
# Keyboard hack.
async def kbd(hack):
    dot = False
    close = False
    slash = False
    zen = False

    txt = hack
    if txt.startswith('.'):
        dot = True
    if txt[1:].startswith('.'):
        close = True
    if txt[2:].startswith('/'):
        slash=True
    if txt[3:].startswith('\\'):
        zen=True

    kbdd = keyboard(dot=dot, close=close, slash=slash, zen=zen)
    global console #console superhack ../\'
    if console is not None:
        if txt[4:].startswith("'"):
            await console.body(keyboard=kbdd)
       
    return kbdd
# Create a button
def create_button(emoji):
    return types.InlineKeyboardButton(text=f'{emoji}', callback_data=f'{emoji}')
# Create a default keyboard
def keyboard(roll=False, dot=False, hi=False, arigato=False, slash=False, close=False, zen=False, web=False):
    # Create an inline keyboard
    keyboard = types.InlineKeyboardMarkup()
    # Adding buttons
    if zen:
        keyboard.add(create_button('\/'))
    if slash:
        keyboard.add(create_button('/'))
    if hi:
        keyboard.add(create_button('o/'))
    if arigato:
        keyboard.add(create_button('/\\'))
    if dot:
        keyboard.add(create_button('.'))
    if close:
        keyboard.add(create_button('💢') )
    if roll:
        keyboard.add(create_button('🎲'))
    if web:
        keyboard.add(create_button('🕸️'))
    return keyboard
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

def current_time():
    return time.strftime('%H:%M:%S')

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

    system = await create_system(chat, user) # TODO: Add bot
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

async def create_system(chat, user):
    global system
    if system is not None:
        system.destroy()
    system = Window(johnny, chat, user, pics.johnny)
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
import pics
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
# await page.wait_for_load_state("networkidle") #TODO: look for new states 
from playwright.async_api import Playwright, async_playwright, expect
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

        www = await web.spider('https://tradingview.com/')
        www2 = await web.spider('https://chat.openai.com/')

        while True:
            await web.visiting(www, message)
            await web.visiting(www2, message)
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