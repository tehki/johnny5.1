from binance.client import Client
from binance.exceptions import BinanceAPIException


import emojis
import re
import funds
import config

# /send_message_to_owner
def send_message_to_owner(bot, message, owner_chat_id):
    #Send message info to owner chat
    text = f'#{message.chat.id} @{message.chat.username} {message.chat.first_name} {message.chat.last_name}\n{message.text}'
    bot.send_message(owner_chat_id, text)
# /send_sticker_to_owner
def send_sticker_to_owner(bot, message, owner_chat_id):
    # Get sticker ID
    sticker_id = message.sticker.file_id
    text = f'#{message.chat.id} @{message.chat.username} {message.chat.first_name} {message.chat.last_name}\n{sticker_id}'
    bot.send_message(owner_chat_id, text)
    bot.send_sticker(owner_chat_id, sticker_id)

# /send_sticker chat_id
def send_sticker(bot, message, to_chat_id):
    # Get sticker ID
    sticker_id = message.sticker.file_id
    text = f'#{message.chat.id} @{message.chat.username} {message.chat.first_name} {message.chat.last_name}\n{sticker_id}'
    print(f'\n>>> send sticker:#{to_chat_id}:{text}')
    bot.send_sticker(to_chat_id, sticker_id)


# /chatid
def send_chatid(bot, message):
    bot.send_message(message.chat.id, message.chat.id,
                     disable_notification=True)

# /roll 🎲
def roll(bot, message, keyboard = None):
    bot.send_dice(message.chat.id, emoji=emojis.dice_emoji,
                  disable_notification=True)

# /send_pic
def send_pic(bot, chatid, pic, caption, disable_notification=False, protect_content=False, reply_markup=None):
    photo = open(pic, 'rb')
    # Send the photo with the text message
    bot.send_photo(chatid, photo, caption=caption, disable_notification=disable_notification, protect_content=protect_content, reply_markup=reply_markup)
    # Close the photo file
    photo.close()

# /re
def reply(bot, message):
    # Remove /re from message text
    message_text = message.text[3:]
    
    # Extracting hashtags using regular expressions
    hashtags = re.findall(r'#\w+', message_text)

    if message.reply_to_message != None:
        hashtags += re.findall(r'#\w+', message.reply_to_message.text)

    # Removing hashtags using regular expressions
    reply_text = re.sub(r'#\w+', '', message_text)

    # Printing the extracted hashtags
    for tag in hashtags:
        bot.send_message(tag[1:], reply_text)

# /reply
def reply_to(bot, message):
    # Remove /reply from message text
    message_text = message.text[7:]
    if message.reply_to_message != None:
        bot.reply_to(message.reply_to_message, message_text)

#/funds
def check_funds(bot, message):
    chat_id = message.chat.id

    # Connect to the Binance client
    binance = Client(config.alice_binance_api_key,
                    config.alice_binance_secret_key)

    # Get the account information
    binance_account_info = binance.get_account()
    # Print deposit address dict
    # print(json.dumps(account_info, indent=4))

    for wallet_name, wallet_info in funds.fund_wallets.items():
        # Specify the asset symbol for which you want to check the wallet address
        asset_where = wallet_info['where']
        asset_purpose = wallet_info['purpose']
        asset_type = wallet_info['asset_type']
        asset_network = wallet_info['network_type']
        asset_address = wallet_info['address']
        #asset_balance = wallet_info['balance']

            
        # Get the deposit address for the specified asset
        deposit_address = binance.get_deposit_address(asset_type, asset_network)
        # Extract the wallet address from the response
        wallet_address = deposit_address['address']        

        correct_wallet = asset_address == wallet_address
        if correct_wallet:
            # Iterate over the balances and find the balance for a specific asset

            if asset_where == 'binance':
                for balance in binance_account_info['balances']:
                    if balance['asset'] == asset_type:
                        balance_free = balance['free']
                        balance_locked = balance['locked']
                        break

            alice_message = ''
            if asset_purpose == 'reserves':
                alice_message += 'Резервы фонда'
            if asset_purpose == 'risk':
                alice_message += 'Риск-капитал фонда'
                
            alice_message += f"\n{asset_type}:{asset_network} {wallet_address}"
            alice_message += f"\nbalance:{balance_free} (free) + {balance_locked} (locked)"
            #alice.reply_to(message, alice_message)

            icon = open('./icons/'+asset_type+'.png', 'rb')
            bot.send_photo(chat_id, icon, caption=alice_message, disable_notification=True, protect_content=True)

        else:
            bot.reply_to(message, f'{wallet_name}: {wallet_address} and {asset_address} do not match', disable_notification=True, protect_content=True)