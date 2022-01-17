import os
import pandas as pd
from koffee import DATA_PATH

def load_coffee_dataset():
    
    coffee = pd.read_csv(os.path.join(DATA_PATH, "coffee_data.csv"), index_col=0)
    return coffee

def load_countries_dataset():
    countries_df = pd.read_csv(os.path.join(DATA_PATH, "country_data.csv"), index_col=0)
    return countries_df
