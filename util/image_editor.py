from PIL import Image
from util.transform.transform import GrayScale, Monochrome, Negative, Transform
import numpy as np


class ImageEditor:
    def __init__(self, file_path):
        self.__cur: Image.Image
        self.__origin: Image.Image
        self.__tools: dict[str, type[Transform]] = {"gray": GrayScale,
                                                    "mono": Monochrome,
                                                    "negative": Negative}
        self.__gray_arr: np.ndarray

        self.load(file_path)


    @property
    def cur(self) -> Image.Image:
        return self.__cur


    def load(self, file_path: str) -> None:
        self.__cur = Image.open(file_path).convert("RGB")
        self.__origin = self.__cur

        gray = GrayScale().apply(self.__cur)
        self.__gray_arr: np.ndarray = np.array(gray)[:, :, :1]


    def save(self, file_path) -> None:
        if not file_path:
            return

        self.__cur.save(file_path)

    def restore(self) -> None:
        self.__cur = self.__origin

        gray = GrayScale().apply(self.__cur)
        self.__gray_arr: np.ndarray = np.array(gray)[:, :, :1]

    def apply(self, tool: str, **kwargs) -> None:
        result = self.preview(tool, **kwargs)

        if result:
            self.__cur = result

            gray = GrayScale().apply(self.__cur)
            self.__gray_arr: np.ndarray = np.array(gray)[:, :, :1]

    def preview(self, tool: str, **kwargs) -> Image.Image | None:
        if not self.__tools.get(tool, None):
            return None

        kwargs |= {"gray_arr": self.__gray_arr}
        transform: Transform = self.__tools[tool]()
        return transform.apply(self.__cur, **kwargs)

    def gray_histogram(self) -> list[int]:
        arr_1d: np.ndarray = np.array(self.__gray_arr).flatten()
        hist, _ = np.histogram(arr_1d, bins=256, range=(0, 256))
        return hist.tolist()


if __name__ == '__main__':
    ImageEditor("Munich.png")