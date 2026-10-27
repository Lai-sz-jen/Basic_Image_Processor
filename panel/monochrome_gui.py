from tkinter import N, S, E, W, NSEW, HORIZONTAL, IntVar
from tkinter import ttk
from .gui_element.menu import Menu
from .gui_element.histogram import Histogram
from collections.abc import Callable

class MonochromeGUI(ttk.Frame):
    def __init__(self,
                 root,
                 preview_mono: Callable,
                 apply: Callable,
                 restore: Callable):
        super().__init__(root)
        self.__preview: Callable = preview_mono
        self.__apply: Callable = apply
        self.__restore: Callable = restore

        self.__threshold: IntVar = IntVar(value=128)

        ## Styling
        style = ttk.Style()
        style.configure("testing.TFrame", background="lightgray")
        self.config(style="testing.TFrame")

        ## Create Widgets
        ttk.Label(self, text="Adjust threshold here:").grid(column=0, row=0, sticky=(E, W))

        self.hist = Histogram(self)
        self.hist.grid(column=0, row=1, sticky=NSEW)

        self.slider = ttk.Scale(self,
                                from_=0,
                                to=255,
                                variable=self.__threshold,
                                command=self.point_to,
                                orient=HORIZONTAL)

        self.slider.grid(column=0, row=2, sticky=(E, W))

        self.threshold_label = ttk.Label(self, textvariable=self.__threshold, anchor=E, width=3)
        self.threshold_label.grid(column=0, row=3, sticky=N)

        self.apply_menu = Menu(self, [("Apply", self.apply_mono), ("Cancel", self.abandon)], style="testing.TFrame")
        self.apply_menu.grid(column=0, row=4, sticky=(N, S), pady= 5)

        self.rowconfigure(1, weight=1)


    def point_to(self, threshold: str) -> None:
        t: int = int(threshold.split('.')[0])
        self.__threshold.set(value=t)

        self.hist.point_to(t)
        self.threshold_label.config(text=str(t))
        self.__preview(t)

    def apply_mono(self):
        t: int = self.__threshold.get()

        self.__apply(threshold=t)
        self.grid_remove()

    def abandon(self):
        self.__restore()
        self.grid_remove()

    def render_hist(self, bins: list[int]) -> None:
        self.hist.show(bins)