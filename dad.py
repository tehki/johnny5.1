import config
import os
import telebot
import io
from telebot import types

import re

#telegram_bot_token = os.environ.get('sensei_bot_token')
dad = telebot.TeleBot(config.dad_bot_token)

avatar_wise_and_happy_man = './pics/wise_and_happy_man.jpg'
avatar_father_anime = './pics/father_anime.jpg' 


# Create a button
def create_button(emoji, text):
    return types.InlineKeyboardButton(text=f'{emoji} {text}', callback_data=f'{emoji}')

# Create a default keyboard
def keyboard(hi=False, ok=False, peace=False, dice=False, run=False):
    # Create an inline keyboard
    keyboard = types.InlineKeyboardMarkup()
    # Adding buttons
    if run:
        keyboard.add(create_button('🏃', 'Утікай'))
    if hi:
        keyboard.add(create_button('👋', 'І тобі привіт! Так потихеньку, горизонтально'))
    if ok:
        keyboard.add(create_button('👌', 'Домовилися'))
    if peace:
        keyboard.add(create_button('✌', 'Успіхів'))
    if dice:
        keyboard.add(create_button('🎲', 'Кинути'))
    return keyboard

import functions

from playwright.sync_api import Playwright, sync_playwright, expect

def visiting(page, text, screenshot_path, chat_id):
    print(f'visiting:{page}:{text}:{screenshot_path}:#{chat_id}')
    if page is not None:    
        page.screenshot(path=screenshot_path)
        with open(screenshot_path, 'rb') as photo:
            dad.send_photo(chat_id, photo, f'{text} @ {screenshot_path}')

def extract_urls(text):
    pattern = r'(https?://\S+)'
    urls = re.findall(pattern, text)
    return urls


def scrns(message):
    screenshot_path = f'./screenshots/scrn_'
    if message is not None:
        screenshot_path += f'#{message.chat.id}.{message.message_id}.png'
    return screenshot_path

import time

# /goog /google
@dad.message_handler(commands=['goog', 'google'])
def google(message: types.Message) -> None:

    with sync_playwright() as playwright:
        #browser = playwright.chromium.launch(headless=False)
        browser = playwright.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("https://www.google.com/account/about/?hl=en")
        page.get_by_role("link", name="Go to your Google Account").click()
        page.get_by_role("textbox", name="Email or phone").click()
        page.get_by_role("textbox", name="Email or phone").fill("pepe.fundbot@gmail.com")
        page.get_by_role("textbox", name="Email or phone").press("Enter")
        page.get_by_role("textbox", name="Enter your password").fill(config.pepe_gmail_password)
        page.get_by_role("textbox", name="Enter your password").press("Enter")
        page.get_by_role("button", name="Google apps").click()

        visiting(page, page.url, scrns(message), message.chat.id)

        with page.expect_popup() as page1_info:
            page.frame_locator("iframe[name=\"app\"]").get_by_role("link", name="Gmail").click()

        visiting(page, 'Clicking Gmail.', scrns(message), message.chat.id)
        page1 = page1_info.value
        visiting(page1, 'Что дальше?', scrns(message), message.chat.id)
        # ---------------------
        context.close()
        browser.close()

import pyperclip
def send_paste(chat_id):
    dad.send_message(chat_id, f'{pyperclip.paste()}')

