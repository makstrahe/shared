import string
import os
from pathlib import Path
import pandas as pd


class CsvFileReader:
    def __init__(self, directory_name: string, separator: chr):
        self.directory_name = directory_name
        self.separator = separator

    def create_timeseries_dataframe(self, filename: string, date_colname: string):
        f = os.path.join(self.directory_name, filename)
        if os.path.isfile(f):
            return CsvFileReader.__timeseries_dataframe_formatter(
                pd.read_csv(filepath_or_buffer=f, sep=self.separator), date_colname)

    def create_timeseries_dataframe_dict(self, date_colname: string):
        dataframe_dict = dict()
        for filename in os.listdir(self.directory_name):
            dataframe_dict[Path(filename).stem.split('_')[0]] = self.create_timeseries_dataframe(filename, date_colname)
        return dataframe_dict

    @staticmethod
    def __timeseries_dataframe_formatter(df: pd.DataFrame, date_colname: string):
        df = df.applymap(lambda x: x.strip() if type(x) == str else x)
        df.loc[:, df.columns != date_colname] = df.loc[:, df.columns != date_colname].apply(pd.to_numeric)
        df = df.set_index(date_colname)
        df.index = pd.to_datetime(df.index, format="%d.%m.%Y")
        return df
