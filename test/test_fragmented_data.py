from ldaca.ldaca import LDaCA
from dotenv import load_dotenv
import os
import glob

load_dotenv('../.env')
API_TOKEN = os.getenv('API_KEY')
URL = os.getenv('HOST')
COLLECTION = os.getenv('COLLECTION_FRAGMENTED')
BASE_PROFILE = os.getenv('BASE_PROFILE') or 'https://purl.archive.org/language-data-commons/profile#Collection'
global ldaca
global member


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
    if len(ldaca.collection_members) > 0:
        member = ldaca.collection_members[1]
        my_file_picker = lambda f: f if f.get('encodingFormat') == 'text/csv' else None
        all_files = ldaca.store_data(sub_collection=member['crateId'], entity_type='RepositoryObject', ldaca_files='ldaca_files', file_picker=my_file_picker, extension='csv')
        assert len(all_files) == 209
    else:
        assert False

