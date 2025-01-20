from flask_sqlalchemy import SQLAlchemy
from pymongo.mongo_client import MongoClient


db = SQLAlchemy()


mongo_client = MongoClient("mongodb+srv://admin:admin@cluster0.kuu7e.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
test_code_db = mongo_client['users_vouchers_2'] ## MongoDB database
test_code_collection = test_code_db[('test_collenctiones')] ## MongoDB test collection for app collecton
