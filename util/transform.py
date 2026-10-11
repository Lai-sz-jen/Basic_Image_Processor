from PIL import Image
from abc import ABC, abstractmethod
import numpy as np


class Transform(ABC):   # Interface
    @abstractmethod
    def apply(self, img: Image.Image, **kwargs) -> Image.Image:
        pass

    @abstractmethod
    def config(self, **kwargs) -> None:
        pass


class GrayScale(Transform):
    # @override
    def apply(self, img: Image.Image, **kwargs) -> Image.Image:
        arr: np.ndarray = np.array(img)
        gray = self._apply_as_arr(arr)
        return Image.fromarray(gray)

    # @override
    def config(self, **kwargs) -> None:
        return


    @staticmethod
    def _apply_as_arr(arr: np.ndarray) -> np.ndarray:
        height, width, _ = arr.shape
        gray = np.zeros((height, width, 3), dtype=np.uint8)
        gray[:,:,0] = np.round(arr[:,:,0] * 0.2126 + arr[:,:,1] * 0.7152 + arr[:,:,2] * 0.0722)
        gray[:,:,1] = gray[:,:,0]
        gray[:,:,2] = gray[:,:,0]
        return gray


class Monochrome(GrayScale):
    def __init__(self, img: Image.Image, threshold: int=128):
        self.__cached = None
        self.gray = None
        self.renew_cache(img)

        self.threshold = threshold

    # @override
    def apply(self, img: Image.Image, **kwargs) -> Image.Image:
        default: dict = {"renew": False}
        kwargs = default | kwargs

        if img is not self.__cached or kwargs["renew"]:
            self.renew_cache(img)

        mono: np.ndarray = np.where(self.gray >= self.threshold, 255, 0).astype(dtype=np.uint8)
        return Image.fromarray(mono)

    def config(self, **kwargs) -> None:
        self.threshold = kwargs.get("threshold", self.threshold)


    def renew_cache(self, img: Image.Image) -> None:
        self.__cached = img
        arr: np.ndarray = np.array(img)
        self.gray = super()._apply_as_arr(arr)


class Negative(Transform):
    # @override
    def apply(self, img: Image.Image, **kwargs) -> Image.Image:
        arr: np.ndarray = np.array(img)
        arr = 255 - arr
        return Image.fromarray(arr)

    def config(self, **kwargs) -> None:
        return


if __name__ == "__main__":
    image = Image.open("Munich.png").convert("RGB")
    #image = GrayScale().apply(image)
    #image = Monochrome(image).apply(image)
    image = Negative().apply(image)

    image.save("altered.png")

