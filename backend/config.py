import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_21ezrOHSnlLh@ep-solitary-butterfly-a8j9co8x-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&options=endpoint%3Dep-solitary-butterfly-a8j9co8x')
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    EXCHANGE_API_KEY = os.environ.get('EXCHANGE_API_KEY', '70897c469235b5fda49cc734')