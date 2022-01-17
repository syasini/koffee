import os
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import rc
#rc('font',**{'family':'sans-serif','sans-serif':["cm"]})
#rc("text", **{"usetex": True})

import plotly.graph_objects as go 
import streamlit as st
from koffee import IMAGE_PATH


class RadarChart:
    
    def __init__(self,
                 categories, 
                 values,
                 fill_color="k",
                 line_color="white",
                 alpha=0.9,
                 standardize=True,
                 ):
        
        self.categories = self.make_title(categories)
        self.values = self.wrap_around(values)
        self.line_color = line_color
        self.fill_color = fill_color
        self.alpha = alpha
        self.standardize= standardize
        
    
    @property
    def N(self):
        return len(self.categories)
    
    @property
    def angles(self):
        return self.wrap_around(self.get_angles())
    
    @staticmethod
    def make_title(item_list):
        """replace '_' in the list items with a blank space."""
        return list(map(lambda x: x.title().replace("_", " "), item_list))

    @staticmethod
    def wrap_around(item_list):
        """append the first element of the list as the last item"""
        assert isinstance(item_list, list)
        item_list += item_list[:1]
        return item_list
    
    def get_angles(self):
        """get the theta angles on the radar chart based on the number of input categories """
        angles = [n / float(self.N) * 2 * np.pi for n in range(self.N)]
        return angles
 
        
    def plot(self, ax=None):
        """plot radar chart of the categories and values.
        if ax is provided, the results """
        ax = ax 
        if ax is None:
            ax = plt.subplot(111, polar=True)
            
        plt.xticks(self.angles[:-1], self.categories, color='k', size=14)
        ax.tick_params(axis='x', which='major', pad=30)

        # Draw ylabels
        ax.set_rlabel_position(20)
        
        if self.standardize:
            plt.ylim(0, 1)
            plt.yticks([.5, 1.], ["0.5","1.0"], color="grey", size=10, fontname = "Helvetica" )
        else:
            plt.ylim(0, 10)
            plt.yticks([5, 10], ["5","10"], color="grey", size=10, fontname = "Helvetica" )

        #print(self.ax)
        ax.plot(self.angles, self.values, linewidth=1, linestyle='solid', color=self.line_color)
        ax.fill(self.angles, self.values, color=self.fill_color, alpha=self.alpha)

        return ax

        
def plot_coffee_cup(figsize=(6,6),
                    dpi=100, 
                    alpha=0.8,
                    extent=[-200, 200, -200, 200]
                    ):
    """Load the coffee cup background image."""

    coffee_image_path = os.path.join(IMAGE_PATH, "coffee-spoon.jpeg")

    fig = plt.figure(figsize=figsize, dpi=dpi)
    coffee_ax = fig.add_subplot(111, frameon=False)

    # load the image and plot it
    img = plt.imread(coffee_image_path)
    coffee_ax.imshow(img, extent=extent, alpha=alpha)
    
    #remove the axis ticks
    coffee_ax.set_xticks([])
    coffee_ax.set_yticks([])

    return fig


def plot_coffee_latte_art(qualities, 
                          values,
                          foam_color="white", 
                          fig=None,
                          standardize=True):
    """Plot a radar chart of coffee qualities."""

    if fig is None:
        fig = plt.figure(figsize=(6,6), dpi=100)
    
    # align the center of the chart with the coffee cup image
    center_coordinates = [.34, -0.009, 0.35, 1] 
    ax = fig.add_axes(center_coordinates, frameon=False, polar=True)

    radar = RadarChart(qualities, values, fill_color=foam_color, standardize=standardize)
    radar.plot(ax)
    return fig
    

class WorldMap:
    
    def __init__(self, locations, z, text=None, colorbar_title=None, ):
        
        self.locations = locations
        self.z = z
        self.text = text
        self.colorbar_title = colorbar_title
        self.fig = self.plot()
        self.update_layout()
        
    def plot(self, **kwargs):
        
        fig_world = go.Figure(
            data=
                go.Choropleth(
                    locations = self.locations,
                    z = self.z,
                    text = self.text,
                    colorscale = 'Solar',
                    autocolorscale=False,
                    marker_line_color='darkgray',
                    marker_line_width=1,
                    colorbar_title = self.colorbar_title,
                    hoverinfo = "all",
                    **kwargs
            )
        )
        
        return fig_world
    
    
    def update_layout(self, lon=None, lat=None, projection_type="orthographic", **kwargs):
        
        self.fig.update_layout(
            geo=dict(
                showframe=True,
                showcoastlines=False,
                projection = go.layout.geo.Projection(
                    type = projection_type,
                    scale=1
                ),
                projection_rotation=dict(lon=lon, lat=lat),
            ),

            #width=800,
            height=400,
            margin={"r":10,"t":0,"l":10,"b":50}
        )
        self.fig.data[0].colorbar.x=0.
        
        
def plot_altitude(country_name, value, low, high, pop_average):

    fig = plt.figure(figsize=(5, 10), dpi=100)

    ax = fig.add_subplot(111, polar=False, frameon=False,)
    img = plt.imread(os.path.join(IMAGE_PATH, "altitude_bg.png"))

    max_x = 6000
    max_y = 3000

    ax.imshow(img, extent=[0, max_x, 0, max_y], alpha=0.3)

    ax.axhline(value, lw=2, color="tab:blue")
    ax.fill_between(np.arange(0, max_x), low, high, alpha=0.2, color="tab:blue")
    ax.axhline(pop_average, lw=1, ls="--", color='tab:red')

    ax.text(100, value+150, f"{country_name}", fontsize=10, color="tab:blue")
    ax.text(max_x-2400, pop_average-200, f"median altitude of the population", fontsize=8, color="tab:red")
    ax.set_ylabel("Altitude [meters]")
    # Draw ylabels

    ax.set_xticks([])

    return fig 

def plot_logo():
    st.image(os.path.join(IMAGE_PATH, "logo.png"))
