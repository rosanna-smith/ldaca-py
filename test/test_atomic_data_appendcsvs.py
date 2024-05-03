from ldaca.ldaca import LDaCA
from dotenv import load_dotenv
import os
import pandas as pd
import csv

load_dotenv('../.env')
API_TOKEN = os.getenv('API_KEY')
URL = os.getenv('HOST')
COLLECTION = os.getenv('COLLECTION_ATOMIC')
print(f"URL: {URL}")
global ldaca
global member


def test_store_all_csv():
    global ldaca
    data_dir = 'atomic_data'
    ldaca = LDaCA(url=URL, token=API_TOKEN, data_dir=data_dir)
    ldaca.set_collection(COLLECTION)
    ldaca.set_collection_type('Collection')

    ldaca.retrieve_collection(
        collection=COLLECTION,
        collection_type='Collection',
        data_dir=data_dir)

    my_file_picker = lambda f: f if f.get('encodingFormat') == 'text/csv' else None
    all_files = ldaca.store_data(entity_type='RepositoryObject', file_picker=my_file_picker)

    assert len(all_files) == 34
    
    
    #Version 1 with pandas - doesn't duplicate the header for each file so more difficult to differentiate the 34 files
    # Set the path to your main folder containing subfolders and CSV files
    main_folder = 'atomic_data/files'

    # Initialize an empty DataFrame to store combined data
    combined_data = pd.DataFrame()

    # Iterate through each subfolder
    for subdir, dirs, files in os.walk(main_folder):
        for file in files:
            # Check if the file is a CSV
            if file.endswith('.csv'):
                # Read the CSV file into a DataFrame
                file_path = os.path.join(subdir, file)
                data = pd.read_csv(file_path)
                # Append the data to the combined DataFrame
                combined_data = combined_data.append(data, ignore_index=True)

    # Write the combined DataFrame to a single CSV file
    combined_data.to_csv('atomic_data/combined_csvs_v1.csv', index=False)


'''
    #Version 2 with csv - keeps the header for each file so easier to differentiate
    # Set the path to your main folder containing subfolders and CSV files
def test_combine_all_csv():
    main_folder = 'atomic_data/files'

    # Initialize a list to store combined rows
    combined_rows = []

    # Iterate through each subfolder
    for subdir, dirs, files in os.walk(main_folder):
        for file in files:
            # Check if the file is a CSV
            if file.endswith('.csv'):
                # Read the CSV file and append its rows to combined_rows
                file_path = os.path.join(subdir, file)
                with open(file_path, 'r', newline='') as csvfile:
                    csvreader = csv.reader(csvfile)
                    for row in csvreader:
                        combined_rows.append(row)

    # Write the combined rows to a single CSV file
    output_file = 'atomic_data/combined_csvs_v2.csv'
    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for row in combined_rows:
            csvwriter.writerow(row)
'''