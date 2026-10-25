from tkinter import N, S, E, W, NSEW, CENTER
from tkinter.ttk import Frame, Button, Separator, Style
from collections.abc import Callable


class Menu(Frame):
    def __init__(self,
                 root,
                 button: list[list[tuple[str, Callable]]] | list[tuple[str, Callable]],
                 **kwargs):
        ## Data Cleaning
        if not button:
            return
        elif not isinstance(button[0], list):
            button = [button]

        ## Setup Frame
        super().__init__(root)
        kwargs = {"height": "3c"} | kwargs
        self.config(**kwargs)

        ## Button Config
        pad = 4     # space between buttons
        style = Style()
        f_style: str = kwargs.get("style", "")
        if f_style:
            style.configure("given.TButton", background = style.lookup(f_style, "background"))


        ## Layout
        column: int = 0
        for i, group in enumerate(button):
            for text, callback in group:
                b = Button(self, text=text, command=callback)
                b.config(style="given.TButton")
                b.grid(column=column, row=0, padx=pad, ipady=3, sticky=(E, W))
                column += 1

            if i < len(button) - 1:
                Separator(self, orient="vertical").grid(column=column, row=0, padx=pad, sticky=(N, S))
                column += 1


if __name__ == '__main__':
    import tkinter as tk

    void = lambda :print("pressed")
    bttn = [[("option", void), ("option", void)],
            [("option", void), ("option", void), ("option", void), ("option", void)],
            [("option", void)]]

    app = tk.Tk()
    Menu(app, bttn).grid()
    app.mainloop()