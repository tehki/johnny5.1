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

async def forefront_login(page: Page, login):
    print(f'>>> forefront login')
    buttons = await page.query_selector_all('button')
    button_texts = [await button.text_content() for button in buttons]
    print(f'button_texts:{button_texts}')
    for button in buttons:
        print(f'>>> button {button}')
        if await button.text_content() == 'Login':
            # search for the buttons
            print(f'>>>> clicking Login {button}')
            await button.click() # page.get_by_role("button", name="Login").click()

        if await button.text_content() == 'Sign in with Google Continue with Google':
            print(f'>>>> clicking Sign in with Google {button}')
            await button.click() # page.get_by_role("button", name="Sign in with Google Continue with Google").click()

    textboxes = await page.query_selector_all('textbox')
    textboxes_texts = [await txtbox.text_content() for txtbox in textboxes]
    print(f'txtboxes:{textboxes_texts}')

    buttons = await page.query_selector_all('button')
    button_texts = [await button.text_content() for button in buttons]
    for button in buttons:
        if button.text_content() == 'Continue on Free':
             await button.click() # page.get_by_role("button", name="Continue on Free").click()

    for textbox in textboxes:
         print(f'txtbox:{textbox}')

         if await textbox.text_content() == 'Email or phone':
            await textbox.click()
            await page.get_by_role("textbox", name="Email or phone").click()
            await page.get_by_role("textbox", name="Email or phone").fill(login)
            await page.get_by_role("textbox", name="Email or phone").press("Enter")
    
    await page.get_by_role("textbox").locator("div").click()

    print('>>> yo yo yo how r u')
    await page.get_by_role("textbox").fill("Yo yo yo, how are u")
    await page.get_by_role("textbox").press("Enter")
    
    output = page.locator("div:nth-child(2) > div:nth-child(4)")
    print(f'{output}')
    
    """
    await page.get_by_role("textbox").filter(has_text="Message GPT-3.5").locator("div").click()
    await page.get_by_role("textbox").filter(has_text="Message GPT-3.5").fill("Good good! ")
    await page.get_by_role("textbox").filter(has_text="Message GPT-3.5").press("Enter")
    output2 = page.locator("div:nth-child(8)")
    print(f'{output2}')
    """
    print(f'{await page.content()}')
    print(f'--- the end of forefront login ---')

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
        """
        if buttons:
            print(f'>> clicking {buttons[0]}')
            await buttons[0].click()
        """
