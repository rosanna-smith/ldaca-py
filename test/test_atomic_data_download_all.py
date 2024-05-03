from ldaca.ldaca import LDaCA
from dotenv import load_dotenv
import os

load_dotenv('../.env')
API_TOKEN = os.getenv('API_KEY')
URL = os.getenv('HOST')
COLLECTION = os.getenv('COLLECTION_ATOMIC')
print(f"URL: {URL}")
global ldaca
global member


def test_store_all_data():
    global ldaca
    data_dir = 'atomic_data'
    ldaca = LDaCA(url=URL, token=API_TOKEN, data_dir=data_dir)
    ldaca.set_collection(COLLECTION)
    ldaca.set_collection_type('Collection')

    ldaca.retrieve_collection(
        collection=COLLECTION,
        collection_type='Collection',
        data_dir=data_dir)

    all_files = ldaca.store_data(entity_type='RepositoryObject')

    assert len(all_files) == 102

