from tkinter import Canvas


class Histogram(Canvas):
    def __init__(self, root, **args):
        default = {"bg": "white",
                   "width":256,
                   "height":100,
                   "highlightthickness": 0      # disabled to avoid edge clipping
                   }
        args = default | args     # merging dictionary preserving args given

        super().__init__(root, **args)

        self.curr_val: int = -1    # current indexed value
        self.hist_bin: list[int] = []
        self.width: int = int(args["width"])
        self.height:int = int(args["height"])
        self._resize_timer = None

        self.bind("<Configure>", self.__on_config)


    def show(self, hist_bin: list[int]) -> None:
        self.delete("bar")

        self.hist_bin = hist_bin
        highest: int = max(hist_bin)

        if highest == 0:
            return

        for lumi, n in enumerate(hist_bin):
            left: float = self.width * lumi / len(hist_bin)
            right: float = self.width * (lumi + 1) / len(hist_bin)
            top: int = self.height - self.height * n // highest

            self.create_rectangle(left, top, right, self.height,
                                  fill="#5599FF",
                                  outline="#5599FF",
                                  tags="bar")

    def point_to(self, threshold: int):
        # safety check
        if not self.hist_bin:
            return

        # clamping
        if threshold < 0:
            threshold = 0
        elif threshold >= len(self.hist_bin):
            threshold = len(self.hist_bin) - 1

        # erase last line
        if self.curr_val != -1:
            self.delete("index")

        # safe threshold for reference
        self.curr_val = threshold

        # draw the line
        x: int = self.width * threshold // len(self.hist_bin)
        self.create_line(x, 0, x, self.height, fill="red", tags="index")
        self.tag_raise("index")     # avoid being blocked by other elements


    def __on_config(self, event) -> None:
        if self._resize_timer is not None:
            self.after_cancel(self._resize_timer)

        self._resize_timer = self.after(100, self.__on_resize, event)


    def __on_resize(self, event) -> None:
        self.delete("all")

        self.width = event.width
        self.height = event.height
        if self.hist_bin:
            self.show(self.hist_bin)
        if self.curr_val != -1:
            self.point_to(self.curr_val)

        self._resize_timer = None


if __name__ == "__main__":
    import tkinter as tk

    window = tk.Tk()
    hist = Histogram(window)
    hist.grid(column=0, row=0, sticky=tk.NSEW)


    hist.show([1, 3, 5, 7])
    hist.point_to(255)

    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1)

    window.mainloop()