import numpy as np
import math
import matplotlib.pyplot as plt
import tkinter as tk
from typing import List

class DraggablePoint():
    """
    Class to handle the points that are moved around by the user in the graph
    """

    def __init__(self, radar: str,
                 canvas: tk.Canvas,
                 ax: plt.axes,
                 angles: List[float],
                 values: List[float],
                 i: int,
                 radius: float = 0.02):
        """
        Initialize the parameters of the points and the fact that we can drag
        and drop them

        :param radar: the plot object to update (cannot pass the Radar object,
                        because of circular import)
        :type radar: str
        :param canvas: the canvas frame to draw in
        :type canvas: tk.Canvas
        :param ax: the axis to plot in
        :type ax: plt.axes
        :param angles: the list of angles of the points
        :type angles: List[float]
        :param values: the list of values of the point
        :type values: List[float]
        :param i: the index of the point
        :type i: int
        :param radius: the radius of the point, defaults to 0.02
        :type radius: float, optional
        """
        self.radar = radar
        self.ax = ax
        self.canvas = canvas
        self.i = i
        # Data coordinate is polar -> x = angle, y = r
        self.x = angles[self.i]
        self.y = values[self.i]
        self.point, = ax.plot(self.x, self.y, 'ro', markersize=radius*400, alpha=0.7, picker=5)
        self.angles = angles
        self.values = values
        self.radius = radius
        self.dragging = False
        self.canvas.mpl_connect('button_press_event', self.on_pick)
        self.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.canvas.mpl_connect('button_release_event', self.on_release)

    def retrieve_col(self) -> float:
        """
        Retrieve the column where the point is dragged

        :return: the column position
        :rtype: float
        """
        return self.x*len(self.radar.cols)/(2*np.pi)

    def on_pick(self, event: tk.Event) -> None:
        """
        Show the distribution of values when a point is clicked

        :param event: when the point is first clicked
        :type event: tk.Event
        """
        if event.ydata is None:
            event.ydata = 1.0
        if event.xdata is not None:
            first_condition = math.isclose(event.xdata, self.x, abs_tol= 0.1)
            second_condition = math.isclose(2*np.pi+event.xdata, self.x, abs_tol= 0.1)
            third_condition = math.isclose(event.ydata, self.y, abs_tol= 0.1)
            fourth_condition = math.isclose(event.ydata, 0, abs_tol=0.1)
            fifth_condition = math.isclose(self.y, 0, abs_tol=0.1)
            first_combined_condition = ((first_condition or second_condition) and third_condition)
            second_combined_condition = (fourth_condition and fifth_condition)
            if first_combined_condition or second_combined_condition:
                self.dragging = True
                self.x0 = event.xdata
                self.y0 = event.ydata
                # Make the point continue to respond to pick events
                self.point.set_picker(True)

    def on_drag(self, event: tk.Event) -> None:
        """
        Show teh histogram of values and change point's position when the point
        is dragged

        :param event: when the point is dragged
        :type event: tk.Event
        """
        if self.dragging:
            if event.ydata is None:
                event.ydata = 1.0
            dy = event.ydata - self.y0
            self.y += dy
            self.point.set_data(self.x, self.y)
            self.values[self.i] = self.y
            self.canvas.draw_idle()
            self.y0 = event.ydata
            self.radar.show_histogram(self.i)
            self.radar.update_plot_line()

    def on_release(self, event: tk.Event) -> None:
        """
        Remove the histogram of the distribution when you release the button

        :param event: when the point is released
        :type event: tk.Event
        """
        if self.dragging:
            self.dragging = False
            # Reset the point's picker radius
            self.point.set_picker(5)
            i = round(self.retrieve_col())
            self.radar.change_value(i)
            self.radar.remove_histogram(i)
