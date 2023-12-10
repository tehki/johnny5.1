from telebot import types

# Keyboard hack.
def kbd(hack):
    dot = False
    close = False
    slash = False
    zen = False

    txt = hack
    if txt.startswith('.'):
        dot = True
    if txt[1:].startswith('.'):
        close = True
    if txt[2:].startswith('/'):
        slash=True
    if txt[3:].startswith('\\'):
        zen=True
    kbdd = keyboard(dot=dot, close=close, slash=slash, zen=zen)
    return kbdd
# Create a button
def create_button(emoji):
    return types.InlineKeyboardButton(text=f'{emoji}', callback_data=f'{emoji}')
# Create a default keyboard
def keyboard(roll=False, dot=False, hi=False, arigato=False, slash=False, close=False, zen=False, web=False):
    # Create an inline keyboard
    keyboard = types.InlineKeyboardMarkup()
    # Adding buttons
    if zen:
        keyboard.add(create_button('\/'))
    if slash:
        keyboard.add(create_button('/'))
    if hi:
        keyboard.add(create_button('o/'))
    if arigato:
        keyboard.add(create_button('/\\'))
    if dot:
        keyboard.add(create_button('.'))
    if close:
        keyboard.add(create_button('💢') )
    if roll:
        keyboard.add(create_button('🎲'))
    if web:
        keyboard.add(create_button('🕸️'))
    return keyboard