# /rex
@dad.message_handler(commands=['rex'])
def rex(message: types.Message) -> None:
    with sync_playwright() as playwright:
        #browser = playwright.chromium.launch(headless=False)
        browser = playwright.firefox.launch(headless=False)
        context = browser.new_context()
        
        global page
        page = context.new_page()
        ''' # TODO: Register.
        page.goto("https://rexcount.store/")
        page.get_by_text("Register | Gift +30$").first.click()
        page.get_by_text("Google/Gmail").click()
        '''
        page.goto("https://rexcount.store/")
        visiting(page, 'https://mn.rexcoin.store/ref525165', scrns(message), message.chat.id )
        page.get_by_text("Login with Google").click()

        page.get_by_role("textbox", name="Email or phone").click()
        page.get_by_role("textbox", name="Email or phone").fill("ilya.von.gruntal@gmail.com")
        page.get_by_role("textbox", name="Email or phone").press("Enter")
        
        page.locator(".CYBold").click()
        visiting(page, page.content().message, scrns(message), message.chat.id)
        dad.send_message(message.chat.id, f'Press {page.locator("samp").text_content} on your phone.')

        page.goto("https://accounts.google.ru/accounts/SetSID?ssdc=1&sidt=ALWU2cvT7V843Ub3uwCivO%2BIJqpH6wtZOkXqOpO/x9w9A4A73cnjuNZjiq5Mpyj84WsZ0iqmk0xWiJTwIrBRHW%2Brprr4Yk84v7dBPgJpGNtOOTPjd4mNUPPUlfki84ucV7ar4e8%2B0RMNXSGwrU9IqDuC1CnUrSk7LcZ9KvTFGuKUoO5YGUKijmiL8CDg/ts61dgnUziP3K8KYVg38YuucZXoOJG85BYq5X6A49WoizYegsP2FZdT1qXRcbpH1m/MMNwxhUaeJy1d6qCSSdPF1qUokbKnx/VhXwunbOvWq6Pi1zCGRWSsrNMcXO/FaH%2BHK56Xz5qGgFUKqUScvb/YUuv0f3r/x/Nebvh32HJTZdaYvPyxDJL22u5qM0CAUevZ%2B9%2BECSSyOntsp0can1sgv5zzbwdENp1Gwr9viHpBD82ieduHcSDAkiTwiDMXARqESNc3LURjSXQcNdUdpn%2B79Och2jdymBTwUQ%3D%3D&continue=https://accounts.google.com/signin/oauth/consent?authuser%3D0%26part%3DAJi8hAMmabulYK_wGQDzrxWOgGHLWargj7W8i71IKljWzzr3c5HnxKbFGiVdkOGsHqQbupMtCv9-oRNpsL2ZRYl1T_X3HUgqIdmrerWbG_xOQqRf9RLgZKEd2bQlnA95-hpeqSs79Mm0U6le-I6oiQygyhk6r3J7RKVPr6dXr9WfqggMHP_MSENEKYQFHYtdVH4OlnzwOlPbQNaoeTx95ftz3RiR7sTAE1pzoLl0h9ZHCJrOVfL8utuVk7UJ1s6wt779iFvDkFUJLgBkgd9P8yCoUw6uxSUDzMJ5WdjPvL_mKXsTHUA72tkWW-xuyr_jIi4v9ZQMh-Dyee2vVCgQboAM4pKEotKlhlLEAF4ttVLqEn9z4CVy_pqky8alSdVCw9XTIcFYorMTmTnoGMW_cs5k8Et5xG_GhmX-65FqG-_9OLxZa_2-wZecICqy5aC21UKMGJoiPFhyF62_Ge0yPBQB1TRXqts_gw%26as%3DS1828853021%253A1688438672699435%26client_id%3D305576488917-ssgc4j84adbqivvlpui9vrkolh4jq3cu.apps.googleusercontent.com%26rapt%3DAEjHL4PX0-ulvwT8PsZY0kczh0AMxOekV_H7qkME9u4XmpmZBxR6Ro9H_CwlGzz8vziEJGT44blVtLN7MJNsOnvHGmQsY3Iqxw%23&tcc=1")
        page.goto("https://accounts.google.ru/accounts/SetSID")
        page.goto("https://rexcount.store/mistake.1")
        page.get_by_role("link", name="Come back").click()
        page.get_by_text("Google/Gmail").click()
        page.goto("https://mn.rexcount.store/id525165")
        page.locator(".ft_display_profile > div").click()
        visiting(page, 'https://mn.rexcount.store/id525165', scrns(message), message.chat.id )

