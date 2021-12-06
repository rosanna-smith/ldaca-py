import requests
import os
import json
from rocrate_lang.rocrate_plus import ROCratePlus
from rocrate.utils import as_list
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
        self.url = kwargs['url']
        self.token = kwargs['token']
        self.crate = None
        self.collection_type = None
        self.collection_members = None
        self.text_files = []
        self.pandas_data_frame = pandas.DataFrame()

    def set_data_dir(self, data_dir):
        self.data_dir = data_dir

    def set_crate(self):
        self.crate = ROCratePlus(self.data_dir)
        self.crate.addBackLinks()

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
            return "The API_KEY you provided is not correct or not authorized to access this collection"
        else:
            saved = self.download_metadata(self.data_dir)
            return saved

    # This is just used for testing the metadata and downloading files. Or in the case the user
    # doesnt want to download the metadata again
    def set_collection(self, collection, collection_type):
        self.collection = collection
        self.set_collection_type(collection_type)

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
            self.set_crate()
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

    def store_data(self, *args, **kwargs):  # sub_collection, entity_type='DialogueText'):
        col = self.crate.dereference(kwargs['sub_collection'])
        dialogues = []
        for entity in self.crate.contextual_entities:
            entity_list = as_list(entity.type)
            if kwargs['entity_type'] in entity_list:
                dialogues.append(entity.as_jsonld())

        # get me all the members of collection that are members of subcollection
        collection_dialogues = []

        for d in dialogues:
            dialogue = self.crate.dereference(d['@id'])
            dialogue_json = dialogue.as_jsonld()
            for member in dialogue_json['memberOf']:
                if col.id in member['@id']:
                    collection_dialogues.append(dialogue)
        if len(collection_dialogues) > 0:

            for col_dialogue in collection_dialogues:
                files = []
                dialogue = col_dialogue.as_jsonld()
                files = as_list(dialogue['hasPart'])
                # file_picker is a function that can be passed otherwise a basic one is used
                if 'file_picker' in kwargs:
                    file_picker = kwargs['file_picker']
                else:
                    file_picker = self.basic_file_picker
                self.append_if_text(files, file_picker)
            self.download_filtered_files()
            return "Found %d files" % len(self.text_files)
        else:
            return "No entities of type %s found in %s " % (col.id, kwargs['entity_type'])

    def append_if_text(self, files, file_picker):
        for file in files:
            file_crate = self.crate.dereference(file['@id'])
            file_crate_json = file_crate.as_jsonld()
            filtered_file = file_picker(file_crate_json)
            if filtered_file:
                self.text_files.append(filtered_file)

    def basic_file_picker(self, file_metadata_json):
        if file_metadata_json['encodingFormat'] == 'text/csv':
            return file_metadata_json

    # This uses pandas to store files in memory for analysis.
    # TODO: create other options of downloading files
    def download_filtered_files(self):
        for text_file in self.text_files:
            pd = pandas.read_csv(text_file['@id'], storage_options={'Authorization': 'Bearer %s' % self.token})
            self.pandas_data_frame.append(pd)
