import requests
import math
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
SECRET = os.getenv("SECRET")

print(SECRET)