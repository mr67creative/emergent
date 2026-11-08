# Cleanup only explicitly recorded private browser sessions owned by this run.
import os
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv('/app/frontend/.env')
BASE=os.environ['REACT_APP_BACKEND_URL'].rstrip('/')+'/api'
TOKENS=['5zpaWBruMQ3q4gfbYnyqDCLF0cV8P3Ev8sMJ6dAQDNk','Q9V7zLeQYHzZyJDQZAefg5ncJSnJilBgSrZ8ZfqeudA','1NA0OAVjppA2bQmmPNDbCrep5CKoVw7eaToS5neYjU8','FnI922ZrlropTG4nE5ugxjdx8ZbcAO5h0cFW8ug_xK4','yQ9O-piaX3jQXLjAF0MFvH83aiEqKX508JFzYAICi68','vV40afQTjrKXxYGNaGwyo5aA0lLY8s1XjNIwGWBP7Oc']
TOKENS.append('qmze25vSQBwhbnFMXwH7817DykXoBNldXzlFs_kWoJg')
def cleanup():
    load_dotenv('/app/backend/.env')
    client=MongoClient(os.environ['MONGO_URL']); db=client[os.environ['DB_NAME']]
    for token in TOKENS:
        headers={'X-Demo-Token':token}
        r=requests.get(BASE+'/state',headers=headers,timeout=20)
        if r.status_code==401:continue
        assert r.status_code==200,r.text
        for c in r.json()['campaigns']:
            assert c['name'].startswith('TEST_')
            d=requests.delete(BASE+'/campaigns/'+c['id'],headers=headers,timeout=20)
            assert d.status_code==200
            assert not any(x['id']==c['id'] for x in requests.get(BASE+'/state',headers=headers,timeout=20).json()['campaigns'])
        assert db.sessions.delete_one({'token':token}).deleted_count==1
    client.close(); print('Cleaned tracked private browser sessions and exact campaign IDs')
if __name__=='__main__':cleanup()