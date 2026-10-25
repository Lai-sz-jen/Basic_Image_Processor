from tkinter import Tk, N, S, E, W, NSEW, filedialog
from tkinter import ttk
from util.image_editor import ImageEditor
from PIL import Image, ImageTk
from panel.monochrome_gui import MonochromeGUI
from panel.gui_element.menu import Menu
from pathlib import Path


class ImageEditorGUI(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)

        self.editor = None

        ## Styling Color
        style = ttk.Style()
        style.configure("main_theme.TFrame", background= "lightgray")
        self.config(style="main_theme.TFrame")

        ## Create Widgets Reference
        self.head = ttk.Label(self, text="Image Wizard", anchor='center', background="white")
        self.menu = Menu(self,
                   [[("Load", self.load_image), ("Save", self.save_image)],
                          [("Grayscale", self.to_gray), ("Monochrome", self.show_mono_ui), ("Negative", self.to_negative)],
                          [("Restore", self.restore)]],
                         style="main_theme.TFrame")
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
        self.head.config(text=Path(file_path).name)
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

        self._update_image_display(self.editor.preview("mono", threshold=threshold))

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

        ## Define Font Style
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