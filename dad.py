import config
import os
import telebot
import io
from telebot import types

import re
from playwright.sync_api import sync_playwright

#telegram_bot_token = os.environ.get('sensei_bot_token')
dad = telebot.TeleBot(config.dad_bot_token)

avatar_wise_and_happy_man = './pics/wise_and_happy_man.jpg'
avatar_father_anime = './pics/father_anime.jpg' 


# Create a button
def create_button(emoji, text):
    return types.InlineKeyboardButton(text=f'{emoji} {text}', callback_data=f'{emoji}')

# Create a default keyboard
def keyboard(hi=False, ok=False, peace=False, dice=False):
    # Create an inline keyboard
    keyboard = types.InlineKeyboardMarkup()
    # Adding buttons
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
# /roll 🎲
@dad.message_handler(commands=['roll'])
def roll(message):
    functions.roll(dad, message)

# Buttons callback
@dad.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == '👋':
        dad.send_message(call.message.chat.id, '👌', reply_markup=keyboard(ok=True))
    if call.data == '👌':
        dad.reply_to(call.message, '✌ До нових зустрічей', reply_markup=keyboard(peace=True))
    if call.data == '✌':
        with open(avatar_father_anime, 'rb') as photo:
            dad.send_photo(call.message.chat.id, photo, 'До побачення')
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
    dad.reply_to(message, 'Ось, кинь кубик. 🎲', disable_notification=True, reply_markup=keyboard(dice=True))

#html #htmls
owner_chat_id = ''
admin_chat_id = ''

# text
# Handle all incoming text messages
@dad.message_handler(func=lambda message: True)
def listen(message):
    #Trace all incoming messages to console
    print(f"dad:{message}")

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
            screenshot_path = f'./screenshots/screen_#{message.chat.id}.{message.message_id}.png'
            page.screenshot(path=screenshot_path)
            with open(screenshot_path, 'rb') as photo:
                dad.send_photo(message.chat.id, photo, f'@{screenshot_path}')

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