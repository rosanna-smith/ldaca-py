from ldaca.ldaca import LDaCA
from dotenv import load_dotenv
import os
import glob

load_dotenv('../.env')
API_TOKEN = os.getenv('API_KEY')
URL = os.getenv('HOST')
COLLECTION = os.getenv('COLLECTION_FRAGMENTED')
BASE_PROFILE = os.getenv('BASE_PROFILE') or 'https://w3id.org/ldac/profile'
global ldaca
global member

def new_file_picker(f):
    if f.get('encodingFormat'):
        encodingFormat = f.get('encodingFormat')
        return f
    else:
        return None
    
def test_store_all_data():
    global ldaca
    data_dir = 'fragmented_data'
    ldaca = LDaCA(url=URL, token=API_TOKEN, data_dir=data_dir)
    ldaca.BASE_PROFILE = BASE_PROFILE
    ldaca.retrieve_collection(
        collection=COLLECTION,
        collection_type='Collection',
        data_dir=data_dir)
    ldaca.retrieve_members_of_collection()
    if ldaca.collection_members is not None:
        if len(ldaca.collection_members) > 0:
            member = ldaca.collection_members[1]
            my_file_picker = lambda f: f if f.get('encodingFormat') == 'text/plain' else None
            all_files = ldaca.store_data(entity_type='RepositoryObject', ldaca_files='ldaca_files', file_picker=new_file_picker, extension='txt')
            assert len(ldaca.text_files) == 558
        else:
            assert False
    else:
        assert False
