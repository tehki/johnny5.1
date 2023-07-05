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

class Window(types.Message):
    title = ''
    text = ''
    output = ''
    _zen = False

    def __init__(self, bot, chat, user, photo = None, keyboard = None, parse_mode = None, debug = False):
        self.loop = asyncio.get_event_loop()
        self._debug: bool = debug

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
        global Windows
        if self._debug:
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
    def body(self, text=None, title=None, keyboard=None):
        output = ''
        if not self._zen:
            if title != None:
                self.title = title
            if text != None:
                self.text = text
            if keyboard != None:
                self.keyboard = keyboard

            if self.title != None:
                output += f"<b>{self.title}</b>"
            if self.text != None:
                output += f'<code>{self.text}</code>'

            self.output = output
        else:
            self.output = None

        self.update()
    def head(self, photo=None):
        if photo != None:
            self.photo = photo
        self.upload()
    def zen(self):
        self._zen = True
        self.head()
        self.body()
    def update(self):
        update_task = self.loop.create_task(self.async_update()) 
        self.loop.run_until_complete(asyncio.gather(update_task))
    def upload(self):
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
        global system
        if self.message is not None:
            if self._debug:
                print(f'{self.message.message_id}:async_update:output({len(self.output)}):{self.output}')
            """ TODO: add more html filters
            <a href = 'http://www.example.com/'> inline URL </a>
            <a href = 'tg://user?id=123456789'> inline mention of a user</a>
            <pre> pre - formatted fixed-width code block</pre>
            """
            if self.photo is not None:
                if self._debug:
                    print(f'#message.caption:{self.message.caption}\n#self.input:{self.output}')
                if strip_html(self.message.caption) != strip_html(self.output):
                    keyboard = None if system._zen else self.keyboard
                    if (self._debug):
                        print(f'sending edit_message_caption')
                    self.message = await self.bot.edit_message_caption(self.output, self.chat.id, self.message.id, parse_mode=self.parse_mode, reply_markup=keyboard)
            elif self.output != '':
                if strip_html(self.message.text) != strip_html(self.output):
                    keyboard = None if system._zen else self.keyboard
                    if (self._debug):
                        print(f'sending edit_message_text')
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
                    self.message = await self.bot.send_photo(self.chat.id, self.pic, "Creating new avatar...", parse_mode=self.parse_mode)
            else:
                self.message = await self.bot.send_message(self.chat.id, "Creating new window...", parse_mode=self.parse_mode)
    async def async_destroy(self):
        if self.message is not None:
            await self.bot.delete_message(self.chat.id, self.message.message_id)
            self.message = None

# 🤫
# alice.
# I'm here.
# # hiding from pepe. 
# . /\ \/ . / . o/ . /\ ./ ? . #

# Debugging. Turn on/off.
global _debug
_debug = False

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
        if output.endswith('\n'):
            output = output.rstrip('\n')
        return output
    return text

async def echo(text):
    global console
    if console is not None:
        console.body(text)
async def delete(message):
    global johnny
    if message is not None:
        if await johnny.delete_message(message.chat.id, message.message_id):
            message = None

async def update(delay): # delay in seconds
    global Windows, system
    if system._zen:
        if system.photo != None: # no delay for system.head
            system.head(pics.zen) # in zen mode
        for window in Windows:
            window.zen() # no delay for window.zen() when system is in zen mode
    else:
        asyncio.sleep(delay) # for telegram windows update via send message
        for window in Windows:
            window.body()

# Keyboard hack.
def kbd(hack):
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
            console.body(keyboard=kbdd)
       
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
    global system, console
    if _debug: print(f'\n{call}')

    if call.data == '.': # call system
        if system is not None:
            system.body('o/', keyboard=keyboard(slash=True))
        if console is not None:
            console.body('.')

    if call.data == ('\/'):
        await zen(None)
        system.body('\/')
        console.body('\/')
    if call.data == 'o/':
        system.body('/\\', keyboard=keyboard(arigato=True))
        console.body('o/')
    if call.data == ('/\\'):
        system.body('.', keyboard=keyboard(dot=True))
        console.body('/\\')
    if call.data == ('/'):
        system.body('\n./\n/johnny\n/windows\n/pictures\n/pic\n/pics\n/screenshots\n/scrns\n/msg', keyboard=keyboard(roll=True))
        console.body('/')
    if call.data == '🎲':
        await roll (call.message)
        system.body('Nice.', keyboard=keyboard(slash=True))
        console.body('/roll')
    if call.data == '🕸️':
        await web (call.message)
        system.body('/web 🕸️')
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
@johnny.message_handler(commands='say')
async def say(message):
    if _debug:
        print(f'{message}')

    if message.text.startswith('/say '):
        message.text = message.text[5:]

    kbdd = kbd(message.text)

    await johnny.send_message(message.chat.id, message.text, reply_markup=kbdd)
    await echo(message.text)
    await delete(message)

