from tkinter import Tk, N, S, E, W, NSEW, HORIZONTAL, filedialog
from tkinter import ttk
from util.image_editor import ImageEditor
from PIL import Image, ImageTk
from gui_element.menu import Menu
from gui_element.histogram import Histogram
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
                                value=128,
                                command=self.point_to,
                                orient=HORIZONTAL)

        self.slider.grid(column=0, row=2, sticky=(E, W))

        self.threshold_label = ttk.Label(self, text="128", anchor=E, width=3)
        self.threshold_label.grid(column=0, row=3, sticky=N)

        self.apply_menu = Menu(self, [("Apply", self.apply_mono), ("Cancel", self.abandon)], style="testing.TFrame")
        self.apply_menu.grid(column=0, row=4, sticky=(N, S), pady= 5)

        self.rowconfigure(1, weight=1)


    def point_to(self, threshold: str) -> None:
        t: int = int(threshold.split('.')[0])

        self.hist.point_to(t)
        self.threshold_label.config(text=str(t))
        self.__preview(t)

    def apply_mono(self):
        self.__apply()
        self.grid_remove()

    def abandon(self):
        self.__restore()
        self.grid_remove()

    def render_hist(self, bins: list[int]) -> None:
        self.hist.show(bins)


class ImageEditorGUI(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)

        self.editor = None

        ## test code for debugging
        #style = ttk.Style()
        #style.configure("testing.TFrame", background= "red")
        #self.config(style="testing.TFrame")

        ## Create Widgets Reference
        self.head = ttk.Label(self, text="Image Wizard", anchor='center', background="white")
        self.menu = Menu(self,
                   [[("Load", self.load_image), ("Save", self.save_image)],
                          [("Grayscale", self.to_gray), ("Monochrome", self.show_mono_ui), ("Negative", self.to_negative)],
                          [("Restore", self.restore)]])
        self.img_label = ttk.Label(self, background="gray")
        self.mono_ui = MonochromeGUI(self,
                                     self.mono_preview,
                                     self.to_mono,
                                     lambda :self._update_image_display(self.editor.cur))

        ## Mount Widget Onto Screen
        self.head.grid(column=0, row=0, columnspan=2, sticky=(E, W))
        self.menu.grid(column=0, row=1, columnspan=2, sticky=NSEW)
        self.mono_ui.grid(column=0, row=2, sticky=NSEW)
        self.mono_ui.grid_remove()  # hide temporarily
        self.img_label.grid(column=1, row=2, sticky=NSEW)

        ## Define Stretching Behavior
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

    def show_mono_ui(self):
        if not self.editor:
            return

        self.mono_ui.grid()
        self.mono_ui.render_hist(self.editor.gray_histogram())


    def _update_image_display(self, img: Image.Image):
        if not self.editor:
            return

        tk_img = ImageTk.PhotoImage(img)
        self.img_label.config(image=tk_img)
        self.img_label.img = tk_img  # keep a reference to prevent garbage collection


    def load_image(self) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if not file_path:
            return

        self.editor = ImageEditor(file_path)
        self._update_image_display(self.editor.cur)
        self.mono_ui.grid_remove()


    def save_image(self) -> None:
        if not self.editor:
            return

        file_path = filedialog.asksaveasfilename(filetypes=[("Image Files", "*.png")])
        self.editor.save(file_path)

    def restore(self):
        if not self.editor:
            return

        self.editor.restore()
        self._update_image_display(self.editor.cur)
        self.mono_ui.grid_remove()

    def to_gray(self):
        if not self.editor:
            return

        self.editor.apply("gray")
        self._update_image_display(self.editor.cur)
        self.mono_ui.grid_remove()

    def mono_preview(self, threshold: int):
        if not self.editor:
            return

        self.editor.config("mono", threshold=threshold)
        self._update_image_display(self.editor.preview("mono"))

    def to_mono(self):
        if not self.editor:
            return

        self.editor.apply("mono")
        self._update_image_display(self.editor.cur)

    def to_negative(self):
        if not self.editor:
            return

        self.editor.apply("negative")
        self._update_image_display(self.editor.cur)
        self.mono_ui.grid_remove()


class App(Tk):
    def __init__(self):
        super().__init__()

        ## Define Style
        style = ttk.Style()
        # Configure the '.' (root) style to __apply to EVERYTHING
        style.configure('.', font=('Helvetica', 12))

        ## Create Window
        self.title("Basic Image Editor")
        self.geometry("900x600")

        ## Mount GUI view
        self.gui: ImageEditorGUI = ImageEditorGUI(self)
        self.gui.grid(row=0, column=0, sticky=NSEW)

        ## Define stretching
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)


if __name__ == '__main__':
    app = App()
    app.mainloop()