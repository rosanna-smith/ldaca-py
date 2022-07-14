from ldaca.ldaca import LDaCA
from dotenv import load_dotenv
import os
import glob

load_dotenv('../.env')
API_TOKEN = os.getenv('API_KEY')
URL = os.getenv('HOST')
COLLECTION = os.getenv('COLLECTION_ATOMIC')
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

    my_file_picker = lambda f: f if f.get('encodingFormat') == 'text/csv' else None
    ldaca.store_data(entity_type='RepositoryObject', ldaca_files='ldaca_files', file_picker=my_file_picker, extension='csv')

    all_files = glob.glob(ldaca.data_dir + '/' + ldaca.ldaca_files_path + '/*.csv')

    assert len(all_files) == 34

