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

async def print_all(page: Page, objects = '*'):
     # Get a list of all available locators on the page
    locators = await page.query_selector_all(objects)
    print(f'list of all {objects}\n***')
    for locator in locators:
         print(f'>> {await locator.text_content()}')
    print('*** ***')

async def click_on(page: Page, text, button='button'):
    buttons = await page.query_selector_all(button)
    for button in buttons:
         button_text = await button.inner_text()
         if button_text == text:
              await button.click()
              print(f'clicked {text}\n{button}')

async def forefront_login(page: Page, login, timeout = 200000):
    print(f">> forefront login {login}")
    print(f'page:{page}')
    #await page.set_default_timeout(timeout)  # Set timeout to 200 seconds
    #print(f'timeout:{timeout}')
    await page.wait_for_load_state('domcontentloaded')
    print(f'domcontentloaded')

    login = 'button:text("Login")'
    await page.click(login)
    print(f'clicked {login}')

    await page.wait_for_load_state('networkidle', timeout=timeout)
    print(f'networkidle')

    await print_all(page, 'button')
    await click_on(page, 'Continue with Google', 'button')
    # await buttons[0].click()
    # print(f'clicked {buttons[0]}')   

    await page.wait_for_load_state('networkidle', timeout=timeout)
    print(f'_ networkidle')

    # await print_all(page, 'button')


"""
    print(f'{await page.content()}')
    await page.wait_for_load_state('networkidle', timeout=timeout)
    print(f'networkidle loaded')
    await page.get_by_role("button", name="Sign in with Google Continue with Google").click()
    await page.get_by_role("textbox", name="Email or phone").click()
    await page.get_by_role("textbox", name="Email or phone").fill(login)
    await page.get_by_role("textbox", name="Email or phone").press("Enter")
    await page.wait_for_load_state('networkidle', timeout=timeout)
    await page.goto("https://accounts.google.ru/accounts/SetSID")
    await page.wait_for_load_state('networkidle', timeout=timeout)
    await page.goto("https://chat.forefront.ai/")
    await page.wait_for_load_state('networkidle')
    await page.get_by_role("button", name="Continue on Free").click()
    await page.wait_for_load_state('networkidle')
    await page.get_by_role("textbox").locator("div").click()
    await page.get_by_role("textbox").locator("div").click()
    await page.get_by_role("textbox").fill("hai hai")
    await page.get_by_role("textbox").press("Enter")
    await page.get_by_text("Hello! How can I assist you today?").click()
    await page.get_by_role("textbox").filter(has_text="Message GPT-3.5").locator("div").click()
    await page.get_by_role("textbox").filter(has_text="Message GPT-3.5").fill("Please start every message with ")
    await page.get_by_role("textbox").filter(has_text="Please start every message with").locator("div").click()
    await page.get_by_role("textbox").filter(has_text="Please start every message with").fill("Please start every message with 🧱 symbol. Do you know what the day is it today")
    await page.get_by_role("textbox").filter(has_text="Please start every message with").press("Enter")
    await page.get_by_role("textbox").filter(has_text="Message GPT-3.5").locator("div").click()
    await page.get_by_role("textbox").filter(has_text="Message GPT-3.5").fill("Great joke")
    await page.get_by_role("textbox").filter(has_text="Message GPT-3.5").press("Enter")
    await page.get_by_text("🧱 Hello! Yes, I can tell you the current date. Today is [current date]. How can").click()
    await page.get_by_text("🧱 Thank you! I'm glad you found it amusing. If you have any specific requests o").click()
    # ---------------------
"""
    
async def extract_buttons_and_text(page: Page):
        # Find all buttons
        buttons = await page.query_selector_all('button')
        button_texts = [await button.text_content() for button in buttons]


        # Output buttons 
        #print(f'>> buttons:\n{buttons}')
        #print(f'>> button texts:\n{button_texts}')
        #print(f'>> divs:\n{divs}')
        #print(f'>> divs_texts:\n{div_texts}')

        # Click the first button if there is at least one
        """
        if buttons:
            print(f'>> clicking {buttons[0]}')
            await buttons[0].click()
        """
