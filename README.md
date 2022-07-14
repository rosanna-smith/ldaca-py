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
    file_picker=my_file_picker, 
    extension='csv')
```

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

Use a file_picker function, to select only the desired files

```python
my_file_picker = lambda f: f if f.get('encodingFormat') == 'text/csv' else None
```

Select the `entity_type`, in this case 'RepositoryObject'

```python
ldaca.store_data(
    entity_type='RepositoryObject', 
    ldaca_files='ldaca_files', 
    file_picker=my_file_picker, 
    extension='csv'
)
```

All files should be downloaded into `atomic_data/ldaca_files`