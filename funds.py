# Define a wallet structure
wallet = {
    'where': '', # Where is it located? 'binance,rex,qiwi,etc.'
    'purpose': '', # What is it for? 'reserves,risk,wallet,deposits,withdrawals,trading,etc.'
    'asset_type': '', # What coin is it? 'usdt,busd,doge,rub,etc.'
    'network_type': '', # What network type is it? 'fiat,doge,bsc,etc.'
    'address': '', # Wallet address '0x01234,+7965...,etc.'
    'balance': '' # Current balance
}

# Create a dictionary of wallets
wallets = {
    'fund_reserves_busd': {
        'where': 'binance',
        'purpose': 'reserves',
        'asset_type': 'BUSD',
        'network_type': 'BSC',
        'address': '0x680c4f9ff13461ce520a0065d244d2491621861c',
        'balance': ''
    },

    'fund_reserves_doge': {
        'where': 'binance',
        'purpose': 'reserves',
        'asset_type': 'DOGE',
        'network_type': 'DOGE',
        'address': 'DDw3KgysepG1daYotYxKK8sKgzi6vuq4Wh',
        'balance': ''
    },

    'fund_risk_capital_usdt': {
        'where': 'binance',
        'purpose': 'risk',
        'asset_type': 'USDT',
        'network_type': 'BSC',
        'address': '0x680c4f9ff13461ce520a0065d244d2491621861c',
        'balance': ''
    }
}