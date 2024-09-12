# config.py
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '5b3b881f0d95b107525e353965e09442')
    DATABASE_URI = os.getenv('DATABASE_URI', 'postgresql://postgres:VrPost@Server@localhost/delivery_db')
