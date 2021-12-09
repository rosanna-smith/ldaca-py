from ldaca.ldaca import LDaCA
from dotenv import load_dotenv
import os

load_dotenv('../.env')
API_TOKEN = os.getenv('API_KEY')
URL = os.getenv('HOST')
COLLECTION = os.getenv('COLLECTION')
global ldaca
global member


def test_init():
    global ldaca
    ldaca = LDaCA(url=URL, token=API_TOKEN)
    # Saves the metadata in the data_dir
    ldaca.get_collection(collection=COLLECTION, collection_type='Collection', data_dir='data')

    for cm in ldaca.collection_members:
        print("Member Id: %s" % cm['crateId'])

    assert len(ldaca.collection_members) > 0


def test_get_a_member():
    global member
    member = ldaca.collection_members[0]
    m = ldaca.crate.dereference(member['crateId'])
    assert m.id == member['crateId']