# text
# Handle all incoming text messages
###
@johnny.message_handler(func=lambda message: True)
async def listen(message):
    global system
    if _debug: print(f'>>> {message}')
    await echo(message.text) # console echoes input
    await delete(message) # deletes the message

    if message.text == '.':
        if system is not None:
            system.body('o/')
        else:
            message.text = '󠀠🗔'
            await say(message)

    if system is not None:
        if message.text == 'o/':
            system._zen = False
            system.body('/\\')
        elif message.text == '/\\':
            system.body('.')
        elif message.text == '/':
            system.body('/\n.\n/say Hi!') #TODO: To function >> call.data update
        elif message.text == '\/':
            await zen(None)
            system.body('\/')
        elif message.text == './':
            await web(message)
            system.body('/web 🕸️')
###


# /start
@johnny.message_handler(commands=['start'])
async def start(message):
    global Chats, Users, Messages, Windows
    global _debug
    #print(f'MESSAGE:\n{message}')

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

    system = Window(johnny, chat, user, pics.johnny, _debug)
    process = Window(johnny, chat, user, _debug)
    console = Window(johnny, chat, user, _debug)

    system.text = f"Hi there. I'm {system.first_name()}."
    system.keyboard = keyboard(hi=True)
    system.title = f'~system'

    console.text = f'And you are {system.user.first_name}. Am i right?'
    console.title = f'~console'

    # TODO: debug mode
    # if debug: system.title = f"#{avatar.message.id}:@{avatar.name()} {avatar.first_name()}:{avatar.chat.id}\n"
    # if debug: process.title = f"#{console.message.id}\n"
    # if debug: console.title = f"#{console.message.id}:@{console.user.username} {console.user.full_name}:{console.chat.id}\n"
    print("While TRUE: >>")
    processing_speed = 0.1 # TODO: processing slow-down for group chats
    process.title = '~process'
    while True:
        process.text = f"{time.strftime('%H:%M:%S')}"
        await update(processing_speed)

#TODO: "Object of type Window is not JSON serializable" for Windows
# /windows
@johnny.message_handler(commands=['windows'])
async def windows(message):
    global Windows, system
    if system is not None:
        system.text = f"Windows?"
        for wnd in Windows:
            system.text += f'\n{wnd.to_json()}'

        system.body()

    await echo(message.text)
    await delete(message)
# /pictures /pics
@johnny.message_handler(commands=['pictures', 'pics'])
async def pictures(message):
    global system
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
        system.body()

        if _debug:
            print(f"/pics OK? {system.text} @ system")

        await echo(message.text)
        await delete(message)
# /screenshots /scrns
@johnny.message_handler(commands=['screenshots', 'scrns'])
async def screenshots(message):
    global system
    if system is not None:
        system.text = f"Screenshots?"

        screenshots = []
        pic_path = './screenshots/'
        # Iterate over all files in the folder
        for filename in os.listdir(pic_path):
            # Check if the file has a .jpg or .png extension
            if filename.endswith('.jpg') or filename.endswith('.png'):
                # Create the full file path
                file_path = os.path.join(pic_path, filename)
                screenshots.append(file_path)

        for screenshot in screenshots:
            system.text += f"\n{screenshot}"
        system.body()

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
            system.body()
        else:
            url = message.text[5:]
            system.photo = url
            system.text = system.message.photo[0].file_id

            # print(f"/pic {url} head updated.\n{system.message.photo}")
            system.head()
            system.body()
        
    await echo(message.text)
    await delete(message)
