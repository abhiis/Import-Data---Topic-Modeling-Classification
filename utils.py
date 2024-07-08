import pandas as pd
from glob import glob as g
import os
def club_raw_files(files_dir):
    files = g(os.path.join(files_dir,f'*.*'))
    files = [file for file in files if not '~' in file]
    print(files)
    return pd.concat([pd.read_excel(file) for file in files])

