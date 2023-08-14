import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
HOST = os.getenv('HOST')
DB = os.getenv('DB')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
ADMIN = os.getenv('ADMIN')
PORT = os.getenv('PORT')