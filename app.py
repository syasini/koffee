import streamlit as st
from io import BytesIO

from koffee.plots import plot_logo, plot_coffee_cup, plot_coffee_latte_art, plot_altitude, WorldMap
from koffee.datasets import load_coffee_dataset, load_countries_dataset
from koffee.constants import QUALITY_MEASURES, COLOR_LIST, PROC_METHOD_LIST
from koffee.utils import filter_column, get_quality_agg, get_country_lon_lat,\
    check_dataframe_is_empty, filter_count, convert_df, get_altitudes,\
    get_cosine_similarity

# Let's go!

# ==============
# Logo and Title
# ============== 

plot_logo()
st.sidebar.title("Koffee of the world")
st.sidebar.markdown("Made by [Siavash Yasini](https://www.linkedin.com/in/siavash-yasini/), while holding a cup of :coffee:!")


# ==============
#    Settings
# ==============

st.sidebar.header("Settings")

projection_type = st.sidebar.radio("Map Projection Type", ["orthographic", "stereographic", "natural earth"])
st.sidebar.markdown("---")

standardize = st.sidebar.checkbox("Standardize the data (recommended)", value=True)
st.sidebar.caption("""If checked, each quality measure will be scaled between 0 to 1 for all countries. 
                      For each measure, 0 and 1 will be respectively assigned to countries with the mimimum and maximum values.""")

agg_func = st.sidebar.radio("Aggregation", ["mean", "median", "max"], index=0)
st.sidebar.caption("This function will be applied to each country's samples to aggregate the quality measures.")
st.sidebar.markdown("---")

color = st.sidebar.multiselect("Bean Color", COLOR_LIST, default=COLOR_LIST)
proc_method = st.sidebar.multiselect("Processing Method", PROC_METHOD_LIST, default=PROC_METHOD_LIST)
st.sidebar.markdown("---")

min_sample_count = st.sidebar.slider("Min Sample Count Required", min_value=1, max_value=20, value=5)
st.sidebar.caption("Countries with fewer samples than this number in the dataset will be excluded.")
st.sidebar.markdown("---")


# ==============
#   Main App
# ==============

# load the data
coffee_df = load_coffee_dataset()
countries_df = load_countries_dataset()

# filter data based on color and processing method options
for column_name, options in zip(["COLOR", "PROCESSING_METHOD"], [color, proc_method]):
    coffee_df = filter_column(coffee_df, column_name, options)
    check_dataframe_is_empty(coffee_df)

# aggregate the quality measures for each country (drop out ones with too few samples)
quality_df = get_quality_agg(coffee_df, standardize=standardize, agg_func=agg_func, filter_counts_less_than=min_sample_count)
quality_df = quality_df.merge(countries_df, left_index=True, right_index=True)

world_map_placeholder = st.empty() # to be filled with the world map later

# set the default to Ethiopia if possible
try:
    default_country_index = quality_df.index.get_loc("Ethiopia")
except KeyError:
    default_country_index = 0

# select the country using dropdown list 
st.session_state["country"] = st.selectbox("Select Country", quality_df.index, index=default_country_index)

# plot the world map
world_map = WorldMap(quality_df["COUNTRY_CODE"].values.tolist(), 
                     z=quality_df["TOTAL_CUP_POINTS"].values.tolist(), 
                     text = quality_df.index.values.tolist(), 
                     colorbar_title="Total Cup Points")

# plot the world map and center it on the selected country
lon_lat_dict = get_country_lon_lat(countries_df, st.session_state["country"])
world_map.update_layout(projection_type=projection_type, **lon_lat_dict)
world_map_placeholder.plotly_chart(world_map.fig, use_container_width=True)

# get the quality profile vector for the selected country
coffee_quality = quality_df.loc[st.session_state["country"], QUALITY_MEASURES]

# plot the quality cup figure
quality_labels = coffee_quality.index
quality_values = coffee_quality.to_list()

fig = plot_coffee_cup(figsize=(6, 6), dpi=200)
fig = plot_coffee_latte_art(quality_labels, quality_values, fig=fig, standardize=standardize)

# plot the coffee cup (with work-around solution for the figure size)
buf = BytesIO()
fig.savefig(buf, format="png")
st.image(buf)

# print out the most and least similar countries in terms of quality profile
st.subheader(st.session_state["country"] )
similarity_vector = get_cosine_similarity(quality_df[QUALITY_MEASURES])[st.session_state["country"]].sort_values(ascending=False)
most_similar = similarity_vector.index[1:5]
least_similar = similarity_vector.index[-3:]

st.caption("Most Similar")
st.success(", ".join(most_similar.values))
st.caption("Least Similar")
st.error(", ".join(least_similar.values))
st.markdown("""---""")

# plot the altitude chart
altitude_median_all = quality_df["ALTITUDE_MEAN_METERS"].median()
altitude, altitude_low, altitude_high =\
     get_altitudes(quality_df, st.session_state["country"])
altitude_fig = plot_altitude(st.session_state["country"], altitude, altitude_low, altitude_high, altitude_median_all)
st.pyplot(altitude_fig )

# make expander with the aggregated table to be downloaded if needed
with st.expander("Aggregated ☕️ Profile Table"):
    st.caption("Click on the column names to sort by that column.")
    st.download_button("Download CSV", file_name='koffee_data.csv', data=convert_df(quality_df))
    st.dataframe(quality_df.iloc[:,:-3].style.text_gradient(cmap="YlOrBr"))


# ==============
#    Resources
# ==============

# finish it up with some information panels 
st.sidebar.header("Resources")
st.sidebar.info(
    """The raw data is taken from [here](https://www.kaggle.com/volpatto/coffee-quality-database-from-cqi), 
    which has been resourced from [here](https://github.com/jldbc/coffee-quality-database), 
    originally scraped from [here](https://database.coffeeinstitute.org/)! Suggestions for better or more comprehensive datasets are more than [welcome](https://github.com/syasini/koffee/issues/new)."""
    )

st.sidebar.info(
    """
    Images are from [here](https://photostockeditor.com/clip-art-vector/chemex), 
    [here](https://photostockeditor.com/clip-art-vector/steaming-coffee-top-view),
    and [here](https://openclipart.org/detail/263858/vegetation-silhouette-2).
    """
    )

st.sidebar.info(
    """
    Check out Ellie Jones's wonderful [streamlit-plotly-events](https://github.com/null-jones/streamlit-plotly-events) Streamlit Component.
    """
)