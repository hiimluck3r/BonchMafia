import os
from dotenv import loaddotenv

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
HOST = os.getenv('HOST')
DB = os.getenv('DB')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')