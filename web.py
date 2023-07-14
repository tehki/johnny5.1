import io
import re
import os
import json
from telebot import types
from playwright.async_api import Page
from playwright.async_api import BrowserContext

""" TODO: add more html filters
            <a href = 'http://www.example.com/'> inline URL </a>
            <a href = 'tg://user?id=123456789'> inline mention of a user</a>
"""

async def extract_urls(text):
    if text is not None:   
        pattern = r'(https?://\S+)'
        urls = re.findall(pattern, text)
        return urls

async def save_cookies(context: BrowserContext, cookie_file = 'cookies.json'): # TODO: Consider multiple cookies files
    cookies = await context.cookies()
    dir = f'./cookies/'
    # Check if the directory exists
    if not os.path.exists(dir):
    # Create the directory if it doesn't exist
        os.makedirs(dir)

    with open(f'{dir}{cookie_file}', 'w') as file:
        json.dump(cookies, file)
    return cookies

async def load_cookies(context: BrowserContext, cookie_file = 'cookies.json'):
    if os.path.exists(f'./cookies/{cookie_file}'):
        with open(f'./cookies/{cookie_file}', 'r') as file:
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
async def strip_html(text):
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

async def is_on_page(page: Page, selector: str):
    return await page.query_selector_all(selector)

async def click_on(page: Page, selector='button:text("Next")'):
    buttons = await page.query_selector_all(selector)
    for button in buttons:
        await button.click()
        print(f'clicked on {selector}\n{button}')

async def tradingview_login(page: Page, login, password):
    print('tradingview login')
    await page.wait_for_load_state('load') # ["commit", "domcontentloaded", "load", "networkidle"]

    topLeftMenu = 'div[class^="topLeftButton"]'
    if await is_on_page(page, topLeftMenu):
         await page.click(topLeftMenu)

    if await is_on_page(page, 'span:text("Sign in")'):
         await page.click('span:text("Sign in")')
    else:
        await page.click(topLeftMenu)
         
    await page.wait_for_load_state('load') # ["commit", "domcontentloaded", "load", "networkidle"]
    if await is_on_page(page, 'span:text("Email")'):
         await page.click('span:text("Email")')
         
    await page.wait_for_load_state('load') # ["commit", "domcontentloaded", "load", "networkidle"]
    if await is_on_page(page, 'input[id="id_username"]'):
         await page.fill('input[id="id_username"]', login)
    if await is_on_page(page, 'input[id="id_password"]'):
         await page.fill('input[id="id_password"]', password)
    if await is_on_page(page, 'span:text("Sign in")'):
         await page.click('span:text("Sign in")')
    return True

async def forefront_format(text):
    # Remove all HTML tags except <code> and </code>
    cleaned_text = re.sub(r'<(?!/?code\b)[^>]+>', '', text)
    # Remove 'pythonCopy'
    cleaned_text = re.sub('pythonCopy', '\n', cleaned_text)
    return cleaned_text

async def forefront_disable_autosave(page: Page):
    print(f">> forefront disable autosave")
    button = 'button:text("Manual")'
    if await is_on_page(page, button):
        await page.click(button)

async def forefront_enable_autosave(page: Page):
    print(f">> forefront enable autosave")
    button = 'button:text("Auto")'
    if await is_on_page(page, button):
        await page.click(button)

async def forefront_continue(page: Page):
    button = 'button:text("Continue on Free")'
    try:
        await page.wait_for_selector(button, timeout=3000)
        await page.click(button)
    except Exception as e:
        return False

async def forefront_output(page: Page):
    # print('>> forefront output')
    sel = 'div[class="post-markdown flex flex-col gap-4 text-th-primary-dark text-base "]'
    divs = await page.query_selector_all(sel)
    htmls = [await forefront_format(await div.inner_html()) for div in divs]
    # print(htmls)
    return htmls

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

async def forefront_login(page: Page, login: str, password: str, timeout = 200000):
    print(f">> forefront login {login}")
    print(f'page:{page}')
    await page.wait_for_load_state('networkidle')
    print(f'networkidle')

    button = 'button:text("Login")'
    if await is_on_page(page, button): # TODO : Test.
        await page.click(button)
        await page.wait_for_load_state('networkidle', timeout=timeout) # ["commit", "domcontentloaded", "load", "networkidle"]

    if login.endswith('gmail.com'):
        span = 'span:text("Continue with Google")'
        if await is_on_page(page, span):
            await page.click(span)
            await page.wait_for_load_state('networkidle', timeout=timeout) # ["commit", "domcontentloaded", "load", "networkidle"]

            # Find the element with the <samp> tag
            samp = await page.query_selector('text leaf')
            if samp is not None:
                print(f'samp:{await samp.text_content()}')
    
    email_input = 'input[type="email"]'
    if await is_on_page(page, email_input):    
        await page.fill(email_input, login)

    await click_on(page, 'button:text("Continue")')
    await page.wait_for_load_state('load', timeout=timeout) # ["commit", "domcontentloaded", "load", "networkidle"]

    email_password = 'input[type="password"]'
    if await is_on_page(page, email_password):
        await page.fill(email_password, password)
        await click_on(page)
    
    await page.wait_for_load_state('load') # ["commit", "domcontentloaded", "load", "networkidle"]

    input = 'input[name^="codeInput-"]'
    try:
        await page.wait_for_selector(input, timeout=5000)
        return False
    except Exception as e:
        print(f'There is no code validation required\n{str(e)}')

    return True
    
async def needs_validation(page: Page):
    input = 'input[name^="codeInput-"]'
    if await is_on_page(page, input):
        return True
    else:
        return False

async def forefront_validate(page: Page, code: str):
    for i, char in enumerate(code):
        field = f'input[name^="codeInput-{i}"]'
        if await is_on_page(page, field):
            await page.fill(field, char)

    await page.wait_for_load_state('load')

    input = '[contenteditable="true"]'
    try:
        await page.wait_for_selector(input, timeout=30000)
        return True
    except Exception as e:
        return False