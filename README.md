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
ldaca.get_collection(
    collection='arcp://name,my-corpus/corpus/root',
    collection_type='Collection',
    data_dir='data')
```

You can find the members of your selected collection by doing:

```python
members = ldaca.get_members_of_collection()
```

Then select a particular corpus and store it in a pandas dataFrame

```python
# Stores data into a pandas dataframe
ldaca.store_data(
    sub_collection='arcp://name,my-corpus/subcorpus/subcorpusname',
    entity_type='DialogueText')
ldaca.pandas_dataframe
```

Optional: you can pass a file_picker function

```python
my_file_picker = lambda f: f if f['encodingFormat'] == 'text/csv' else None 
```

or

```python
my_other_file_picker = lambda f: f if 'OrthographicTranscription' in f['@type'] else None
```

and:

```python
ldaca.store_data(
    sub_collection='arcp://name,my-corpus/subcorpus/subcorpusname',
    entity_type='DialogueText',
    file_picker=my_other_file_picker)
ldaca.pandas_dataframe
```