# /ya
@dad.message_handler(commands=['ya', 'yandex'])
def ya(message: types.Message) -> None:
    with sync_playwright() as playwright:
        #browser = playwright.chromium.launch(headless=False)
        browser = playwright.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        global _page
        _page = page

        dad.send_message(message.chat.id, 'i ya!')

        if message.text[6:].startswith('/'):
            page.goto("https://ya.ru/internet/")
            context.default_timeout = 60000

            page.get_by_role("button", name="Измерить").click()
            
            visiting(_page, 'https://ya.ru/internet/', scrns(message), message.chat.id)
            page.get_by_role("button", name="Скопировать в буфер обмена").click()

            send_paste(message.chat.id)

            page.get_by_role("button", name="Поделиться").click()
            visiting(page, 'Поделиться....', scrns(message), message.chat.id)
            page.locator("label").filter(has_text="тёмный").click()
            visiting(page, 'Тёмная тема.', scrns(message), message.chat.id)
            page.get_by_label("Ссылка на картинку").click()
            visiting(page, 'Ссылка на картинку', scrns(message), message.chat.id)
            page.get_by_role("button", name="Закрыть").click()
            visiting(page, '.', scrns(message), message.chat.id)

        if message.text[5:].startswith('.'):
            _page.goto("https://ya.ru/showcaptcha?cc=1&mt=61624D92A5F263EAF03B4107B1A7BD132D1DD5E9F5CAC5BA75DFBE142F27A599AB84580E321C7FB491AAABD40E0DB81BD5ADA63937AAC7736ECF83E2A3FD3EA7F8DE62BAB41A359BBF387B25D7B252C581C842D7BA4E15953A9E&retpath=aHR0cHM6Ly95YS5ydS8__7a5a45ebd9be8b8e52c78369eb4cc6ab&t=2/1688424824/bac6e5f5ef29fbe85e83a1d102a1219b&u=64e4c8bd-55170695-a5ce66b6-44ed7d14&s=274fa260001d12dbba0d23d211f5b07b")
            _page.get_by_role("search", name="Поиск в интернете").click()
            visiting(page, 'Вы вошли? Yandex.', scrns(message), message.chat.id)
            _page.get_by_placeholder("найдётся всё").click()
            _page.get_by_placeholder("найдётся всё").fill(f'{message.text[6:]}')
            _page.get_by_role("button", name="Найти").click()
            _page.wait_for_selector('body')
            _page.wait_for_load_state("networkidle")
            visiting(_page, f'Ищем {message.text[7:]}', scrns(message), message.chat.id)

        if message.text[4:].startswith('.'):
            _page.goto("https://ya.ru/showcaptcha?cc=1&mt=61624D92A5F263EAF03B4107B1A7BD132D1DD5E9F5CAC5BA75DFBE142F27A599AB84580E321C7FB491AAABD40E0DB81BD5ADA63937AAC7736ECF83E2A3FD3EA7F8DE62BAB41A359BBF387B25D7B252C581C842D7BA4E15953A9E&retpath=aHR0cHM6Ly95YS5ydS8__7a5a45ebd9be8b8e52c78369eb4cc6ab&t=2/1688424824/bac6e5f5ef29fbe85e83a1d102a1219b&u=64e4c8bd-55170695-a5ce66b6-44ed7d14&s=274fa260001d12dbba0d23d211f5b07b")
            visiting(_page, 'ya.ru', scrns(message), message.chat.id)
            _page.get_by_role("checkbox", name="SmartCaptcha нужна проверка пользователя").click()
            visiting(_page, 'smart capcha...', scrns(message), message.chat.id)
            _page.get_by_role("img", name="Задание с картинкой").click()
            visiting(_page, 'задание с картинкой...', scrns(message), message.chat.id)
            _page.get_by_placeholder("Строчные или прописные буквы").click()
            # Create a ForceReply instance
            force_reply = types.ForceReply(True)
            dad.send_message(message.chat.id, 'Что там написано? Жду 10 секунд. Отвечай!', reply_markup=force_reply)
            time.sleep(10)
            # Ask a question and get user input
            answer = input("Что там написано?")
            # Process the answer
            print("Your answer is:", answer)
            reply(answer, message, page)
        
            # ---------------------
    context.close()
    browser.close()

