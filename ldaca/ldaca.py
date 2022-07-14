import requests
import os
import json
from rocrate_lang.rocrate_plus import ROCratePlus
from rocrate_lang.utils import as_list
import pandas
import shutil
import uuid
import logging


def basic_file_picker(file_metadata_json):
    if file_metadata_json.get('encodingFormat') == 'text/csv':
        return file_metadata_json
    else:
        return None


def clear_files(files_dir):
    if os.path.exists(files_dir):
        print('Clearing LDaCA helper "%s" folder' % files_dir)
        for filename in os.listdir(files_dir):
            file_path = os.path.join(files_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    else:
        os.mkdir(files_dir)


class LDaCA:
    """
    An LDaCA ReST API wrapper
    """
    BASE_PROFILE = "https://purl.archive.org/textcommons/profile"

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
        self.pandas_dataframe = pandas.DataFrame()
        self.collection = None
        self._membership = []
        self.ldaca_files_path = 'ldaca_files'

    def set_collection(self, collection):
        self.collection = collection

    def set_data_dir(self, data_dir):
        self.data_dir = data_dir

    def set_crate(self):
        self.crate = ROCratePlus(source=self.data_dir)
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

    @property
    def membership(self):
        return self._membership

    @membership.setter
    def membership(self, membership):
        self._membership = membership

    def retrieve_collection(self, *args, **kwargs):
        self.set_collection(kwargs['collection'])
        self.set_collection_type(kwargs['collection_type'])
        self.set_data_dir(kwargs['data_dir'])
        response = requests.get(self.url + '/auth/memberships', headers={'Authorization': 'Bearer %s' % self.token})
        if response.status_code != 200:
            raise SystemExit("The API_KEY you provided is not correct or not authorized to access this collection")
        else:
            self.membership = response.json()
            saved = self.retrieve_metadata(self.data_dir)
            self.set_crate()
            return saved

    def retrieve_metadata(self, data_dir):
        # Downloading the metadata saves in memory information about the specific collection
        # use retrieve_collection to reset them.
        if data_dir:
            self.set_data_dir(data_dir)
        params = dict()
        params['id'] = self.collection
        # Pass resolve-links to expand sydney speaks distributed metadata into one single metadata file
        params['resolve-parts'] = True

        response = requests.get(self.url + '/object/meta', params=params)
        collection = response.json()
        metadata = collection.get('data')
        self.retrieve_members_of_collection()

        # Create a data directory to store our downloaded metadata file
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # Save it into a file
        with open(self.data_dir + '/ro-crate-metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
            return self.data_dir

    def retrieve_members_of_collection(self):
        # Pass conformsTo and memberOf to find out members of this collection
        params = dict()
        params['conformsTo'] = self.collection_type
        params['memberOf'] = self.collection
        response = requests.get(self.url + '/object', params=params)
        conforms = response.json()
        if conforms['total'] > 0:
            self.set_collection_members(conforms['data'])
        else:
            return "this collection does not have members"

    def store_data(self, *args, **kwargs):  # sub_collection, entity_type='DialogueText'):
        is_sub_collection = False
        if 'sub_collection' in kwargs:
            is_sub_collection = True
            col = self.crate.dereference(kwargs['sub_collection'])
            if not col:
                raise ValueError('Cannot find sub_collection {}', format(kwargs['sub_collection']))
        else:
            col = self.crate.dereference(self.collection)
        # Optional store the ldaca_files in a specific folder under self.data_dir
        if 'ldaca_files' in kwargs:
            self.ldaca_files_path = kwargs['ldaca_files']
        dialogues = []
        for entity in self.crate.contextual_entities + self.crate.data_entities:
            entity_list = as_list(entity.type)
            if kwargs['entity_type'] in entity_list:
                dialogues.append(entity.as_jsonld())

        # get me all the members of collection that are members of subcollection
        collection_dialogues = []

        for d in dialogues:
            dialogue = self.crate.dereference(d['@id'])
            dialogue_json = dialogue.as_jsonld()
            if is_sub_collection:
                for member in dialogue_json['memberOf']:
                    col_id = col.get('@id')
                    if col_id in member['@id']:
                        collection_dialogues.append(dialogue)
            else:
                collection_dialogues.append(dialogue)
        if len(collection_dialogues) > 0:
            for col_dialogue in collection_dialogues:
                files = []
                dialogue = col_dialogue.as_jsonld()
                files = as_list(dialogue.get('hasPart'))
                # file_picker is a function that can be passed otherwise a basic one is used
                if 'file_picker' in kwargs:
                    file_picker = kwargs['file_picker']
                else:
                    file_picker = basic_file_picker
                self.append_if_text(files, file_picker)
            extension = kwargs.get('extension')
            if not extension:
                raise SystemError('no extension provided')
            else:
                self.download_filtered_files(extension=extension)
                return "Found %d files" % len(self.text_files)
        else:
            raise ValueError("No entities of type %s found in %s " % (col.id, kwargs['entity_type']))

    def append_if_text(self, files, file_picker):
        for file in files:
            file_crate = self.crate.dereference(file['@id'])
            file_crate_json = file_crate.as_jsonld()
            filtered_file = file_picker(file_crate_json)
            if filtered_file:
                self.text_files.append(filtered_file)

    # This uses pandas to store files in memory for analysis.
    # TODO: create other options of downloading files
    def download_filtered_files(self, extension):
        # Clear
        if len(self.text_files) > 0:
            # Todo: Pass in store_data an optional delete or confirmation
            ldaca_files_folder = os.path.join(self.data_dir, self.ldaca_files_path)
            clear_files(ldaca_files_folder)
            for text_file in self.text_files:
                # Save it to a file while we are here
                if text_file['name']:
                    name = text_file['name'].replace(' ', '_') + '.' + extension
                else:
                    # If it doesnt have a name:
                    name = str(uuid.uuid4()) + '.' + extension
                self.download_file(text_file['@id'], file_path=os.path.join(ldaca_files_folder, name))
        else:
            # No files found
            return None

    def download_file(self, url, file_path):
        if not file_path:
            raise ValueError('No file_path provided')
        try:
            with requests.get(url, stream=True, headers={'Authorization': 'Bearer ' + self.token}) as response:
                response.raise_for_status()
                with open(file_path, 'wb') as out_file:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                        out_file.write(chunk)
                logging.info('Download finished successfully')
                return file_path
        except Exception as e:
            logging.error(f'Trying to download failed with error: {e}')

