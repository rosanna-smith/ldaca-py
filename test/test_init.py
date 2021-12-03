from ldaca.ldaca import LDaCA
from dotenv import load_dotenv
import os

load_dotenv('../.env')
API_TOKEN = os.getenv('API_KEY')
URL = os.getenv('URL')
COLLECTION = os.getenv('COLLECTION')
global ldaca

def test_init():
    global ldaca
    ldaca = LDaCA(url=URL, token=API_TOKEN)
    # Saves the metadata in the data_dir
    ldaca.get_collection(collection=COLLECTION, collection_type='Collection', data_dir='data')

    ldaca.collection_members

