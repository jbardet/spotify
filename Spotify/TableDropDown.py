import tkinter as tk
import tkinter.ttk as ttk
from typing import List, Tuple

class TableDropDown(ttk.Combobox):
    """
    Class to handle the DropDown table for playlists

    Inherited from ttk.Combobox
    """
    def __init__(self, parent: ttk.Frame, values: List[str], font: Tuple[str, int]):
        """
        Initialize the TableDropDown class

        :param parent: the frame where to put the DropDown box
        :type parent: ttk.Frame
        :param values: The values to write inside the box
        :type values: List[str]
        :param font: the font name and size
        :type font: Tuple[str, int]
        """
        self.current_table = tk.StringVar() # create variable for table
        ttk.Combobox.__init__(self, parent, font=font)#  init widget
        self.config(textvariable = self.current_table,
                    state = "readonly",
                    values = values)
        self.current(0) # index of values for current table
        self.pack(side="left") # place drop down box
