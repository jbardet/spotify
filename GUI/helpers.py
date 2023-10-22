import webbrowser
import tkinter as tk

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

def add_website_link(window: tk.Frame, url: str, text: str, font: str, side: str) -> None:
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
    """
    label = tk.Label(window, text= text, cursor= "hand2",
                     foreground= "blue", font= font)
    label.pack(side = side)
    label.bind("<Button-1>", lambda e: open_url(url))
