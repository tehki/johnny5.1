from telebot import types
from telebot.async_telebot import AsyncTeleBot

import config
import asyncio
import nest_asyncio
nest_asyncio.apply()

alice = AsyncTeleBot (config.alice_bot_token)

# Handle all incoming text messages
@alice.message_handler(func=lambda message: True)
async def listen(message):
    print(f'> {message.text}')

asyncio.run(alice.infinity_polling())