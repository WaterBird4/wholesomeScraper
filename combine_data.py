from os import listdir
import pandas as pd
from datetime import datetime


files = listdir()
# ####### filter down to product_data_ files
pd_files = [x for x in files if str(x).startswith('product_data_')]

# ####### check at least 1 file in array
assert len(pd_files) > 0

# ####### Create initial DF from data
all_data = pd.read_csv(pd_files[0])
all_data['filename'] = str(pd_files[0])
all_data['filedate'] = str(pd_files[0]).replace('product_data_', '').replace('.txt','')

# ####### concat data from rest of files in array
for file in pd_files[1:]:
    temp = pd.read_csv(file)
    temp['filename'] = str(file)
    temp['filedate'] = str(file).replace('product_data_', '').replace('.txt','')
    all_data = pd.concat([all_data, temp])

# Make sure all files included in dataset
assert len(pd_files) == len(all_data['filename'].unique())

# ####### reset index
all_data.reset_index(drop=True, inplace=True)

# ####### identify rows with time
all_data['dt_cols'] = all_data.apply(lambda row: len(str(row['filedate']).split('_')), axis=1)

# ####### extract time from filename
all_data.loc[all_data['dt_cols'] == 4, 'filetime'] = all_data.apply(lambda row: str(row['filedate']).split('_')[-1], axis=1)

# ####### remove time from filedate
all_data.loc[all_data['dt_cols']==4, 'filedate'] = all_data.apply(lambda row: str(row['filedate'])[:-5].replace('_', '-'), axis=1)

# ####### drop dt_cols
all_data.drop('dt_cols', axis=1, inplace=True)

# ####### save file with date and time
savefile = 'all_data' + datetime.now().strftime('_%m_%d_%Y_%H%M') + '.txt'
with open(savefile, 'w') as f:
    all_data.to_csv(f, index=False)
