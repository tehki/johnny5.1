import os
import sys
import config
import emojis
import pics

from telebot import types
from telebot.async_telebot import AsyncTeleBot
import asyncio
import nest_asyncio
nest_asyncio.apply()

# Debugging. Turn on/off.
global _debug
process_delay = 10
_debug = False

global Windows
from window import Windows
from window import Window
from window import keyboard, kbd # kbd hacks
from window import current_time

async def create_console(bot, chat, user):
    console = Window(bot, chat, user)
    await console.body(f'{emojis.user} {user.username}', f'{emojis.window} ~console')
    return console

async def create_system(bot, chat, user):
    system = Window(bot, chat, user, pics.enso)
    await system.head()
    await system.body(f'{system.first_name()}', f'{emojis.window} ~system', keyboard(slash=True))
    return system

global Allowed, Requests
Allowed = [] # Chats where bot is allowed to talk and delete messages
Requests = {} # Input requests from { 'chat.id' : '' }

global sensei
print('Starting up. Hatz!')
sensei = AsyncTeleBot (config.sensei_bot_token)
sensei.parse_mode = "html"

global forefront, console
forefront = None
console = None

async def echo(text):
    global console
    if console is not None:
        await console.body(text)

async def delete(message):
    if message is not None:
        if await sensei.delete_message(message.chat.id, message.message_id):
            message = None

# /restart
@sensei.message_handler(commands=['restart'])
async def restart(message = None):
    #TODO: Auth. Users.
    os.execvp('python', ['python', sys.argv[0]])

# /update
@sensei.message_handler(commands=['update'])
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
async def say(message):
    global _debug
    if _debug:
        print(f'/say:\n{message}')

    if message.text.startswith('/say '):
        message.text = message.text[5:]

    kbdd = kbd(message.text)
    await sensei.send_message(message.chat.id, message.text, reply_markup=kbdd)

# /request
@sensei.message_handler(commands=['request'])
async def request(message):
    global _debug, Requests
    if _debug:
        print(f'/request:\n{message}')

    if message.text.startswith('/request '):
        message.text = message.text[9:]

    force_reply = types.ForceReply()
    await sensei.send_message(message.chat.id, message.text, reply_markup=force_reply)

    Requests[message.chat.id] = ''
    while Requests[message.chat.id] == '':
        await asyncio.sleep(1)

    return Requests[message.chat.id]

### WEB PART ###
from playwright.async_api import async_playwright, Page
from web import forefront_login, forefront_input, forefront_output, forefront_disable_autosave, forefront_validate, forefront_continue
from web import forefront_claude, forefront_claudeplus, forefront_gpt3, forefront_gpt4

from web import tradingview_login
from web import save_cookies, extract_urls, needs_validation
from config import johnny_proton_login, johnny_proton_password

# /web
@sensei.message_handler(commands='web')
async def web(message: types.Message) -> None:
    global _debug
    headless = True

    chat = message.chat
    user = message.from_user
    
    urls = await extract_urls(message.text)
    if not urls:
        urls.append('https://chat.forefront.ai/')
    print(f'urls:\n{urls}')

    # Creating web console
    web = await create_console(sensei, chat, user)
    await web.body(f'Entering {emojis.web} ~web')
    tasks = []

    async with async_playwright() as playwright:
        await web.run(playwright, headless, 'sensei.json')
        for url in urls:
            www = await web.spider(url)

            page: Page = www.page
            await page.wait_for_load_state("load") # ["commit", "domcontentloaded", "load", "networkidle"]

            print(f'page.url:{page.url}')
            if 'forefront.ai' in page.url:
                if await forefront_login(page, johnny_proton_login, johnny_proton_password) is False:
                    if await needs_validation(page):
                        await www.screen()
                        message.text = f'Please reply with validation code at your email {johnny_proton_login}'
                        code = await request(message)
                        if code is not None:
                            if await forefront_validate(page, code) is False:
                                print('Failed to login to forefront')
                                continue
                print('Logged in to forefront')
                await page.wait_for_load_state("networkidle")
                await forefront_continue(page)
                global forefront
                forefront = www
                await web.body(web.text+f"\n{current_time()} Nice. {emojis.spider} got into {page.url}")
                await gpt3()
                await forefront_disable_autosave(page)
                await forefront_input(page, '.') # This is required for first click. # TODO: if first click make it double.
                await forefront_input(page, '@Sensei')
                await forefront_input(page, 'Hello, who are you?')

                await web.body(web.text+f"\n{current_time()} {emojis.spider} Sensei is alive.")
                tasks.append(asyncio.ensure_future(forefront_process(web, www, message)))

            if 'tradingview.com' in page.url:
                if await tradingview_login(page, johnny_proton_login, johnny_proton_password) is True:
                    await web.body(web.text+f"\n{current_time()} Nice. {emojis.spider} got into {page.url}")
                    await page.wait_for_load_state("commit")
                    global tradingview
                    tradingview = www
            
            tasks.append(asyncio.ensure_future(www_process(www, process_delay)))
        tasks.append(asyncio.ensure_future(web_process(web, process_delay)))

        web.loop.run_until_complete(asyncio.gather(*tasks))

async def web_process(web: Window, delay = 25):
    global _debug
    while True:
        if _debug: print(f'web_ai(): {web.id}')
        if web is None:
            break
        await web.update()
        await save_cookies(web.context, f'sensei.json')
        await asyncio.sleep(delay) 

