### An LDaCA API Wrapper

# Work in progress

Example:

```python
from ldaca.ldaca import LDaCA
ldaca = LDaCA(url='https://ldaca.api.url/api', token='my-token-12-34')
# Saves the metadata in the data_dir
ldaca.get_collection(collection='arcp://name,my-corpus/corpus/root', collection_type='Collection', data_dir='data')
```

Then select a particular corpus and store it in a pandas dataFrame

```python
# Stores data into a pandas dataframe
ldaca.store_data(sub_collection='arcp://name,my-corpus/subcorpus/subcorpusname', entity_type='DialogueText')
ldaca.pandas_dataframe
```

Optional: you can pass a file_picker function
```python

def my_file_picker(file_metadata):
    if file_metadata['encodingFormat'] == 'text/csv':
        return file_metadata

ldaca.store_data(sub_collection='arcp://name,my-corpus/subcorpus/subcorpusname', entity_type='DialogueText', file_picker=my_file_picker)
ldaca.pandas_dataframe
```

