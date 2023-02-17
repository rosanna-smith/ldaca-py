import requests
import os
import json
from rocrate_lang.rocrate_plus import ROCratePlus
from rocrate_lang.utils import as_list
import shutil
import uuid
import logging
import glob


def basic_file_picker(file_metadata_json):
    """
    Default file picker
    :param file_metadata_json:
    :return:
    """
    if file_metadata_json.get('encodingFormat') == 'text/csv':
        return file_metadata_json
    else:
        return None


def clear_files(files_dir):
    """
    Clear all files from files_dir
    :param files_dir: files path inside data_dir
    :return:
    """
    if os.path.exists(files_dir):
        logging.info(f"Clearing LDaCA helper {files_dir} folder")
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
    BASE_PROFILE = "https://purl.archive.org/language-data-commons/profile"

    def __init__(self, url: str, token: str, data_dir=None):
        """
        Constructor of LDaCA
        :param url: ldaca api url example: https://ldaca.api.url/api
        :param token: generated in ldaca web
        :param data_dir: base data directory
        """
        if not data_dir:
            self.data_dir = 'data'
        else:
            self.data_dir = data_dir
        self.url = url
        self.token = token
        self.crate = None
        self.collection_type = None
        self.collection_members = None
        self.text_files = []
        self.collection = None
        self._membership = []
        self.ldaca_files_path = 'ldaca_files'

    def set_base_profile(self, profile):
        self.BASE_PROFILE = profile

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

    def retrieve_collection(self, collection: str, collection_type: str, data_dir: str):
        """
        Will retrieve the collection metadata in the selected data_dir and set the crate
        :param args:
        :param collection: The id of the collection
        :param collection_type: Can be either Collection or Object
        :param data_dir: set the data directory
        :return:
        """
        self.set_collection(collection)
        self.set_collection_type(collection_type)
        self.set_data_dir(data_dir)
        try:
            response = requests.get(self.url + '/auth/memberships', headers={'Authorization': 'Bearer %s' % self.token})
            if response.status_code != 200:
                logging.error(f"Request failed for access collection {collection} with error {response.reason}")
                if response.text:
                    logging.error(f"{response.text}")
                raise ValueError(response.reason)
            else:
                self.membership = response.json()
                self.retrieve_metadata(self.data_dir)
                self.set_crate()
                logging.info(f"Saved crate in {self.crate}")
        except requests.exceptions.RequestException as e:
            logging.error(e)
            raise e

    def retrieve_metadata(self, data_dir):
        """
        Downloading the metadata saves in memory information about the specific collection
        use retrieve_collection to reset them.
        :param data_dir:
        :return:
        """
        if data_dir:
            self.set_data_dir(data_dir)
        params = dict()
        params['id'] = self.collection
        # Pass resolve-links to expand the collection distributed metadata into one single ro-crate-metadata file
        params['resolve-parts'] = True

        response = requests.get(self.url + '/object/meta', params=params)
        logging.debug(response.request.url)
        collection = response.json()
        if collection.get('error'):
            raise ValueError("There was an error trying to get metadata from API")
        if collection.get('data'):
            metadata = collection.get('data')  # this is to stay compatible with older versions of the Oni API
        else:
            metadata = collection

        self.retrieve_members_of_collection()

        # Create a data directory to store our downloaded metadata file
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # Save it into a file
        with open(self.data_dir + '/ro-crate-metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

    def retrieve_members_of_collection(self):
        """
        Retrieves the members of the collection sending conformsTo and memberOf to find out if there are sub collections
        :return:
        """
        params = dict()
        params['conformsTo'] = self.collection_type
        params['memberOf'] = self.collection
        response = requests.get(self.url + '/object', params=params)
        request_url = response.request.url
        logging.debug(request_url)
        conforms = response.json()
        if conforms['total'] > 0:
            self.set_collection_members(conforms['data'])
        else:
            logging.info(f"This collection {self.collection} does not have members")

    def store_data(self, entity_type: str, extension: str, ldaca_files: str = None, sub_collection: str = None,
                   file_picker=None):
        """
        Stores data inside data_dir/ldaca_files filtered by entity_type
        :param entity_type: Filter objects in collection by entity_type
        :param extension: select extension to be saved as
        :param ldaca_files: Directory inside data_dir to place files
        :param sub_collection: if set get only the sub collection members
        :param file_picker: function to send to filter files from the metadata file
        :return: list of files paths
        """
        is_sub_collection = False
        if not sub_collection:
            col = self.crate.dereference(self.collection)
        else:
            is_sub_collection = True
            col = self.crate.dereference(sub_collection)
            if not col:
                raise ValueError(f"Cannot find sub_collection {sub_collection}")

        if ldaca_files:
            self.ldaca_files_path = ldaca_files
        dialogues = []
        for entity in self.crate.contextual_entities + self.crate.data_entities:
            entity_list = as_list(entity.type)
            if entity_type in entity_list:
                dialogues.append(entity.as_jsonld())

        # get me all the members of collection that are members of subcollection
        collection_dialogues = []

        for d in dialogues:
            dialogue = self.crate.dereference(d['@id'])
            dialogue_json = dialogue.as_jsonld()
            if is_sub_collection:
                member = dialogue_json.get('memberOf')
                if member['@id']:
                    collection_dialogues.append(dialogue)
            else:
                collection_dialogues.append(dialogue)
        if len(collection_dialogues) > 0:
            for col_dialogue in collection_dialogues:
                files = []
                dialogue = col_dialogue.as_jsonld()
                files = as_list(dialogue.get('hasPart'))
                # file_picker is a function that can be passed otherwise a basic one is used
                if not file_picker:
                    file_picker = basic_file_picker
                else:
                    file_picker = file_picker
                self.append_if_text(files, file_picker)
            if not extension:
                raise ValueError("No extension provided")
            else:
                self.download_filtered_files(extension=extension)
                all_files = glob.glob(os.path.join(self.data_dir, self.ldaca_files_path + '/*.csv'))
                logging.info(f"Found {len(self.text_files)} files")
                return all_files
        else:
            raise ValueError("No entities of type %s found in %s " % (col.id, entity_type))

    def append_if_text(self, files, file_picker):
        """
        Append filtered files to text_files
        :param files: ids of files list
        :param file_picker: file_picker function
        :return:
        """
        for file in files:
            file_crate = self.crate.dereference(file['@id'])
            file_crate_json = file_crate.as_jsonld()
            filtered_file = file_picker(file_crate_json)
            if filtered_file:
                self.text_files.append(filtered_file)

    def download_filtered_files(self, extension):
        """
        Downloads all files selected into the ldaca_files_path folder
        :param extension: file name extension to be saved as
        :return:
        """
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
            logging.info("No files to download")
            return None

    def download_file(self, url, file_path):
        """
        Use requests to download file from URL
        :param url:
        :param file_path:
        :return:
        """
        if not file_path:
            raise ValueError("No file_path provided")
        try:
            with requests.get(url, stream=True, headers={'Authorization': 'Bearer ' + self.token}) as response:
                response.raise_for_status()
                with open(file_path, 'wb') as out_file:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                        out_file.write(chunk)
                logging.info("Download finished successfully")
                return file_path
        except Exception as e:
            logging.error(f"Trying to download failed with error: {e}")
