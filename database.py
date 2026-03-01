# conexão com o banco

import os
from pymongo import MongoClient, ASCENDING

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

client = MongoClient(MONGO_URI)
db = client['hacker_news_db']
collection = db['posts']


def create_indexes():
    collection.create_index([("title", ASCENDING)], unique=True)
    collection.create_index([("country", ASCENDING)])
    collection.create_index([("domain", ASCENDING)])
    collection.create_index([("author", ASCENDING)])