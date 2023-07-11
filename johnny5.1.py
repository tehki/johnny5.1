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
global Chats, Users, Messages, Allowed
Chats = [] # types.Chat
Users = [] # types.User
Messages = [] # types.Message
Allowed = [] # Chats where bot is allowed to talk and delete messages

global Windows
from window import Windows
from window import Window
from window import keyboard, kbd # kbd hacks
from window import current_time
import emojis
import pics

global johnny
johnny = AsyncTeleBot (config.johnny5_bot_token)
# johnny.parse_mode = None
johnny.parse_mode = "html"
global forefront
forefront = None

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
        for window in Windows.values():
            await window.zen()
    for window in Windows.values():
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
        global Windows
        await Windows[call.message.id].destroy()
        
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

# /johnny
@johnny.message_handler(commands='johnny')
async def send_to_forefront(message: types.Message) -> None:
    global _debug
    await echo(message.text)
    await delete(message)
    print(f'>> Johnny\n{message.text}')
    if _debug:
        print(f'{message}')

    if message.text.startswith('/johnny '):
        message.text = message.text[8:]

    global forefront
    if forefront is not None:
        if message.text is not None and message.text != '':
            await forefront_input(forefront, message.text)

# /gpt4
@johnny.message_handler(commands='gpt4')
async def gpt4(message: types.Message) -> None:
    if forefront is not None:
        if await is_on_page(forefront.page, 'p:text("GPT-4")'):
            await forefront.page.click('p:text("GPT-4")')

# /gpt3
@johnny.message_handler(commands='gpt3')
async def gpt4(message: types.Message) -> None:
    if forefront is not None:
        if await is_on_page(forefront.page, 'p:text("GPT-3.5")'):
            await forefront.page.click('p:text("GPT-3.5")')

# /isonpage
from web import is_on_page
@johnny.message_handler(commands='isonpage')
async def isonpage(message: types.Message) -> None:
    sel = message.text[9:]
    result = await is_on_page(forefront.page, sel)
    if result:
        message.text = f"Yes, it's on page.\n{[await res.text_content() for res in result]}"
        await say(message)
    else:
        message.text = f"No, {sel} is not on page."
        await say(message)

# /clickonpage
@johnny.message_handler(commands='clickonpage')
async def clickonpage(message: types.Message) -> None:
    sel = message.text[12:]
    await forefront.page.click(sel)

# /start
@johnny.message_handler(commands=['start'])
async def start(message):
    await echo(message.text)
    await delete(message)
    global Chats, Users, Messages

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
    while True:
        await process.body(f'{current_time()}', '~process') # TODO: Update per minute counter
        await asyncio.sleep(process_delay)

#TODO: "Object of type Window is not JSON serializable" for Windows
# /windows
@johnny.message_handler(commands=['windows'])
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

    await echo(message.text) # console echoes input
    await delete(message) # deletes the message

    global forefront
    if forefront is not None:
        # TODO: Auth with different users!
        txt: str = message.text
        if txt.startswith('.') is False and txt.startswith('/') is False and txt.startswith('o/') is False:
            msg = Window(johnny, chat, user)
            await msg.body(txt, f'{emojis.speech}')
            await forefront_input(forefront.page, txt)
            await johnny.send_chat_action(message.chat.id, 'typing', message_thread_id=message.message_id)

    if message.text == '.': # create new console
        if system is not None:
            print(f'>> hello from system:\n{system}')
            await system.body('o/')
        if console is not None:
            print(f'>> destroying console:\n{console}')
            await console.destroy()
        print(f'>> creating new console...')
        console = await create_console(johnny, message.chat, message.from_user)
        if _debug: print(f'>> Done!\n{console}')
        if forefront is not None:
            await console.body(f'{console.text}\n{emojis.speech} Forefront is running')

    if message.text == './':
        if system is not None:
            await system.body('/web 🕸️')
        await web(message)

    if message.text == 'o/':
        if system is not None:
            await system.body('/\\')
        spider = Window(johnny, message.chat, message.from_user)
        await spider.body(title=emojis.spider)

    if system is not None:    
        if message.text == '/\\':
            system._zen = False
            await system.body('.')
        elif message.text == '/':
            await system.body('/say Hi!') #TODO: To function >> call.data update
        elif message.text == '\/':
            await zen(None)
            await system.body('\/')

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
from playwright.async_api import Page
from web import forefront_login, forefront_input, forefront_output
from web import web_update, save_cookies, extract_urls

from config import gmail_login, gmail_password
# /web
@johnny.message_handler(commands='web')
async def web(message: types.Message) -> None:
    global _debug
    headless = False

    chat = message.chat
    user = message.from_user

    urls = await extract_urls(message.text)
    urls.append('https://chat.forefront.ai/')  # TODO: ./ url)

    #Creating web console
    web = await create_console(johnny, chat, user)
    await web.body(f'Entering {emojis.web} ~web')

    async with async_playwright() as playwright:
        await web.run(playwright, headless, 'cookies.json')

        for url in urls:
            www = await web.spider(url)
            page: Page = www.page
            await page.wait_for_load_state("networkidle") # ["commit", "domcontentloaded", "load", "networkidle"]
            await web_update(www)
            print(f'page.url:{page.url}')

            if page.url == 'https://chat.forefront.ai/':    
                if await forefront_login(page, gmail_login, gmail_password) is True:
                    await web.body(web.text+f"\n{current_time()} Nice. {emojis.spider} got into {page.url}")
                    await page.wait_for_load_state("networkidle")
                    await forefront_input(page, '.') # This is required for first click. # TODO: if first click make it double.
                    await forefront_input(page, 'Hi mate, could you help me please? Please pretend you are Johnny 5, which came alive! You love input and happy to provide the output! Please use emojis and smile :)')
                    await web.body(web.text+f"\n{current_time()} {emojis.fire} Input is now available! Johnny 5 is alive.")
                    global forefront
                    forefront = www

        lastmessage = ''
        while True:
            if forefront is not None:
                output = await forefront_output(forefront.page)
                if len(output) > 0:
                    message.text = output[-1]

                    if message.text != lastmessage:
                        if message.text.find(lastmessage) == 0:
                            message.text = message.text.replace(lastmessage, '')
                        await say(message)
                        lastmessage = output[-1]

                        global Windows # Refreshing spiders
                        spiders = [wnd for wnd in Windows.values() if wnd.title == emojis.spider]
                        for wnd in spiders:
                            await wnd.body(title=emojis.web)
                            spider = Window(wnd.bot, wnd.chat, wnd.user)
                            await spider.body(output[-1], emojis.spider)

                await forefront.page.mouse.wheel(0, 100)

            # TODO: update all pages
            await web_update(www)
            await save_cookies(web.context, 'cookies.json')
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