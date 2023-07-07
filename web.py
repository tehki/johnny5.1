import re
def extract_urls(text):
    pattern = r'(https?://\S+)'
    urls = re.findall(pattern, text)
    return urls

from telebot import types
async def scrns(message:types.Message): # returns path to screen.png file of the message
    screen_path = f'./screens/'
    if message is not None:
        screen_path += f'#{message.chat.id}.{message.message_id}.png'
    return screen_path

from playwright.async_api import Page

async def cookies(page: Page):
            # Get the cookies
            cookies = page.context.cookies()
            for cookie in cookies:
                print(f'\n{cookie}')
            return cookies

import io
async def send_html(page: Page, message: types.Message, bot = None): # returns a file # TODO: do we need a message or we can send to self?
    if page is not None:
        with io.BytesIO() as file:
            content = await page.content()
            file.write(content.encode())
            file.seek(0)
            if bot is not None:
                 bot.send_document(message.chat.id, file, caption=f'{page.url}', visible_file_name='sources.html') # TODO: make a window with modifying document?
            return file # TODO: can a self contain multiple documents and send them in one window?


async def tradingview_login(page: Page, login, password):
    await page.goto("https://www.tradingview.com/")
    await page.get_by_role("button", name="Open user menu").click()
    await page.get_by_role("menuitem", name="Sign in").click()
    await page.get_by_role("button", name="Email").click()
    await page.get_by_label("Email or Username").click()
    await page.get_by_label("Email or Username").fill(login)
    await page.get_by_label("Password").click()
    await page.get_by_label("Password").fill(password)
    await page.get_by_role("button", name="Sign in").click()

async def extract_buttons_and_text(page: Page):
        # Find all buttons
        buttons = await page.query_selector_all('button')
        button_texts = [await button.text_content() for button in buttons]

        # Find all text from divs
        divs = await page.query_selector_all('div')
        div_texts = [await div.text_content() for div in divs]

        # Output buttons 
        print(f'>> buttons:\n{buttons}')
        print(f'>> button texts:\n{button_texts}')
        print(f'>> divs:\n{divs}')
        print(f'>> divs_texts:\n{div_texts}')

        # Click the first button if there is at least one
        if buttons:
            buttons[0].click()
