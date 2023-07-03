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

# /ya
@dad.message_handler(commands=['ya', 'yandex'])
def ya(message: types.Message) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("https://ya.ru/showcaptcha?cc=1&mt=61624D92A5F263EAF03B4107B1A7BD132D1DD5E9F5CAC5BA75DFBE142F27A599AB84580E321C7FB491AAABD40E0DB81BD5ADA63937AAC7736ECF83E2A3FD3EA7F8DE62BAB41A359BBF387B25D7B252C581C842D7BA4E15953A9E&retpath=aHR0cHM6Ly95YS5ydS8__7a5a45ebd9be8b8e52c78369eb4cc6ab&t=2/1688424824/bac6e5f5ef29fbe85e83a1d102a1219b&u=64e4c8bd-55170695-a5ce66b6-44ed7d14&s=274fa260001d12dbba0d23d211f5b07b")
        visiting(page, 'ya.ru', scrns(message), message.chat.id)

        page.get_by_role("checkbox", name="SmartCaptcha нужна проверка пользователя").click()
        visiting(page, 'smart capcha...', scrns(message), message.chat.id)

        page.get_by_role("img", name="Задание с картинкой").click()
        visiting(page, 'задание с картинкой...', scrns(message), message.chat.id)

        page.get_by_placeholder("Строчные или прописные буквы").click()
        
        # Create a ForceReply instance
        force_reply = types.ForceReply(selective=False)
        dad.send_message(message.chat_id, 'Что там написано?', reply_markup=force_reply)
        
        page.expect_download()
        page.get_by_placeholder("Строчные или прописные буквы").fill() 
        page.get_by_placeholder("Строчные или прописные буквы").press("Enter")
        page.get_by_role("search", name="Поиск в интернете").click()
        page.get_by_placeholder("найдётся всё").click()
        page.get_by_placeholder("найдётся всё").fill("boo")
        page.get_by_role("button", name="Найти").click()
        with page.expect_popup() as page1_info:
            page.get_by_role("link", name="boo.world").click()
        page1 = page1_info.value
        page1.get_by_role("button", name="OK!").click()
        page1.locator("#main-modal").click()
        page1.locator("#authGhost").click(position={"x":191,"y":199})
        with page1.expect_popup() as page2_info:
            page1.get_by_role("button", name="ВХОД С GOOGLE").click()
        page2 = page2_info.value
        page2.get_by_role("textbox", name="Телефон или адрес эл. почты").click()
        page2.get_by_role("textbox", name="Телефон или адрес эл. почты").fill("ilya.von.gruntal@gmail.com")
        page2.get_by_role("textbox", name="Телефон или адрес эл. почты").press("Enter")
        page2.get_by_role("link", name="Повторить попытку").click()
        page2.get_by_role("textbox", name="Телефон или адрес эл. почты").click()
        page2.get_by_role("textbox", name="Телефон или адрес эл. почты").fill("ilya.von.gruntal@gmail.com")
        page2.get_by_role("textbox", name="Телефон или адрес эл. почты").press("Enter")
        with page2.expect_popup() as page3_info:
            page2.get_by_role("link", name="Подробнее…").click()
        page3 = page3_info.value

    # ---------------------
    context.close()
    browser.close()

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

        global _reply
        _reply = message.reply_text
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