from tkinter import N, S, E, W
from tkinter import ttk
from .gui_element.menu import Menu
from collections.abc import Callable

class RotateGUI(ttk.Frame):
    def __init__(self,
                 root,
                 preview: Callable,
                 apply: Callable,
                 abort: Callable):
        super().__init__(root)
        self.__preview: Callable = preview
        self.__apply: Callable = apply
        self.__abort: Callable = abort

        ## Styling
        style = ttk.Style()
        style.configure("testing.TFrame", background="lightgray")
        self.config(style="testing.TFrame")

        ## Create Widgets
        ttk.Label(self, text="Adjust angle here:").grid(column=0, row=0, columnspan=2, sticky=(E, W))

        ttk.Label(self, text="\tangle(degree)").grid(column=0, row=1, sticky=(E, W))
        self.angle = ttk.Spinbox(self,
                                 from_=-float("inf"),
                                 to=float("inf"),
                                 increment=1.0)
        self.angle.set(0.0)
        self.angle.grid(column=1, row=1)

        ttk.Label(self, text="Select background here:").grid(column=0, row=3, columnspan=2, sticky=(E, W))
        ttk.Label(self, text="\tred").grid(column=0, row=4, sticky=(E, W))
        self.red = ttk.Spinbox(self,
                               from_=0,
                               to=255,
                               increment=1)
        self.red.set(0)
        self.red.grid(column=1, row=4)

        ttk.Label(self, text="\tgreen").grid(column=0, row=5, sticky=(E, W))
        self.green = ttk.Spinbox(self,
                                 from_=0,
                                 to=255,
                                 increment=1)
        self.green.set(0)
        self.green.grid(column=1, row=5)

        ttk.Label(self, text="\tblue").grid(column=0, row=6, sticky=(E, W))
        self.blue = ttk.Spinbox(self,
                                from_=0,
                                to=255,
                                increment=1)
        self.blue.set(0)
        self.blue.grid(column=1, row=6)

        self.apply_menu = Menu(self, [("Apply", self.apply), ("Cancel", self.abort)], style="testing.TFrame")
        self.apply_menu.grid(column=0, row=10, sticky=(N, S), pady=5)

    def apply(self):
        angle = float(self.angle.get())
        red = self.clip(int(self.red.get()), 0, 255)
        green = self.clip(int(self.green.get()), 0, 255)
        blue = self.clip(int(self.blue.get()), 0, 255)

        self.__apply(degree=angle,
                     background=(red, green, blue))
        self.grid_remove()

    def abort(self):
        self.__abort()
        self.grid_remove()

    @staticmethod
    def clip(val: int, from_: int, to: int) -> int:
        assert from_ <= to
        return min(to, max(from_, val))