# /johnny #TODO: Remake
@johnny.message_handler(commands=['johnny'])
async def johnny_(message):
    global system, process

    if system is not None:
        # system.photo = './pics/johnny_anime.jpg'
        # system.sticker #TODO: Stickers
        # stickers https://t.me/addstickers/parnoemoloko
        system.text = 'Yes?'
        system.head()
        system.body()
        processing_speed = 5
        new = Window(system.bot, system.chat, system.user)
        new.title = f"#{new.message.id}:@{new.name()} {new.first_name()}:{new.chat.id}\n"
        new.keyboard = keyboard(slash=True, dot=True, arigato=True)
        new.text = '/\\'
        # system = new # TODO: System reboot? Saving states.

        while True:
            time.sleep(processing_speed) # TODO: FIX HTML update timeout messages
            console.text = f"{time.strftime('%H:%M:%S')}"
            await update()

    await echo(message.text)
    await delete(message)
# /system /sys
@johnny.message_handler(commands=['system', 'sys'])
async def sys(message):
    global system
    if system is not None:

        system.text = f'\nsystem:{system.to_json()}'
        system.text += f'\nphoto:{system.message.photo[0]}'

        # system.text = f'\nmsg:{system.message.json}' # TODO: create new output window
        # await johnny.send_message(message.chat.id, system.message.json)
        system.body()
    
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
    system.body()

    await echo(dice_value)
    await johnny.delete_message(message.chat.id, message.message_id) #TODO: It was await delete(). What's the difference?

### WEB PART ###

async def scrns(message):
    screenshot_path = f'./screenshots/scrn_'
    if message is not None:
        screenshot_path += f'#{message.chat.id}.{message.message_id}.png'
    return screenshot_path

async def visiting(page, text, screenshot_path, chat_id):
    global www

    print(f'visiting:{page}:{text}:{screenshot_path}:')
    if page is not None:    
        await page.screenshot(path=screenshot_path)
        with open(screenshot_path, 'rb') as photo:
            await www.head(photo)
            await www.body(screenshot_path, 'www', keyboard(close=True, zen=True))
            # await johnny.send_photo(chat_id, photo, f'{text} @ {screenshot_path}')

async def till_load_and_screenshot(page, message):
    page.wait_for_load_state("networkidle")
    await visiting(page, page.url, await scrns(message), message.chat.id)

from playwright.async_api import Playwright, async_playwright, expect
# /web
@johnny.message_handler(commands='web')
async def web(message: types.Message) -> None:
    global system, console, process

#hack = message.text[5:] #TODO: kbd hacks

    global www, _debug
    user = message.from_user
    chat = message.chat
    www = Window(johnny, chat, user, pics.enso, keyboard(close=True), debug = _debug)
    www.body('whalecum!', 'www:', keyboard(close=True, zen=True))

    async with async_playwright() as playwright:
        #browser = playwright.chromium.launch(headless=False)
        #browser = playwright.firefox.launch(headless=False)
        browser = await playwright.webkit.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.tradingview.com/")
        await till_load_and_screenshot(page, message)

        await page.get_by_role("button", name="Open user menu").click()
        await till_load_and_screenshot(page, message)

        await page.get_by_role("menuitem", name="Sign in").click()
        await till_load_and_screenshot(page, message)
        await page.get_by_role("button", name="Email").click()
        await till_load_and_screenshot(page, message)
        await page.get_by_label("Email or Username").click()
        await till_load_and_screenshot(page, message)
        await page.get_by_label("Email or Username").fill(config.johnny5_proton_login)
        await till_load_and_screenshot(page, message)
        await page.get_by_label("Password").click()
        await till_load_and_screenshot(page, message)
        await page.get_by_label("Password").fill(config.johnny5_proton_password)
        await till_load_and_screenshot(page, message)
        await page.locator("label").filter(has_text="Remember me").locator("span").nth(1).click()
        await till_load_and_screenshot(page, message)
        await page.get_by_role("button", name="Sign in").click()
        await asyncio.sleep(5)
        await till_load_and_screenshot(page, message)
        # ---------------------
        await context.close()
        await browser.close()

# sticker
# Handle all incoming stickers
@johnny.message_handler(content_types=['sticker'])
async def sticker(message):
    global system
    system.body(message.sticker.file_id)
    await echo(message.sticker.emoji)
    await delete(message)
###
asyncio.run(johnny.infinity_polling())