async def www_process(www: Window, delay = 25):
    global _debug
    while True:
        if _debug: print(f'www_ai(): {www.page.url}')
        if www is None:
            break
        if www.page is not None:
            await www.body(f'{current_time()} {await www.screen()}', f'{emojis.spider} ~spider')
        await asyncio.sleep(delay)

async def forefront_process(web: Window, www: Window, message: types.Message, delay = 2):
    global Windows, _debug
    lastmessage = ''
    while True:
        if _debug: print(f'forefront_ai()')
        if web is None or www is None:
            break
        if www is not None:
            output = await forefront_output(www.page)
            if len(output) > 0:
                message.text = output[-1]
                if message.text != lastmessage:
                    if message.text.find(lastmessage) == 0:
                        message.text = message.text.replace(lastmessage, '')
                    await say(message)
                    lastmessage = output[-1]
            await www.page.mouse.wheel(0, 100)
        await asyncio.sleep(delay)

#TODO: Message on delete
#await context.close()
#await browser.close()


# /claude
@sensei.message_handler(commands='claude')
async def claude(message: types.Message = None) -> None:
    if forefront is not None:
        await forefront_claude(forefront.page)
        await forefront.screen()

# /claude2
@sensei.message_handler(commands='claude2')
async def claudeplus(message: types.Message = None) -> None:
    if forefront is not None:
        await forefront_claudeplus(forefront.page)
        await forefront.screen()

# /gpt4
@sensei.message_handler(commands='gpt4')
async def gpt4(message: types.Message = None) -> None:
    if forefront is not None:
        await forefront_gpt4(forefront.page)
        await forefront.screen()

# /gpt3
@sensei.message_handler(commands='gpt3')
async def gpt3(message: types.Message = None) -> None:
    if forefront is not None:
        await forefront_gpt3(forefront.page)
        await forefront.screen()

photo_pic = './pics/sensei.jpg'

caption_pic = './sensei-sitting-room.jpg'
caption_text = """Даже путь в тысячу ли начинается с первого шага.\n«Дао Дэ Цзин»"""

about_pic = './pics/sensei-sitting.jpg'
about_text = """Наставник - хранитель опыта и знаний.

Помогает спекулянтам заработать себе на хлеб и колбасу,
стать профессиональным трейдером, пройти стажировку и
продвигаться далее по карьерной лестнице, достигать своих целей.

Ведёт ранги и награждения, следит за развитием карьеры.
Анализирует сделки, помогает исправлять ошибки,
Помогает вести дневник, наставляет на Путь истинный.

Независимая роль."""

#/start
@sensei.message_handler(commands=['start'])
async def send_welcome(message):
    await sensei.send_message(message.chat.id, "Хац!")

async def send_photo(chatid, pic, caption):
    photo = open(pic, 'rb')
    # Send the photo with the text message
    await sensei.send_photo(chatid, photo, caption=caption)
    # Close the photo file
    photo.close()

#/about
@sensei.message_handler(commands=['about'])
async def send_welcome(message):
    chatid = message.chat.id
    await send_photo(chatid, about_pic, about_text)

#/study
@sensei.message_handler(commands=['study'])
async def send_welcome(message):
    chatid = message.chat.id
    await send_photo(chatid, caption_pic, caption_text)

#/sensei
@sensei.message_handler(commands=['sensei'])
async def send_welcome(message):
    photo = open(photo_pic, 'rb')
    caption = 'Ку!'
    # Send the photo with the text message
    await sensei.send_photo(message.chat.id, photo, caption=caption)
    # Close the photo file
    photo.close()

    await sensei.send_message(message.chat.id,
"""/about - обо мне
/study - начать обучение""")

#Сенсей Сатоши Satoshi Sensei
@sensei.message_handler(func=lambda message: message.text.startswith('Сенсей') or message.text.startswith('Сатоши') or message.text.startswith('Satoshi') or message.text.startswith('Sensei'))
async def satoshi(message):
    text = message.text
    
    global forefront
    if forefront is not None:
        # TODO: Auth with different users!
        txt: str = message.text
        if txt.startswith('.') is False and txt.startswith('/') is False and txt.startswith('o/') is False:
            await forefront_input(forefront.page, txt)
            await sensei.send_chat_action(message.chat.id, 'typing', message_thread_id=message.message_id)
    
# text
# Handle all incoming text messages
@sensei.message_handler(func=lambda message: True)
async def listen(message):
    global console, _debug
    print(f'>>> incomming message {message.text}')
    if _debug: print(f'>>> {message}')
    user: types.User = message.from_user
    chat: types.Chat = message.chat

    global Allowed
    if chat.id not in Allowed:
        if message.text == '/':
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

    if message.text == '/': # create new console
        if console is not None:
            print(f'>> destroying console:\n{console}')
            await console.destroy()
        print(f'>> creating new console...')
        console = await create_console(sensei, message.chat, message.from_user)
        if _debug: print(f'>> Done!\n{console}')
        if forefront is not None:
            await console.body(f'{console.text}\n{emojis.speech} Forefront is running')

    if message.text.startswith('//'):
        await web(message)

# Buttons callback
@sensei.callback_query_handler(func=lambda call: True)
async def handle_callback(call):
    global console, _debug
    if _debug: print(f'\n{call}')
    if call.data == '🕸️':
        await web (call.message)
    if call.data == '💢':
        global Windows
        await Windows[call.message.id].destroy()

asyncio.run(sensei.infinity_polling())