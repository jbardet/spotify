import webbrowser
import tkinter as tk
import matplotlib.pyplot as plt
import matplotlib
from typing import Tuple

def round_point_00_2(n: float) -> float:
    """
    Round the number to the nearest 0.02

    :param n: the number to round
    :type n: float
    :return: the rounded number
    :rtype: float
    """
    return round(n*50)/50

def open_url(url: str) -> None:
    """
    Open an url when a button or label is clicked

    :param url: the url string
    :type url: str
    """
    webbrowser.open_new_tab(url)

def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    try:
        rgb = (round(rgb[0]*255), round(rgb[1]*255), round(rgb[2]*255))
        return "#%02x%02x%02x" % rgb
    except TypeError:
        return rgb

def add_website_link(window: tk.Frame,
                     url: str,
                     text: str,
                     font: str,
                     side: str,
                     fg: str,
                     bg: str):
    """
    Add a link to a website

    :param window: the window where to add the link
    :type window: tk.Frame
    :param url: the url to open when the link is clicked
    :type url: str
    :param text: the text to display
    :type text: str
    :param font: the font to use
    :type font: str
    :param side: the side of the frame to put the line
    :type side: str
    :param fg: the foreground color
    :type fg: str
    :param bg: the background color
    :type bg: str
    """
    label = tk.Label(window, text= text, cursor= "hand2",
                     foreground= _from_rgb(fg), font= font, bg=_from_rgb(bg))
    label.pack(side = side, expand = True)
    label.bind("<Button-1>", lambda e: open_url(url))

def set_plot_color(fig: matplotlib.figure,
                   ax: matplotlib.axes.Axes,
                   fg_string: str) -> Tuple[matplotlib.figure, matplotlib.axes.Axes]:
    """
    Set the color of the plot

    :param fig: the figure to color
    :type fig: matplotlib.figure
    :param ax: the axis to color
    :type ax: matplotlib.axes.Axes
    :param fg_string: the foreground color
    :type fg_string: str
    :return: the figure and the axes
    :rtype: Tuple(matplotlib.figure, matplotlib.axes.Axes)
    """
    fig.set_facecolor("none")
    ax.set_facecolor("none")
    try:
        ax.spines['bottom'].set_color(fg_string)
        ax.spines['top'].set_color(fg_string)
        ax.spines['right'].set_color(fg_string)
        ax.spines['left'].set_color(fg_string)
    except KeyError:
        ax.spines['polar'].set_color(fg_string)
    ax.tick_params(axis='x', colors=fg_string)
    ax.tick_params(axis='y', colors=fg_string)
    ax.yaxis.label.set_color(fg_string)
    ax.xaxis.label.set_color(fg_string)
    ax.title.set_color(fg_string)
    return fig, ax

