## An LDaCA REST API Wrapper

### Install

```shell
pip install ldaca@git+https://github.com/Language-Research-Technology/ldaca-py.git
```

### Get a token

For accessing files you will need to get a token. To get a token go to ldaca website and generate a token in the user
area Example:

### Load the modules and instanciate an LDaCA

```python
from ldaca.ldaca import LDaCA

ldaca = LDaCA(url='https://ldaca.api.url/api', token='my-token-12-34')
# Saves the metadata in the data_dir
ldaca.retrieve_collection(
    collection='arcp://name,my-corpus/corpus/root',
    collection_type='Collection',
    data_dir='data')
```

You can find the members of your selected collection by doing:

```python
ldaca.retrieve_members_of_collection()
member = ldaca.collection_members[1]
```

Use a file_picker function

```python
my_file_picker = lambda f: f if f.get('encodingFormat') == 'text/csv' else None
```

Then select a particular corpus `sub_collection` and store it in a folder
**(Beware, this folder will be deleted everytime store_data gets called)**

```python
ldaca.store_data(
    sub_collection=member['crateId'], 
    entity_type='RepositoryObject', 
    ldaca_files='ldaca_files', 
    file_picker=my_file_picker, 
    extension='csv')
```

Example:

```python
ldaca = LDaCA(url='https://ldaca.api.url/api', token='my-token-12-34', data_dir='atomic_data')

ldaca.retrieve_collection(
    collection='arcp://name,my-corpus/corpus/root',
    collection_type='Collection',
    data_dir='atomic_data')
```
```python
my_file_picker = lambda f: f if f.get('encodingFormat') == 'text/csv' else None
```
```python
ldaca.store_data(
    entity_type='RepositoryObject', 
    ldaca_files='ldaca_files', 
    file_picker=my_file_picker, 
    extension='csv'
)
```