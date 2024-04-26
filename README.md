## An LDaCA REST API Wrapper

### Install

```shell
pip install ldaca@git+https://github.com/Language-Research-Technology/ldaca-py.git
```

### Get a token

For accessing files you will need to get a token. To get a token go to ldaca website and generate a token in the user
area Example:

### Load the modules and instantiate an LDaCA

Example 1:

Retrieve a set of files from a fragmented collection

```python
from ldaca.ldaca import LDaCA

ldaca = LDaCA(url='https://ldaca.api.url/api', token='my-token-12-34')
# Saves the metadata in the data_dir
ldaca.retrieve_collection(
    collection='arcp://name,my-corpus/corpus/root',
    collection_type='Collection',
    data_dir='data')
```

If you don't want to delete any of the previous files/directories, select clear = False

Find the sub_collections of such collection

```python
ldaca.retrieve_members_of_collection()
member = ldaca.collection_members[1]
```

Use a file_picker function, to select only the desired files

```python
my_file_picker = lambda f: f if f.get('encodingFormat') == 'text/csv' else None
```

Then select a particular corpus `sub_collection` and store it in a folder. Select the `entity_type`, in this case 'RepositoryObject'

**(Beware, this folder will be deleted everytime store_data gets called)**

```python
ldaca.store_data(
    sub_collection=member['crateId'], 
    entity_type='RepositoryObject', 
    ldaca_files='ldaca_files', 
    file_picker=my_file_picker)
```

If you don't specify a file picker, it will download all files by default.
For example, if you only want to download part of the ICE collection, you would specify a file picker.

All files should be downloaded into `data/ldaca_files`

Example 2:

Download files from an atomic collection 

```python
ldaca = LDaCA(url='https://ldaca.api.url/api', token='my-token-12-34', data_dir='atomic_data')

ldaca.retrieve_collection(
    collection='arcp://name,my-corpus/corpus/root',
    collection_type='Collection',
    data_dir='atomic_data')
```

If you don't want to delete any of the previous files/directories, select clear = False

Use a file_picker function, to select only the desired files

```python
my_file_picker = lambda f: f if f.get('encodingFormat') == 'text/csv' else None
```

Select the `entity_type`, in this case 'RepositoryObject'

```python
ldaca.store_data(
    entity_type='RepositoryObject', 
    ldaca_files='ldaca_files', 
    file_picker=my_file_picker 
)
```

All files should be downloaded into `atomic_data/ldaca_files`

### Developer Documentation

Creat virtual environment:
Create a venv with python 3. Minimum python version is 3.6
    * python3 -m venv venv
    * source venv/bin/activate (Mac OS/Linux) / venv/Scripts/activate (Windows)
    * pip install -r requirements.txt
    * Then run example runs as listed above

#### For testing create a .env file in the folder above

With
```shell
HOST='https://data.ldaca.edu.au/api'
API_KEY=my-key-12-34
COLLECTION_ATOMIC='my-id'  #e.g.'arcp://name,doi10.4225%2F35%2F555d661071c76'
COLLECTION_FRAGMENTED='my-id'  #e.g.'arcp://name,doi10.25949%2F24769173.v1'
BASE_PROFILE='collection-base-profile'  #e.g.https://w3id.org/ldac/profile'
```

#### API_KEY
To get an API key:
- Login to data.ldaca.edu.au
- Under your name, select User Information
- Under API Key, select Generate

#### COLLECTION
Both an atomic and a fragmented collection ID are required for the tests. Atomic collections are those without sub-collections (e.g. Farms to Freeways Example Dataset), whereas fragmented collections may be made up of multiple sub-collections (e.g. International Corpus of English (ICE-AUS)).

The following tests require an atomic collection:
- test_atomic_data.py

The following tests require a fragmented collection:
- test_init.py
- test_fragmented.data.py

#### BASE_PROFILE

This can be obtained by right-clicking the ConformsTo icon in the portal and copying the link. Don't include #Collection at the end of the base profile link in the .env file.

#### RUNNING TESTS

When running the tests:
- Change directories to test/ first
- This ensures your .env file is picked up correctly
- To run test use the command pytest