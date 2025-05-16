import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import seaborn as sns
import re
from requests import Response, get
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout, JSONDecodeError
sns.set_theme()


class DataFrameConstructor:

    def __init__(self, y_axis='tonnage'):
        self.url: str = 'http://10.28.100.183:3000/get/all/scraps/blv_weekly'
        self.header: dict = {'Authorization': 'xeXRK2RPc5dZLTPp2z2s4eAhfMH01bOaIZsqxbTzys12dL65e8KvKvszlalaoxOZaMhJyPGTECSSRc2j7VkZdGeJZm5Ypu02pdSoxbrxzY875vugEQ5x3aVeQu2UTAcIDwWdrgaWzuzE8u3RUz6igD'}
        self.y_axis: str = y_axis # tonnage, volume_odm, volume_total ...
        self.data: Response = None
        self.df: DataFrame = None
        self.cleaned_df: DataFrame = None
    
    def get_cleaned_df(self, ) -> DataFrame:
        return self.cleaned_df
    
    def get_raw_df(self, ) -> DataFrame:
        return self.df
    
    def get_raw_data(self, ) -> Response:
        return self.data

    def get_data(self, ) -> 'DataFrameConstructor':
        """ Fetch data from API and store it in the instance. Returns __self__ chaining """

        try:
            response = get(url=self.url, headers=self.header, timeout=10)
            response.raise_for_status() 
            self.data = response.json()
        except HTTPError as http_err:
            print(f'HTTP error: {http_err}')
        except ConnectionError:
            print('Connection error: Could not connect to server')
        except Timeout:
            print('Timeout error: Request took too long')
        except JSONDecodeError:
            print('JSON error: Could not parse response')
        except RequestException as e:
            print(f'Error: {e}')

        return self

    def convert_dataframe(self, ) -> 'DataFrameConstructor':
        """ Convert the stored JSON data to a DataFrame. Returns __df__ for chaining """

        if self.data is None:
            raise ValueError("No data available. Call get_data() first.")
        
        self.df = pd.json_normalize(self.data)

        return self
    
    def clean_df(self, ) -> 'DataFrameConstructor':
        """ Clean the Dataframe to the minimum usable data """

        if self.df is None:
            raise ValueError("No DataFrame available. Call convert_dataframe() first.")
        
        df = self.df.filter(['flightday', 'task_id', 'pile', self.y_axis])  # 'tonnage', 'volume_total'
        df = df[df['pile'].str.lower() != 'ditch']

        df['pile_group'] = df['pile'].str.extract(r'^([A-Za-z0-9]{2})')

        grouped = df.groupby(['flightday', 'task_id', 'pile_group'], as_index=False)[self.y_axis].sum()
        grouped = grouped.drop(columns=['task_id'])

        grouped['flightday'] = pd.to_datetime(grouped['flightday'])
    
        grouped = grouped.sort_values(['pile_group', 'flightday'])

        self.cleaned_df: DataFrame = grouped

        return self
    
    def graph(self, save: bool = False) -> None:
        """ Graph the cleaned dataframe """

        plt.figure(figsize=(16,8))
        
        plot = sns.lineplot(data=self.cleaned_df, x='flightday', y=self.y_axis, hue='pile_group')

        plt.title(f'{self.y_axis} progression per Pile')
        plt.xlabel('Flightday')
        plt.ylabel(f'{self.y_axis}')
        plt.legend()
        plt.xticks(rotation=32)
        plt.tight_layout()
        plt.show()
        
        if save:
            fig = plot.get_figure()
            fig.savefig("plot_tonnage.png") 
        
        

def main() -> None:

    c: DataFrameConstructor = DataFrameConstructor()
    c.get_data().convert_dataframe().clean_df().graph()


if __name__ == '__main__':
    main()
