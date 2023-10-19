import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import math
import time
import matplotlib.pyplot as plt

class DraggablePoint:
    def __init__(self, canvas, ax, x, y, radius=0.02):
        self.ax = ax
        self.canvas = canvas # ax.figure.canvas
        self.point, = ax.plot(x, y, 'ro', markersize=radius*200, alpha=0.7, picker=5)
        self.x = x
        self.y = y
        self.radius = radius
        self.dragging = False
        self.canvas.mpl_connect('button_press_event', self.on_pick)
        self.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.canvas.mpl_connect('button_release_event', self.on_release)

    def on_pick(self, event):
        if math.isclose(event.xdata, self.x, rel_tol= 1e-1) and math.isclose(event.ydata, self.y, rel_tol= 1e-1):
            # print("pick")
            self.dragging = True
            self.x0 = event.xdata
            self.y0 = event.ydata
            self.point.set_picker(True)  # Make the point continue to respond to pick events

    def on_drag(self, event):
        if self.dragging:
            # print("drag")
            dx = event.xdata - self.x0
            dy = event.ydata - self.y0
            # print(dx, dy)
            self.x += dx
            self.y += dy
            self.point.set_data(self.x, self.y)
            # self.point, = ax.plot(self.x, self.y, 'ro', markersize=self.radius*200, alpha=0.4, picker=5)
            # print(self.point)
            self.canvas.draw_idle()
            self.x0 = event.xdata
            self.y0 = event.ydata
            # self.canvas.draw()
            # self.canvas.show()
            # time.sleep(0.01)
            # plt.pause(0.01)

    def on_release(self, event):
        if self.dragging:
            print("release")
            # self.point, = ax.plot(event.xdata, event.ydata, 'ro', markersize=self.radius*200, alpha=0.7, picker=5)
            self.dragging = False
            # self.canvas.draw()
            # time.sleep(0.01)
            # plt.pause(0.01)
            # self.after(500, self.update)
            # self.canvas.show()
            # self.canvas.update()
            self.point.set_picker(5)  # Reset the point's picker radius

def create_draggable_points(canvas, ax):
    points = []
    for x, y in zip(np.linspace(1, 9, 5), np.random.rand(5)):
        point = DraggablePoint(canvas, ax, x, y)
        points.append(point)
    return points

# Create a tkinter window
root = tk.Tk()
root.title("Draggable Points on Graph")
plt.ion()

# Create a matplotlib figure and axis
fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)

# Plot some data (example)
x = np.linspace(0, 10, 100)
y = np.sin(x)
ax.plot(x, y, color = "b")

# Create a FigureCanvasTkAgg widget
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack()

# Create draggable points
draggable_points = create_draggable_points(canvas, ax)

# canvas.draw()
# fig.show(block=False)
# Run the tkinter main loop
root.mainloop()
