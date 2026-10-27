from tkinter import BooleanVar, N, S, E, W
from tkinter import ttk
from .gui_element.menu import Menu
from collections.abc import Callable

class ReflectGUI(ttk.Frame):
    def __init__(self,
                 root,
                 preview: Callable,
                 apply: Callable,
                 abort: Callable):
        super().__init__(root)
        self.__preview: Callable = preview
        self.__apply: Callable = apply
        self.__abort: Callable = abort

        self.__inv_x = BooleanVar(value=False)
        self.__inv_y = BooleanVar(value=False)

        ## Styling
        style = ttk.Style()
        style.configure("testing.TFrame", background="lightgray")
        self.config(style="testing.TFrame")

        ## Create Widgets
        ttk.Label(self, text="Select direction here:").grid(column=0, row=0, sticky=(E, W))
        ttk.Checkbutton(self,
                        text="left-right",
                        variable=self.__inv_x,).grid(column=0, row=1, sticky=W)
        ttk.Checkbutton(self,
                        text="top-bottom",
                        variable=self.__inv_y, ).grid(column=0, row=2, sticky=W)

        self.apply_menu = Menu(self, [("Apply", self.apply), ("Cancel", self.abort)], style="testing.TFrame")
        self.apply_menu.grid(column=0, row=4, sticky=(N, S), pady=5)


    def apply(self):
        self.__apply(invert_x=self.__inv_x.get(),
                     invert_y=self.__inv_y.get())
        self.grid_remove()

    def abort(self):
        self.__abort()
        self.grid_remove()
