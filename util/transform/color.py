from .interface import Transform
from PIL import Image
import numpy as np

class GrayScale(Transform):
    # @override
    def apply(self, img: Image.Image, **kwargs) -> Image.Image:
        arr: np.ndarray = np.array(img)
        gray = self._apply_as_arr(arr)
        return Image.fromarray(gray)


    @staticmethod
    def _apply_as_arr(arr: np.ndarray) -> np.ndarray:
        height, width, _ = arr.shape
        gray = np.zeros((height, width, 3), dtype=np.uint8)
        gray[:,:,0] = np.round(arr[:,:,0] * 0.2126 + arr[:,:,1] * 0.7152 + arr[:,:,2] * 0.0722)
        gray[:,:,1] = gray[:,:,0]
        gray[:,:,2] = gray[:,:,0]
        return gray


class Monochrome(Transform):
    # @override
    def apply(self, img: Image.Image, **kwargs) -> Image.Image:
        """
        :param img: any grayscale image in RGB mode
        :param kwargs:
            threshold: an integer in range [0, 255]
            gray_arr: a 3d ndarray representing a grayscale image, either 1 channel or 3 channel will do.
        :return: converted image
        """
        default: dict = {"threshold": 128,
                         "gray_arr": None   # this should be in RGB mode
                         }
        kwargs = default | kwargs

        threshold: int = kwargs["threshold"]
        if kwargs["gray_arr"] is not None:
            arr: np.ndarray = kwargs["gray_arr"]
        else:
            arr: np.ndarray = np.array(img)

        mono: np.ndarray = np.where(arr >= threshold, np.uint8(255), np.uint8(0))
        h, w, _ = mono.shape
        return Image.fromarray(np.broadcast_to(mono[:,:,:1], (h, w, 3)))


class Negative(Transform):
    # @override
    def apply(self, img: Image.Image, **kwargs) -> Image.Image:
        arr: np.ndarray = np.array(img)
        arr = 255 - arr
        return Image.fromarray(arr)




if __name__ == "__main__":
    image = Image.open("../Munich.png").convert("RGB")
    image = GrayScale().apply(image)
    image = Monochrome().apply(image, gray_arr=np.array(image))
    #image = Negative().apply(image)

    image.save("altered.png")