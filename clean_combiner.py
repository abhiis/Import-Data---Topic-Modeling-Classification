import os, pandas as pd, numpy as np
import pyxlsb
import warnings as ws

class DataCombiner:
    def __init__(self, cleaned_OU_files):
        self.cleaned_OU_files = cleaned_OU_files
        self.cleaned_files = {}
        self.collector = {}
        self.sheets_known = {}
        print("Running sheet identification....")
        self.identify_sheet()

    def identify_sheet(self):
        for filename in self.cleaned_OU_files:
            if '.xls' in filename:
                file = pd.ExcelFile(filename)
                sheet_selected = self.sheets_known.get(filename, 0)
                print(filename.split("\\")[-1])
                print(file.sheet_names)
                if not sheet_selected:
                    if 'Raw' in file.sheet_names:
                        print("Auto Selecting: Raw")
                        sheet_selected = 'Raw'
                    else:
                        sheet_selected = input("Which sheet to select?:   ")
                    self.sheets_known[filename] = sheet_selected
        
    def eda(self):
        ### EDA
        print(f"Total Files: {len(self.cleaned_files.keys())}")
        collector = []
        for file in self.cleaned_files.keys():
            holder = self.cleaned_files.get(file, "Doesn't exists.")
            print(file)
            print(holder.columns)
            print(holder.shape)
            holder['file'] = file
            collector.append(holder)
        self.collector = collector

    def read_files(self):
        ws.filterwarnings("ignore")
        for filename in self.cleaned_OU_files:
            if '.xls' in filename:
                file = pd.ExcelFile(filename)
                sheet_selected = self.sheets_known.get(filename, 0)
                print(filename.split("\\")[-1])
                print(file.sheet_names)
                if not sheet_selected:
                    if 'Raw' in file.sheet_names:
                        print("Auto Selecting: Raw")
                        sheet_selected = 'Raw'
                    else:
                        sheet_selected = input("Which sheet to select?:   ")
                    self.sheets_known[filename] = sheet_selected
                
                print(f"Selected sheet --> {sheet_selected}")

                if '.xlsb' in filename:
                    raw = pd.read_excel(filename, sheet_name=sheet_selected, engine='pyxlsb')
                elif '.xlsx' in filename:
                    raw = pd.read_excel(filename, sheet_name=sheet_selected)
                elif '.csv' in filename:
                    raw = pd.read_csv(filename)
                else:
                    print(f"Can't find a loader for {filename}")
                if len(raw) > 15000:
                    print("Unmapped rows may be present. Removing rows with blanks in Operating Unit.")
                ## check if we have read column names
                if not 'Operating Unit' in raw.columns:
                    if 'Operating Unit' in raw.iloc[0].values:
                        raw.columns = raw.iloc[0].values
                        raw = raw.iloc[1:]


                raw = raw[~raw['Operating Unit'].isna()]
                self.cleaned_files[filename.split("\\")[-1]] = raw
        return self
            

    def return_problematic_data(self, file_keyword, sheet_name):
        return pd.read_excel([file for file in self.cleaned_OU_files if file_keyword in file][0], sheet_name=sheet_name)

    def identify_file_name(self, keyword):
        file_names = [file for file in self.cleaned_OU_files if keyword in file]
        if len(file_names) > 1:
            ws.warn("More than One file found for the keyword. Returning first index.")
        return file_names[0]

    def remove_unmapped_rows(self, deletion_dict):
        for filename_keyword, sheet in deletion_dict.items():
            data = self.return_problematic_data(filename_keyword, sheet)
            data = data[~data['Operating Unit'].isna()]
            self.raw_collector_cleaned[self.identify_file_name(filename_keyword).split("\\")[-1]] = data
        return self.raw_collector_cleaned


    def create_extract(self):
        extract = pd.concat(self.collector)
        cols_to_rename = {"Index":'ImpIndex'}
        extract.rename(columns=cols_to_rename, inplace=True)
        identity_cols = ['Operating Unit','Sub-Operating Unit','Product Type','Company','Family name']
        extract = extract.drop_duplicates()

        for col in identity_cols:
            extract[col] = extract[col].astype(str)

        extract['familyIndex'] = extract['Operating Unit'] +'>'+ extract['Sub-Operating Unit'] +'>'+ extract['Product Type']+'>'+extract['Company'] +'>'+ extract['Family name']
        extract['deviceIndex'] = extract['Operating Unit'] +'>'+ extract['Sub-Operating Unit'] +'>'+ extract['Product Type']
        # Insert 'deviceIndex' at position 1
        device_index = extract.pop('deviceIndex')
        extract.insert(0, 'deviceIndex', device_index)

        # Insert 'familyIndex' at position 0
        family_index = extract.pop('familyIndex')
        extract.insert(1, 'familyIndex', family_index)
        return extract
        
    def get_mdt_period_meta(self):
        period_df = pd.read_csv("MDT Period_df.csv")
        return period_df