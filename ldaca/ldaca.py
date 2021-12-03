import requests
import os
import json
from rocrate_lang.rocrate_plus import ROCratePlus
import pandas


class LDaCA():
    """
    An LDaCA API wrapper
    """
    CONFORMSTO_COLLECTION = "https://github.com/Language-Research-Technology/ro-crate-profile#Collection"

    def __init__(self, *args, **kwargs):
        self.data_dir = kwargs['data_dir']
        self.url = kwargs['url']
        self.collection = kwargs['collection']
        self.token = kwargs['token']
        self.data = kwargs['data_dir'] or 'data'
        self.crate = None

    def set_data_dir(self, data_dir):
        self.data = data_dir

    def set_crate(self):
        self.crate = ROCratePlus(self.data)

    def get_collection(self, collection, data_dir):
        self.collection = collection

        response = requests.get(self.url + '/auth/memberships', headers={'Authorization': 'Bearer %s' % self.token})
        if response.status_code != 200:
            return "The API_KEY you provided is not correct"
        else:
            saved = self.download_metadata(data_dir)
            print(saved)

    def download_metadata(self, data_dir):

        if data_dir:
            self.set_data_dir(data_dir)
        params = dict()
        params['id'] = self.collection
        # Pass resolve-links to expand sydney speaks distributed metadata into one single metadata file
        params['resolve-links'] = True

        col_response = requests.get(self.url + '/data', params=params)
        metadata = col_response.json()

        # Create a data directory to store our downloaded metadata file
        if not os.path.exists(self.data):
            os.makedirs(self.data)

        # Save it into a file
        with open(self.data + '/ro-crate-metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
            return "Saved in %s" % self.data

    def get_members_of_collection(self):
        print("Get all DialogueText that are members of:");
        # Pass conformsTo and memberOf to find out members of this collection
        params = dict()
        params['conformsTo'] = self.CONFORMSTO_COLLECTION
        params['memberOf'] = self.collection
        response = requests.get(self.url + '/data', params=params)
        conforms = response.json()
        conforms['data']
