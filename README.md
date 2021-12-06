### An LDaCA API Wrapper

# Work in progress

Example:

```python
from ldaca.ldaca import LDaCA
ldaca = LDaCA(url='https://ldaca.api.url/api', token='my-token-12-34')
# Saves the metadata in the data_dir
ldaca.get_collection('arcp://name,my-corpus/corpus/root', collection_type='Collection', data_dir='data')
# Stores data into a pandas dataframe
ldaca.store_data(sub_collection='arcp://name,my-corpus/subcorpus/subcorpusname', entity_type='DialogueText')
ldaca.pandas_data_frame
```