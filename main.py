from tkinter import Tk, N, S, E, W, NSEW, filedialog
from tkinter import ttk
from util.image_editor import ImageEditor
from PIL import Image, ImageTk
from panel.monochrome_gui import MonochromeGUI
from panel.reflect_gui import ReflectGUI
from panel.shift_gui import ShiftGUI
from panel.scale_gui import ScaleGUI
from panel.shear_gui import ShearGUI
from panel.rotate_gui import RotateGUI
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

        self.menu = ttk.Notebook(self)
        file_op: Menu = Menu(self,
                             [[("Load", self.load_image),
                               ("Save", self.save_image)],
                              [("Restore", self.restore)]],
                             style="main_theme.TFrame")
        color_op = Menu(self,
                        [("Grayscale", self.to_gray),
                         ("Monochrome", self.show_mono_ui),
                         ("Negative", self.to_negative)],
                        style="main_theme.TFrame")
        affine_op = Menu(self,
                         [("Reflect", self.show_reflect_ui),
                          ("Shift", self.show_shift_ui),
                          ("Scale", self.show_scale_ui),
                          ("Shear", self.show_shear_ui),
                          ("Rotate", self.show_rotate_ui)],
                         style="main_theme.TFrame")
        self.menu.add(file_op, text="File", sticky=NSEW)
        self.menu.add(color_op, text="Color", sticky=NSEW)
        self.menu.add(affine_op, text="Geometry", sticky=NSEW)

        self.panel = None
        self.img_label = ttk.Label(self, background="gray")

        ## Mount Widget Onto Screen
        self.head.grid(column=0, row=0, columnspan=2, sticky=(E, W))
        self.menu.grid(column=0, row=1, columnspan=2, sticky=NSEW)
        self.img_label.grid(column=1, row=2, sticky=NSEW)

        ## Define Stretching Behavior
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

    def add_panel(self, panel: ttk.Frame):
        if self.panel:
            self.panel.grid_remove()

        panel.grid(column=0, row=2, sticky=NSEW)
        self.panel = panel

    def remove_panel(self):
        if not self.panel:
            return

        self.panel.grid_remove()
        self.panel = None

    def show_mono_ui(self):
        if not self.editor:
            return

        mono_ui = MonochromeGUI(self,
                                self.mono_preview,
                                self.to_mono,
                                lambda: self._update_image_display(self.editor.cur))

        mono_ui.render_hist(self.editor.gray_histogram())
        self.add_panel(mono_ui)

    def show_reflect_ui(self):
        if not self.editor:
            return

        reflect_ui = ReflectGUI(self,
                                lambda: None,
                                self.to_reflected,
                                lambda: self._update_image_display(self.editor.cur))

        self.add_panel(reflect_ui)

    def show_shift_ui(self):
        if not self.editor:
            return

        shift_ui = ShiftGUI(self,
                            lambda: None,
                            self.to_shifted,
                            lambda: self._update_image_display(self.editor.cur))

        self.add_panel(shift_ui)

    def show_scale_ui(self):
        if not self.editor:
            return

        scale_ui = ScaleGUI(self,
                            lambda: None,
                            self.to_scaled,
                            lambda: self._update_image_display(self.editor.cur))

        self.add_panel(scale_ui)

    def show_shear_ui(self):
        if not self.editor:
            return

        shear_ui = ShearGUI(self,
                            lambda: None,
                            self.to_sheared,
                            lambda: self._update_image_display(self.editor.cur))

        self.add_panel(shear_ui)

    def show_rotate_ui(self):
        if not self.editor:
            return

        rotate_ui = RotateGUI(self,
                             lambda: None,
                             self.to_rotated,
                             lambda: self._update_image_display(self.editor.cur))

        self.add_panel(rotate_ui)

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
        self.remove_panel()


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
        self.remove_panel()

    def to_gray(self):
        if not self.editor:
            return

        self.editor.apply("gray")
        self._update_image_display(self.editor.cur)
        self.remove_panel()

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
        self.remove_panel()

    def to_reflected(self, **kwargs):
        if not self.editor:
            return

        inv_x = kwargs.get("invert_x", False)
        inv_y = kwargs.get("invert_y", False)

        self.editor.apply("reflect",
                          invert_x=inv_x,
                          invert_y=inv_y)
        self._update_image_display(self.editor.cur)
        self.remove_panel()

    def to_shifted(self, **kwargs):
        if not self.editor:
            return

        delta_x = kwargs.get("delta_x", 0)
        delta_y = kwargs.get("delta_y", 0)
        bg = kwargs.get("background", (0, 0, 0))

        self.editor.apply("shift",
                          delta_x=delta_x,
                          delta_y=delta_y,
                          background=bg)
        self._update_image_display(self.editor.cur)
        self.remove_panel()

    def to_scaled(self, **kwargs):
        if not self.editor:
            return

        scale_x = kwargs.get("scale_x", 1.0)
        scale_y = kwargs.get("scale_y", 1.0)
        bg = kwargs.get("background", (0, 0, 0))

        self.editor.apply("scale",
                          scale_x=scale_x,
                          scale_y=scale_y,
                          background=bg)
        self._update_image_display(self.editor.cur)
        self.remove_panel()

    def to_sheared(self, **kwargs):
        if not self.editor:
            return

        shear_x = kwargs.get("shear_x", 1.0)
        shear_y = kwargs.get("shear_y", 1.0)
        bg = kwargs.get("background", (0, 0, 0))

        self.editor.apply("shear",
                          shear_x=shear_x,
                          shear_y=shear_y,
                          background=bg)
        self._update_image_display(self.editor.cur)
        self.remove_panel()

    def to_rotated(self, **kwargs):
        if not self.editor:
            return

        angle = kwargs.get("degree", 0.0)
        bg = kwargs.get("background", (0, 0, 0))

        self.editor.apply("rotate",
                          degree=angle,
                          background=bg)
        self._update_image_display(self.editor.cur)
        self.remove_panel()


class App(Tk):
    def __init__(self):
        super().__init__()

        ## Define Font Style
        style = ttk.Style()
        # Configure the '.' (root) style to __apply to EVERYTHING
        style.configure('.', font=('Helvetica', 12))

        ## Create Window
        self.title("Image Wizard")
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