def reply(answer, message, page):
    global _reply, _page
    _page = page.get_by_placeholder("Строчные или прописные буквы").fill(_reply)
    visiting(_page, f'{_reply}, говоришь?', scrns(message), message.chat.id) 
    page.get_by_placeholder("Строчные или прописные буквы").press("Enter")

# /visit 
@dad.message_handler(commands=['visit'])
def run(message: types.Message) -> None:
    with sync_playwright() as playwright:

        screenshot_path = f'./screenshots/screen_'
        if message is not None:
            screenshot_path += f'#{message.chat.id}.{message.message_id}.png'

        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()

        urls = extract_urls(message.text)
        page = context.new_page()

        for url in urls:
            page.goto(url)
            # Perform actions on the page after navigation
            visiting(page, url, screenshot_path, message.chat.id)
        
        # download = download_info.value
        # download_path = download.path()  # Get the path where the file is saved
        # download.save_as(screenshot_path)  # Save the file to a specific location
        context.close()
        browser.close()
        

# /run 🏃
@dad.message_handler(commands=['run'])
def run(message: types.Message) -> None:
    with sync_playwright() as playwright:

        screenshot_path = f'./screenshots/screen_'
        if message is not None:
            screenshot_path += f'#{message.chat.id}.{message.message_id}.png'

        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.farandwide.com/s/the-worlds-most-peaceful-countries-936ebdfd97a94aa1")
        
        visiting(page.get_by_title("Austria"), "Austria", screenshot_path, message.chat.id)
        page.mouse.wheel(0, 40000)
        visiting(page.get_by_title("Botswana"), "Botswana", screenshot_path, message.chat.id)
        page.mouse.wheel(0, -20000)
        visiting(page.get_by_title("Spain"), "Spain", screenshot_path, message.chat.id)
        visiting(page.get_by_title("Chile"), "Chile", screenshot_path, message.chat.id)
        
        # download = download_info.value
        # download_path = download.path()  # Get the path where the file is saved
        # download.save_as(screenshot_path)  # Save the file to a specific location
        context.close()
        browser.close()
        
    
# /roll 🎲
@dad.message_handler(commands=['roll'])
def roll(message):
    functions.roll(dad, message)

# Buttons callback
@dad.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == '🏃': # /run 🏃   
        run(call.message)
    if call.data == '👋':
        dad.send_message(call.message.chat.id, '👌', reply_markup=keyboard(ok=True))
    if call.data == '👌':
        dad.reply_to(call.message, '✌ До нових зустрічей', reply_markup=keyboard(peace=True))
    if call.data == '✌':
        with open(avatar_father_anime, 'rb') as photo:
            dad.send_photo(call.message.chat.id, photo, 'До побачення', reply_markup=keyboard(run=True))
    if call.data == '🎲':
        roll(call.message)

@dad.message_handler(commands=['serj'])
def serj(message):
    echo_all(message)

@dad.message_handler(commands=['start'])
def start(message):
    with open(avatar_wise_and_happy_man, 'rb') as photo:
        dad.send_photo(message.chat.id, photo, '👋 Вітаю, друже! Як справи?', reply_markup=keyboard(hi=True))

#Серж
@dad.message_handler(func=lambda message: message.text.startswith('Серж') or message.text.startswith('Serj'))
def echo_all(message):
    text = message.text
    print('Мы здесь. '+text)
    dad.reply_to(message, 'Ось, кинь кубик. 🎲', disable_notification=True, reply_markup=keyboard(dice=True, run=True))

