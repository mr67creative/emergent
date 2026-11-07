# Cleanup only the two explicitly tracked browser sandboxes from iteration 1.
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv('/app/backend/.env')
client = MongoClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]
tokens = [
    '1PDBAvoIksPCuIFVfiwCpCa3cqV1aY4eCRgil1H3aeA',
    'NA_VJLZJ1Sz6xTnvWZW2Zu_NW8M2TjNRHKYjcIYv4OY',
]
for token in tokens:
    for collection in ['campaigns', 'submissions']:
        result = db[collection].delete_many({'owner': token})
        print(collection, 'removed', result.deleted_count)
    result = db.sessions.delete_one({'token': token})
    print('session removed', result.deleted_count)
client.close()