import io
import re
import json
import emojis
from telebot import types
from playwright.async_api import Page
from playwright.async_api import BrowserContext
from utils import current_time

""" TODO: add more html filters
            <a href = 'http://www.example.com/'> inline URL </a>
            <a href = 'tg://user?id=123456789'> inline mention of a user</a>
"""
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
        output = re.sub(r'\n', '', output)
        output = output.strip('\n')
        output = output.strip()
        return output
    return text
def extract_urls(text):
    pattern = r'(https?://\S+)'
    urls = re.findall(pattern, text)
    return urls
async def scrns(message:types.Message): # returns path to screen.png file of the message
    screen_path = f'./screens/'
    if message is not None:
        screen_path += f'#{message.chat.id}.{message.message_id}.png'
    return screen_path
async def web_update(www, page: Page):
            if www is not None:
                if page is not None:
                    screen_path = await scrns(www.message)    
                    await page.screenshot(path=screen_path)
                    await www.head(screen_path)
                    await www.body(f'{current_time()} {screen_path}', f'{emojis.spider} ~spider')
async def save_cookies(context: BrowserContext, cookie_file = 'cookies.json'): # TODO: Consider multiple cookies files
    cookies = await context.cookies()
    with open(cookie_file, 'w') as file:
        json.dump(cookies, file)

    return cookies
async def load_cookies(context: BrowserContext, cookie_file = 'cookies.json'):
    with open(cookie_file, 'r') as file:
        cookies = json.load(file)

    await context.add_cookies(cookies)
async def send_html(page: Page, message: types.Message, bot = None): # returns a file # TODO: do we need a message or we can send to self?
    if page is not None:
        with io.BytesIO() as file:
            content = await page.content()
            file.write(content.encode())
            file.seek(0)
            if bot is not None:
                 await bot.send_document(message.chat.id, file, caption=f'{page.url}', visible_file_name='sources.html') # TODO: make a window with modifying document?
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
async def extract_text(page: Page, selector = '*'):
        divs = await page.query_selector_all(selector)
        texts = [await div.text_content() for div in divs]
        print(f'>> extracting {selector} text:\n{texts}')
async def print_all(page: Page, objects = '*'):
    # Get a list of all available locators on the page
    # print(f'{page}')
    locators = await page.query_selector_all(objects)
    print(f'list of all {objects}\n***')
    for locator in locators:
         print(f'>> {await locator.text_content()}')
         print(f'>> > {await locator.inner_html()} ')
         print(f'{locator}')
    print('*** ***')
async def click_on(page: Page, text, button='button'):
    buttons = await page.query_selector_all(button)
    for button in buttons:
         button_text = await button.inner_text()
         if button_text == text:
              await button.click()
              print(f'clicked {text}\n{button}')
async def forefront_output(page: Page):
    print('>> forefront output')
    sel = 'div[class="post-markdown flex flex-col gap-4 text-th-primary-dark text-base "]'
    divs = await page.query_selector_all(sel)
    texts = [await div.text_content() for div in divs]
    print(texts)
    return texts 
async def forefront_input(page: Page, text, timeout = 200000):
    print('>> forefront input')
    sel = '[contenteditable="true"]'
    msg = await page.query_selector(sel)
    if msg is not None:
        await msg.click(timeout=timeout)
        await msg.type(text)
        await msg.press('Enter')
        await page.wait_for_load_state('load', timeout=timeout) # ["commit", "domcontentloaded", "load", "networkidle"]
        print(f'> {text}')
        print(f'load')

async def is_on_page(page: Page, selector: str):
    return await page.query_selector(selector)

async def forefront_login(page: Page, login, password, timeout = 200000):
    print(f">> forefront login {login}")
    print(f'page:{page}')

    await page.wait_for_load_state('domcontentloaded')
    print(f'domcontentloaded')


    button = 'button:text("Login")'
    if await is_on_page(page, button): # TODO : Test.
        await page.click(button)
        await page.wait_for_load_state('networkidle', timeout=timeout) # ["commit", "domcontentloaded", "load", "networkidle"]
        await click_on(page, 'Continue with Google', 'button')
        await page.wait_for_load_state('networkidle', timeout=timeout) # ["commit", "domcontentloaded", "load", "networkidle"]
        google_email = 'input[type="email"]'
        await page.fill(google_email, login)
        await click_on(page, 'Next', 'button')
        await page.wait_for_load_state('commit', timeout=timeout) # ["commit", "domcontentloaded", "load", "networkidle"]
            
        # Find the element with the <samp> tag
        samp = await page.query_selector('text leaf')
        if samp is not None:
            print(f'samp:{await samp.text_content()}')

        google_password = 'input[type="password"]'
        await page.fill(google_password, password)
        print(f'filled in {google_password}')

        await click_on(page, 'Next', 'button')
        await page.wait_for_load_state('commit', timeout=timeout) # ["commit", "domcontentloaded", "load", "networkidle"]

    button = 'button:text("Continue on Free")'
    if await is_on_page(page, button): # TODO : Test.
        await click_on(page, 'Continue on Free', 'button')
        
    await page.wait_for_load_state('networkidle', timeout=timeout) # ["commit", "domcontentloaded", "load", "networkidle"]
    return True