#html #htmls
owner_chat_id = ''
admin_chat_id = ''


# text
# Handle all incoming text messages
@dad.message_handler(func=lambda message: True)
def listen(message):
    #Trace all incoming messages to console
    print(f"dad:{message}")

    if message.reply_to_message and message.reply_to_message.from_user.id == dad.get_me().id:
        reply_text = "You replied: " + message.text
        dad.send_message(message.chat.id, reply_text)
        global _reply, _page
        _reply = reply_text
        reply(_reply, message, _page)
        return _reply


    # Find all URLs in the message text using regular expressions
    urls = re.findall(r'(https?://\S+)', message.text)

    vpn_config = None
    """ #TODO Setup proxy / vpn
    # Set up VPN or proxy settings
    vpn_config = {
        "mode": "manual",
        "server": "vpn_server_address",
        "username": "vpn_username",
        "password": "vpn_password"
        }
    """

    # Set up Google Mail SSO credentials
    google_sso_email = "login@gmail.com"
    google_sso_password = "."

    # Open each URL using Playwright
    with sync_playwright() as playwright:
        for url in urls:
            browser = playwright.chromium.launch()
            context = browser.new_context(proxy=vpn_config)

            page = context.new_page()
            page.goto(url)
            # Do something with the page, e.g., take a screenshot                        
            #screenshot_path = f'./screenshots/screen_#{message.chat.id}.{message.message_id}.png'
            #page.screenshot(path=screenshot_path)
            #with open(screenshot_path, 'rb') as photo:
                #dad.send_photo(message.chat.id, photo, f'@{screenshot_path}')

            """ TODO: Find google.
            # Perform Google Mail SSO authentication
            page.fill('input[type="email"]', google_sso_email)
            page.click('[type="submit"]')
            page.fill("password", google_sso_password)
            page.click('button[type="submit"]')
            """
            
            # Continue with further actions on the authenticated

            dad.send_message(message.chat.id, f'page:{page}')

            # Get the cookies
            cookies = page.context.cookies()
            # Convert cookies to a readable text message
            cookie_message = ''
            for cookie in cookies:
                cookie_message += f"Name: {cookie['name']}, Value: {cookie['value']}\n"
                print(f'\n{cookie}')

            if cookie_message != '':
                with io.BytesIO() as file:
                    file.write(cookie_message.encode())
                    file.seek(0)
                    dad.send_document(message.chat.id, file, caption=f'{page.url}', visible_file_name='cookies.txt')

            html = page.content()

            with io.BytesIO() as file:
                # Write the HTML string to the file
                file.write(html.encode())
                # Reset the file pointer to the beginning of the file
                file.seek(0)
                # Send the file as a document
                dad.send_document(message.chat.id, file, caption=f'{page.url}', visible_file_name='sources.html')
            
            # Click on the button with the specific attributes and text
            # page.click('button:has-text("Измерить")') #TODO: Find the button and click it
            # Wait for the page to load or for a specific element to appear
            page.wait_for_load_state("networkidle")
            # or
            # page.wait_for_selector("selector_of_the_element")
            # Perform other actions..
            # Take a screenshot of the page after clicking the button
            screenshot_path = f'./screenshots/screen_#{message.chat.id}.{message.message_id}.png'
            page.screenshot(path=screenshot_path)
            with open(screenshot_path, 'rb') as photo:
                dad.send_photo(message.chat.id, photo, f'@ {screenshot_path}')

            # Close the browser
            context.close()
            browser.close()

    #Send message info to owner chat
    if owner_chat_id != '':
        functions.send_message_to_owner(dad, message, owner_chat_id)
    if admin_chat_id != '':
        functions.send_message_to_owner(dad, message, admin_chat_id)
        print(f'>> sent to admin\n>>\n{message.text}')

dad.infinity_polling()