# Delete only exact browser-session tokens created and tracked in this refresh run.
import os
from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv('/app/backend/.env')
client = MongoClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]
tokens = ['I6wKwR2HzXjJXUBCDpi23TY8yadrjXAwRb1Yoa0MGy8', 'deVJ6lwF5l3K05oaj45gOia3vxL9c-Jx7KU9t4kr26s', 'sb0gcodOz7Fj38L4MIqSW9oFSfGJD6NCPLyEqvp1RaU']
for token in tokens:
    for collection in ['campaigns', 'submissions']:
        print(collection, db[collection].delete_many({'owner': token}).deleted_count)
    print('session', db.sessions.delete_one({'token': token}).deleted_count)
client.close()