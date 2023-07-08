from telebot import types
from telebot.async_telebot import AsyncTeleBot
from typing import Dict, List, Optional, Union

from playwright.async_api._context_manager import PlaywrightContextManager
from playwright._impl._browser_context import BrowserContext
from playwright._impl._browser_type import BrowserType

import asyncio
import nest_asyncio
nest_asyncio.apply()

import time
def current_time():
    return time.strftime('%H:%M:%S')

import pics
import emojis
from web import strip_html

# Debugging. Turn on/off.
global _debug
_debug = False
# Global Windows
global Windows
Windows = [] # Window()
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
# Create a window
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

    async def spider(self, url = 'google.com'): # returns window of a spider
        if self.context is not None:

            await self.body(self.text+f'\n{current_time()} {emojis.spider} sending a spider to {url}') # logging an action to web.body
            #TODO: may be a bad idea due to message size restriction. check text size of the message
            page = await self.context.new_page()
            www = Window(self.bot, self.chat, self.user, pics.enso, keyboard(close=True))
            await www.body('', f'{emojis.spider} ~spider')
            self.pages[www.id] = page
            
            await page.set_viewport_size({'width': 800, 'height': 600})
            await page.goto(url)
            return www
    
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