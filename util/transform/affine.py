from abc import abstractmethod
from typing import Any
from .interface import Transform
from PIL import Image
import numpy as np

class Affine(Transform):
    def __init__(self):
        self._inverse: np.ndarray = np.identity(3, dtype=np.double)    # initialize as Identity Matrix
        self._default: dict[str, Any] = {"background": (0, 0, 0)}


    @abstractmethod
    def _preview_shape(self, height_0: int, width_0: int, channel: int=3, **kwargs) -> tuple[int, int, int]:
        pass

    @abstractmethod
    def _config(self, **kwargs) -> None:
        pass

    @staticmethod
    def _bilinear_interpolation(src_arr: np.ndarray,
                                mapping: np.ndarray,
                                background: np.ndarray) -> np.ndarray:
        """
        Getting the RGB values of a non-discrete point on an image using bilinear interpolation.

        :param src_arr: a 3D tensor containing the source image pixels' value
        :param mapping: a 2D matrix with each column being the coordinates of a point
        :param background: the color to fill when pixel can't map back to src_arr
        :return the interpolated pixels; a matrix with each row being a rgb value
        """
        def interpolate(a: np.ndarray,
                        b: np.ndarray,
                        d: np.ndarray) -> np.ndarray:
            """
            Getting the RGB values of a non-discrete point on a line using linear interpolation.

            :param a: contain the value of one endpoint; vectorized
            :param b: contain the value of the other endpoint; vectorized
            :param d: the normalized distance between point a and the point to interpolate to; vectorized
            :return the interpolated pixels; vectorized
            """
            delta: np.ndarray = b - a
            return a + delta * d[:, np.newaxis]

            # a(d-1) + bd = a*(d-1) + (a+(b-a))*d
            #             = a*1     + (b-a)*d
            #             = a + (b-a)*d

        ## Hyperparameter
        h, w, _ = src_arr.shape

        ## Precalculate Parameters
        x_0: np.ndarray = np.floor(mapping[0]).astype(np.int32)
        x_1: np.ndarray = x_0 + 1
        y_0: np.ndarray = np.floor(mapping[1]).astype(np.int32)
        y_1: np.ndarray = y_0 + 1
        alpha: np.ndarray = mapping[0] - x_0
        beta: np.ndarray = mapping[1] - y_0

        # clip to avoid index out of bound
        x_0 = x_0.clip(0, w - 1)
        x_1 = x_1.clip(0, w - 1)
        y_0 = y_0.clip(0, h - 1)
        y_1 = y_1.clip(0, h - 1)

        ## Fetch 4 Adjacent Pixels
        pixel_00: np.ndarray = src_arr[y_0, x_0].astype(np.int16)
        pixel_01: np.ndarray = src_arr[y_1, x_0].astype(np.int16)
        pixel_10: np.ndarray = src_arr[y_0, x_1].astype(np.int16)
        pixel_11: np.ndarray = src_arr[y_1, x_1].astype(np.int16)

        ## Bilinear Interpolation
        top: np.ndarray = interpolate(pixel_00, pixel_10, alpha)
        bottom: np.ndarray = interpolate(pixel_01, pixel_11, alpha)
        result: np.ndarray = interpolate(top, bottom, beta)

        ## Fill Background
        invalid = (mapping[0] < 0) | (mapping[0] > w) | (mapping[1] < 0) | (mapping[1] > h)
        result = np.where(invalid[:, np.newaxis], background, result)
        return np.round(result).astype(np.uint8)

    def _apply(self, arr: np.ndarray,
               bg: np.ndarray,
               **kwargs) -> np.ndarray[tuple[int, int, int], np.dtype[np.uint8]]:
        h_0, w_0, c = arr.shape
        h_1, w_1, c = self._preview_shape(h_0, w_0, **kwargs)

        self._config(height=h_0, width=w_0, **kwargs)

        ## Map destination pixels to point of original image
        inverse: np.ndarray = self._inverse
        y_index, x_index = np.indices((h_1, w_1), dtype=np.float64, sparse=False)
        mapping: np.ndarray = np.vstack((x_index.ravel(), y_index.ravel(), np.ones(h_1 * w_1, dtype=np.float64)))
        mapping = inverse @ mapping

        ## Construct Final Image
        flat: np.ndarray = self._bilinear_interpolation(arr, mapping, bg)
        result: np.ndarray = flat.reshape(h_1, w_1, c)
        return result

    def apply(self, img: Image.Image, **kwargs) -> Image.Image:
        kwargs = self._default | kwargs

        background: tuple[int, int, int] = kwargs.pop("background")

        arr: np.ndarray = np.array(img)
        result = self._apply(arr, np.array(background, dtype=np.uint8), **kwargs)
        return Image.fromarray(result)


class Identity(Affine):
    def _preview_shape(self, height_0: int, width_0: int, channel: int = 3, **kwargs) -> tuple[int, int, int]:
        return height_0, width_0, channel

    def _config(self, **kwargs) -> None:
        return


class Translation(Affine):
    def __init__(self):
        super().__init__()

        self.__delta_x = 0
        self.__delta_y = 0

    def _preview_shape(self, height_0: int, width_0: int, channel: int = 3, **kwargs) -> tuple[int, int, int]:
        return (height_0 + abs(self.__delta_y),
                width_0 + abs(self.__delta_x),
                3)


    def _config(self, **kwargs) -> None:
        default: dict[str, int] = {"delta_x": 0,
                                   "delta_y": 0}
        kwargs = default | kwargs

        self.__delta_x = kwargs["delta_x"]
        self.__delta_y = kwargs["delta_y"]
        affine: np.ndarray = np.array([[1, 0, self.__delta_x],
                                       [0, 1, self.__delta_y],
                                       [0, 0, 1]],
                                      dtype=np.double)

        self._inverse = np.linalg.inv(affine)


if __name__ == "__main__":
    image = Image.open("Munich.png").convert("RGB")
    #image = Identity().apply(image)

    t = Translation()
    image = t.apply(image, background=(255, 255, 255))

    image.save("altered.png")


