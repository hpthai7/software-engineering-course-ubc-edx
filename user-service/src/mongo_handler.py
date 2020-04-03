from .config import Config
from .utils.helper import Helper
from bson.objectid import ObjectId
import pymongo
from bson.dbref import DBRef
import json


class MongoHandler(object):

    def __init__(self):
        print(f"Connection to mongo: {Config}")
        self._mongo_client = pymongo.MongoClient(host=Config.DB_HOST,
                                                 port=Config.DB_PORT, # necessary
                                                 username=Config.DB_USERNAME,
                                                 password=Config.DB_PASSWORD,
                                                 authSource=Config.DB_NAME,
                                                 authMechanism=Config.DB_AUTH)

    def _user_collection(self):
        return self._mongo_client[Config.DB_NAME][Config.DB_COLLECTION_USERS]

    def persist_user(self, user):
        if 'username' not in user:
            user['username'] = Helper.make_id()
        user['_id'] = user['username']
        insert_one_result = self._user_collection().insert_one(user)
        return insert_one_result.inserted_id

    def get_users(self):
        return list(self._user_collection().find())

    def get_user(self, id):
        return list(self._user_collection().find({"_id": id}))

    def map_user_to_talk(self, username, talk):
        user = self.get_user(username)[0]
        talk_ids = []
        
        print(f'Current user: {json.dumps(user)}')
        print(f'New talk: {json.dumps(talk)}')
        if 'talk_ids' in user: 
            talk_ids.append(user["talk_ids"])
        
        talk_ids.append(talk['_id'])
        result = self._user_collection().update_one({'_id': user['_id']}, {'$set': {'talk_ids': talk_ids}}, upsert=True)
        print(f'All talks: {json.dumps(talk_ids)}')
        return result.raw_result
