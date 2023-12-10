import pics
import emojis
import json
import kbd

from telebot import types
from telebot.async_telebot import AsyncTeleBot
from typing import Dict, List, Optional, Union

from playwright.async_api._context_manager import PlaywrightContextManager
from playwright._impl._browser_context import BrowserContext
from playwright._impl._browser_type import BrowserType
from playwright.async_api import Page

from web import strip_html
from web import load_cookies
from utils import current_time

import asyncio
import nest_asyncio
nest_asyncio.apply()

# Debugging. Turn on/off.
global _debug
_debug = False
# Global Windows
global Windows
Windows = {} # { Window.id : Window() }

# Create a window
class Window(types.Message):
    title = ''
    text = ''
    output = ''
    _zen = False

    async def screen(self): # updates web page with fresh screenshot and returns a string path to screen.png of the message
        screen_path = f'./screens/'
        if self.message is not None:
            screen_path += f'#{self.message.chat.id}.{self.message.message_id}.png'
            if self.page is not None:
                await self.page.screenshot(path=screen_path)
                await self.head(screen_path)
        return screen_path
    
    async def run(self, playwright: PlaywrightContextManager, headless=True, cookie_file=''): # runs a new browser context
        chrome = playwright.chromium
        firefox = playwright.firefox
        webkit = playwright.webkit

        # iphone = playwright.devices["iPhone 6"] # TODO: to emulate different devices
        self.browser = await firefox.launch(headless=headless) # TODO: implement browsers

        vpn_config = None # TODO: VPN
        
        self.context = await self.browser.new_context(proxy=vpn_config) # **iphone  TODO: many different contexts with vpn
        await self.body(f'', f'{emojis.web} ~web')

        if cookie_file != '':
            await load_cookies(self.context, cookie_file)

    async def spider(self, url = 'google.com'): # returns window of a spider
        if self.context is not None:

            await self.body(self.text+f'\n{current_time()} {emojis.spider} sending a spider to {url}') # logging an action to web.body
            #TODO: may be a bad idea due to message size restriction. check text size of the message
            page = await self.context.new_page()
            spider = Window(self.bot, self.chat, self.user, pics.enso) # TODO: add keyboard to spider
            await spider.body('', f'{emojis.spider} ~spider')
            spider.page = page
            
            await page.set_viewport_size({'width': 800, 'height': 600})
            await page.goto(url)
            return spider
    
    def __init__(self, bot, chat, user, photo = None, keyboard = None, parse_mode = None):
        self.id: int = None
        self.loop = asyncio.get_event_loop()

        self.bot: AsyncTeleBot = bot
        self.chat: types.Chat = chat
        self.user: types.User = user
        self.message: types.Message = None
        self.parse_mode = parse_mode

        self.browser: BrowserType = None
        self.context: BrowserContext = None
        self.page: Page = None

        self.photo: Optional[str] = photo
        self.pic: types.InputMediaPhoto = None

        self.keyboard: Optional[types.ReplyKeyboardMarkup] = keyboard
        self.create()

        global Windows
        if self.id is not None:
            Windows[self.id] = self

    def name(self):
        if self.message is not None:
            return self.message.from_user.full_name

    def first_name(self):
        if self.message is not None:
            return self.message.from_user.first_name
    
    def create(self):
        create_task = self.loop.create_task(self.async_create())
        self.loop.run_until_complete(asyncio.gather(create_task))

    async def destroy(self):
        global Windows, _debug
        if _debug:
            print(f'{self.id}:destroy\nwindows:\n{Windows}')
        print(f'We are in destroy ({self.id})...')
        destroy_task = self.loop.create_task(self.async_destroy())
        self.loop.run_until_complete(asyncio.gather(destroy_task))
        return Windows.pop(self.id)

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

            try:
                # Code that might raise an exception
                # ...
                if self.photo is not None:
                    if await strip_html(self.message.caption) != await strip_html(self.output):
                        keyboard = None if self._zen else self.keyboard
                        # if _debug: print(f'UPDATING:\n{self.output}')
                        self.message = await self.bot.edit_message_caption(self.output, self.chat.id, self.message.id, parse_mode=self.parse_mode, reply_markup=keyboard)
                elif self.output != '':
                    if await strip_html(self.message.text) != await strip_html(self.output):
                        keyboard = None if self._zen else self.keyboard
                        # if _debug: print(f'UPDATING:\n{self.output}')
                        self.message = await self.bot.edit_message_text(self.output, self.chat.id, self.message.message_id, parse_mode=self.parse_mode, reply_markup=keyboard)
            except Exception as e:
                # Code to handle the exception
                # ...
                print(f'Exception in async_update: {str(e)}')

    async def async_upload(self):
        if self.message is not None:
            try:
                # Code that might raise an exception
                # ... 
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
            except Exception as e:
                # Code to handle the exception
                # ...
                print(f'Exception in async_upload: {str(e)}')

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
        print(f'>>> async_destroy()\n{self.id}')
        if self.browser is not None: # TODO: Many browsers and contextes
            print(f'>> closing browser\n{self.browser}')
            await self.browser.close()
            self.context = None
            self.browser = None
        if self.message is not None:
            print(f'>> deleting message via bot\n#{self.chat.id} : {self.message.message_id}')
            await self.bot.delete_message(self.chat.id, self.message.message_id)
            self.message = None
            print(f'>> self.message is None now.')