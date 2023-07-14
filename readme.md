# johnny5.1

# linux install
sudo apt-get install python3-pip
sudo apt-get install python3-virtualenv

# virtualenv --version
virtualenv env
source env/bin/activate
py -m pip install -r requirements.txt

# windows install
# install python https://www.python.org/downloads/

py -m pip install virtualenv
py -m virtualenv env
.\env\scripts\activate
py -m pip install -r requirements.txt

# launch :)
py johnny5.1.py