from pymongo import MongoClient
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Conectar ao MongoDB
load_dotenv()
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client['hellriders_bot']
members_collection = db['members']
farm_logs_collection = db['farm_logs']

def add_member(user_id, user_name, passaporte):
    members_collection.update_one(
        {'user_id': user_id},
        {'$set': {'user_id': user_id, 'user_name': user_name, 'passaporte': passaporte}},
        upsert=True
    )

def add_farm_log(user_id, passaporte, farm_type, quantity, img_antes, img_depois):
    id_farm = str(uuid.uuid4())
    farm_logs_collection.insert_one({
        'id_farm': id_farm,
        'user_id': user_id,
        'passaporte': passaporte,
        'farm_type': farm_type,
        'quantity': quantity,
        'img_antes': img_antes,
        'img_depois': img_depois,
        'timestamp': datetime.utcnow()
    })

def get_member_by_passport(passaporte):
    return list(farm_logs_collection.find({'passaporte': passaporte}))

def get_farm_by_id(id_farm):
    return farm_logs_collection.find_one({'id_farm': id_farm})

def is_passport_registered(passaporte):
    member = members_collection.find_one({'passaporte': passaporte})
    return member


def is_passport_registered(user_id):
    member = members_collection.find_one({'user_id': user_id})
    return member


def get_all_members():
    return list(members_collection.find())
