import requests
import os
import json
from rocrate_lang.rocrate_plus import ROCratePlus
import pandas


class LDaCA():
    """
    An LDaCA API wrapper
    """
    BASE_PROFILE = "https://github.com/Language-Research-Technology/ro-crate-profile"

    def __init__(self, *args, **kwargs):
        if 'data_dir' in kwargs:
            self.data_dir = kwargs['data_dir']
        else:
            self.data_dir = 'data'
        if 'collection' in kwargs:
            self.collection = kwargs['collection']
        self.url = kwargs['url']
        self.token = kwargs['token']
        self.crate = None
        self.collection_type = None
        self.collection_members = None

    def set_data_dir(self, data_dir):
        self.data_dir = data_dir

    def set_crate(self):
        self.crate = ROCratePlus(self.data_dir)

    def set_collection_members(self, collection_members):
        self.collection_members = collection_members

    def set_collection_type(self, collection_type):
        if collection_type.lower() == 'collection':
            self.collection_type = self.BASE_PROFILE + "#Collection"
        elif collection_type.lower() == 'object':
            self.collection_type = self.BASE_PROFILE + "#Object"
        else:
            raise SystemExit("collection_type 'collection' or 'object' required")

    def get_collection(self, *args, **kwargs):
        self.collection = kwargs['collection']
        self.set_collection_type(kwargs['collection_type'])
        self.set_data_dir(kwargs['data_dir'])
        response = requests.get(self.url + '/auth/memberships', headers={'Authorization': 'Bearer %s' % self.token})
        if response.status_code != 200:
            return "The API_KEY you provided is not correct"
        else:
            saved = self.download_metadata(self.data_dir)
            return saved

    def download_metadata(self, data_dir):
        # Downloading the metadata saves in memory information about the specific collection
        # use get_collection to reset them.
        if data_dir:
            self.set_data_dir(data_dir)
        params = dict()
        params['id'] = self.collection
        # Pass resolve-links to expand sydney speaks distributed metadata into one single metadata file
        params['resolve-links'] = True

        col_response = requests.get(self.url + '/data', params=params)
        metadata = col_response.json()
        self.get_members_of_collection()

        # Create a data directory to store our downloaded metadata file
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # Save it into a file
        with open(self.data_dir + '/ro-crate-metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
            return "Saved in %s" % self.data_dir

    def get_members_of_collection(self):
        # Pass conformsTo and memberOf to find out members of this collection
        params = dict()
        params['conformsTo'] = self.collection_type
        params['memberOf'] = self.collection
        response = requests.get(self.url + '/data', params=params)
        conforms = response.json()
        if conforms['total'] > 0:
            self.set_collection_members(conforms['data'])
        else:
            return "this collection does not have members"
