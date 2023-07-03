# johnny5.1

# linux install
sudo apt-get install python3-pip
sudo apt-get install python3-virtualenv

# virtualenv --version
virtualenv env
source env/bin/activate

# install requirements.txt

# windows install
# install python https://www.python.org/downloads/

py -m pip install virtualenv
py -m virtualenv env

.\env\scripts\activate
py -m pip install -r requirements.txt
playwright install

# create config.py and config.py > johnny5_bot_token = "YOUR_SECRET_TELEGRAM_BOT_TOKEN_HERE" # put your secret key here 🤫

# launch :)
py johnny5.1.py