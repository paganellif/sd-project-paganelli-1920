import pymongo

from util.db_utils import Databases, Collections

client = pymongo.MongoClient('mongodb://localhost:27017/')
if Databases.test_db.value not in client.list_database_names():
    print("Created database " + Databases.test_db.value)
    for collection in Collections:
        print("Created collection " + collection.value)
        client[Databases.test_db.value].create_collection(collection.value)
client.close()
