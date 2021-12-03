### An LDaCA API Wrapper

# Work in progress

Example:

```python
from ldaca.ldaca import LDaCA
ldaca = LDaCA(url='https://ldaca.api.url/api', token='my-token-12-34')
# Saves the metadata in the data_dir
ldaca.get_collection('arcp://name,my-corpus/corpus/root', data_dir='data')
```