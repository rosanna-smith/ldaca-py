from ldaca.ldaca import LDaCA
from dotenv import load_dotenv
import os

load_dotenv('../.env')
API_TOKEN = os.getenv('API_KEY')
URL = os.getenv('URL')
COLLECTION = os.getenv('COLLECTION')
global ldaca
global member


def test_store_all_data():
    ldaca = LDaCA(url=URL, token=API_TOKEN)
    ldaca.set_collection(COLLECTION)
    ldaca.set_collection_type('Collection')

    ldaca.set_crate()
    ldaca.get_members_of_collection()
    member = ldaca.collection_members[1]
    ldaca.store_data(sub_collection=member['crateId'], entity_type='DialogueText')
    ldaca.pandas_dataframe.to_csv(ldaca.data_dir + '/pd.csv')

    assert ldaca.pandas_dataframe.values.size > 0


def test_load_local_files():
    pd = ldaca.load_local_files()
    assert ldaca.pandas_dataframe.values.size == pd.values.size
