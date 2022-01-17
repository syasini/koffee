import streamlit as st
import pandas as pd 
from sklearn.metrics.pairwise import cosine_similarity
from koffee.constants import QUALITY_MEASURES, ALTITUDE_COLS, COLOR_LIST, PROC_METHOD_LIST


@st.cache
def get_quality_agg(coffee_df, agg_func="mean", standardize=True, filter_counts_less_than=None):
    
    score_columns = QUALITY_MEASURES + ["TOTAL_CUP_POINTS"]

    country_agg = coffee_df.groupby("COUNTRY")[score_columns].agg(agg_func)
    
    # count the number of samples in each country
    country_agg["COUNT"] = coffee_df.groupby("COUNTRY")["TOTAL_CUP_POINTS"].agg("count")
    if filter_counts_less_than is not None:
        country_agg = filter_count(country_agg, filter_counts_less_than)

    # aggregate the altitude columns using the median of samples in each country
    country_agg["ALTITUDE_MEAN_METERS"] = coffee_df.groupby("COUNTRY")["ALTITUDE_MEAN_METERS"].agg("median")
    country_agg["ALTITUDE_LOW_METERS"] = coffee_df.groupby("COUNTRY")["ALTITUDE_LOW_METERS"].quantile(.1)
    country_agg["ALTITUDE_HIGH_METERS"] = coffee_df.groupby("COUNTRY")["ALTITUDE_LOW_METERS"].quantile(.9)

    if standardize:
        country_agg[score_columns] = (country_agg[score_columns] - country_agg[score_columns].min()) \
            / (country_agg[score_columns].max() - country_agg[score_columns].min())

    fill_value = 0.5 if standardize else 0
    country_agg.fillna(fill_value, inplace=True)
    return country_agg


def get_country_lon_lat(country_df, country):
    """Return a dictionary with longitude and latitude of the input country."""
    lon_lat_dict = dict(lon=country_df.loc[country, "LONGITUDE"],
                        lat=country_df.loc[country, "LATITUDE"])
    return lon_lat_dict

def filter_column(coffee_df, column_name, item_list):
    """Only keep values in the column indicated in the item list."""
    return coffee_df[coffee_df[column_name].isin(item_list)]

def filter_count(df, min_count):
    """Only keep countries with counts higher than this."""
    return df[df["COUNT"]>=int(min_count)]
    
def check_dataframe_is_empty(df):
    if df.empty:
        st.error("There is no data left for visualization... 😕\n Try changing the settings.")
        st.stop()

def get_altitudes(quality_df, country_name):
    altitude = quality_df.loc[country_name, "ALTITUDE_MEAN_METERS"]
    altitude_low = quality_df.loc[country_name, "ALTITUDE_LOW_METERS"]
    altitude_high = quality_df.loc[country_name, "ALTITUDE_HIGH_METERS"]
    return altitude, altitude_low, altitude_high

@st.cache
def convert_df(quality_df):
     # IMPORTANT: Cache the conversion to prevent computation on every rerun
     return quality_df.to_csv().encode('utf-8')


def get_cosine_similarity(quality_df):
    
    return pd.DataFrame(cosine_similarity(quality_df.fillna(0)), index=quality_df.index.values, columns=quality_df.index.values)