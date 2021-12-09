import os
from dotenv import load_dotenv
from ldaca.ldaca import LDaCA


load_dotenv('../.env')
TOKEN = os.getenv('API_KEY')
URL = os.getenv('HOST')
COLLECTION_ID = os.getenv('COLLECTION')
ldaca = LDaCA(url=URL, token=TOKEN)
# Saves the metadata in the data_dir
ldaca.get_collection(collection=COLLECTION_ID, collection_type='Collection', data_dir='test_data')
ldaca.get_members_of_collection()
member = ldaca.collection_members[3]
# Stores the data from sub_collection into the data_dir and the ldaca_files (will be under data_dir specified above
# in get_collection)
ldaca.store_data(sub_collection=member['crateId'], entity_type='DialogueText', ldaca_files='collection_ldaca_files')
ldaca.pandas_dataframe