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

global johnny
johnny = AsyncTeleBot (config.johnny5_bot_token)
# johnny.parse_mode = None
johnny.parse_mode = "html"

global _debug
_debug = False

global Chats, Users, Messages, Windows
global system, process, console # type.Window

system = None
process = None
console = None

Chats = [] # types.Chat
Users = [] # types.User
Messages = [] # types.Message
Windows = []

def strip_html(text):
    output = text
    output = re.sub(r'<b>', '', output)
    output = re.sub(r'</b>', '', output)
    output = re.sub(r'<i>', '', output)
    output = re.sub(r'</i>', '', output)
    output = re.sub(r'<em>', '', output)
    output = re.sub(r'</em>', '', output)
    output = re.sub(r'<code>', '', output)
    output = re.sub(r'</code>', '', output)
    output = re.sub(r'<strong>', '', output)
    output = re.sub(r'</strong>', '', output)
    if output.endswith('\n'):
        output = output.rstrip('\n')
    return output

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

async def echo(text):
    global console
    if console is not None:
        console.body(text)

async def delete(message):
    global johnny
    await johnny.delete_message(message.chat.id, message.message_id)

async def update():
    global Windows, system
    if system._zen:
        if system.photo != None:
            system.head(pics.zen)
        for window in Windows:
            window.zen()
    else:
        for window in Windows:
            window.body()

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

# /flower
@johnny.message_handler(commands='flower')
async def flower(message):
    global system
    if system is not None:
        system.photo = 'AgACAgQAAxkDAAIHimSg9Sojhox9Fz_DQmXwAyzW696AAALYsDEbj5oMUUaU-gWtgmtDAQADAgADcwADLwQ'
        system.head()
        system.text = 'Flowers are wonderful.'
        system.body()
    
    await echo(message.text)
    await delete(message)

# /pic url
@johnny.message_handler(commands='pic')
async def pic(message):
    global system

    if system is not None:
        if message.text == '/pic':
            system.text = system.message.photo[0].file_id
            system.body()
        else:
            url = message.text[5:]
            system.photo = url
            system.head()
            system.text = system.message.photo[0].file_id
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

# /message /msg
@johnny.message_handler(commands=['message', 'msg'])
async def msg(message):
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

# Define an asynchronous handler for the /start command
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
    
    system = Window(johnny, chat, user, pics.johnny, debug = _debug)
    process = Window(johnny, chat, user, debug = _debug)
    console = Window(johnny, chat, user, debug = _debug)

    system.text = "Hi there."
    system.keyboard = keyboard(hi=True)
    system.title = f'{system.first_name()}: '

    processing_speed = 0.1 # TODO: processing slow-down for group chats
    process.title = ''

    console.text = '/start'
    console.title = f'{system.user.first_name}: '

    # TODO: debug mode
    # if debug: system.title = f"#{avatar.message.id}:@{avatar.name()} {avatar.first_name()}:{avatar.chat.id}\n"
    # if debug: process.title = f"#{console.message.id}\n"
    # if debug: console.title = f"#{console.message.id}:@{console.user.username} {console.user.full_name}:{console.chat.id}\n"
    
    print("While TRUE: >>")

    while True:
        time.sleep(processing_speed)
        process.text = f"{time.strftime('%H:%M:%S')}"
        await update()

# Create a button
def create_button(emoji):
    return types.InlineKeyboardButton(text=f'{emoji}', callback_data=f'{emoji}')
# Create a default keyboard
def keyboard(roll=False, dot=False, hi=False, arigato=False, slash=False, close=False, zen=False):
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
    return keyboard
# Buttons callback
@johnny.callback_query_handler(func=lambda call: True)
async def handle_callback(call):
    global system, console

    if call.data == ('\/'):
        await zen(None)
        system.body('\/')
        console.body('\/')
    if call.data == '.':
        system.body('o/', keyboard=keyboard(slash=True))
        console.body('.')
    if call.data == 'o/':
        system.body('/\\', keyboard=keyboard(arigato=True))
        console.body('o/')
    if call.data == ('/\\'):
        system.body('.', keyboard=keyboard(dot=True))
        console.body('/\\')
    if call.data == ('/'):
        system.body('\n./\n/johnny\n/windows\n/pictures\n/pic\n/pics\n/screenshots\n/scrns\n/msg\n/flower', keyboard=keyboard(roll=True))
        console.body('/')
    if call.data == '🎲':
        await roll (call.message)
        system.body('Nice.', keyboard=keyboard(slash=True))
        console.body('/roll')
    if call.data == ('💢'):
        global Windows
        # Call debug
        print(f'\n{call}')     
        # johnny.send_message(call.chat.id, call, parse_mode=None)
        # system.text += f'\n{call.json}'
        for wnd in Windows:
            if wnd.message.id == call.message.id:
                if wnd.destroy():
                    system.text = f'#{wnd.message.id} destroyed.'
                else:
                    system.text = f'#{wnd.message.id} is not under my power.'

        console = f'💢#{call.message.id}'

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

# text
# Handle all incoming text messages
###
@johnny.message_handler(func=lambda message: True)
async def listen(message):
    global system
    
    if message.text == '.':
        system.body('o/')
    elif message.text == 'o/':
        system._zen = False
        system.body('/\\')
    elif message.text == '/\\':
        system.body('.')
    elif message.text == '/':
        system.body('\n./\n/johnny\n/windows\n/pictures\n/pic\n/msg\n/flower') #TODO: To function >> call.data update
    elif message.text == '\/':
        await zen(None)
        system.body('\/')
    
    print(f'>>> {message}')
    await echo(message.text)
    await delete(message)
###

# sticker
# Handle all incoming stickers
@johnny.message_handler(content_types=['sticker'])
async def sticker(message):
    global system
    system.body(message.sticker.file_id)
    await echo(message.sticker.emoji)
    await delete(message)
###
###

asyncio.run(johnny.infinity_polling())