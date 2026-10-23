from abc import abstractmethod
from typing import Any
from .interface import Transform
from PIL import Image
import numpy as np
from math import radians, sin, cos

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

        self._default |= {"delta_x": 0,
                          "delta_y": 0}

    def _preview_shape(self, height_0: int, width_0: int, channel: int = 3, **kwargs) -> tuple[int, int, int]:
        return (height_0 + abs(kwargs["delta_y"]),
                width_0 + abs(kwargs["delta_x"]),
                channel)

    def _config(self, **kwargs) -> None:
        ## Fetching Parameters
        delta_x: int = kwargs["delta_x"]
        delta_y: int = kwargs["delta_y"]

        ## Building Affine Matrix
        affine: np.ndarray = np.identity(3, dtype=np.double)
        if delta_x > 0:
            affine[0, 2] = delta_x
        if delta_y > 0:
            affine[1, 2] = delta_y

        ## Find Inverse of Affine Matrix
        inverse: np.ndarray = np.identity(3, dtype=np.double)
        inverse[0, 2] = -affine[0, 2]   #  R1 += -(R3 * delta_x)
        inverse[1, 2] = -affine[1, 2]   #  R2 += -(R3 * delta_y)

        self._inverse = inverse


class Reflection(Affine):
    def __init__(self):
        super().__init__()

        self._default |= {"invert_x": False,
                          "invert_y": False}

    def _preview_shape(self, height_0: int, width_0: int, channel: int=3, **kwargs) -> tuple[int, int, int]:
        return height_0, width_0, channel

    def _config(self, **kwargs) -> None:
        ## Building Affine Matrix
        affine: np.ndarray = np.identity(3, dtype=np.double)

        if kwargs["invert_x"]:
            affine[0, 0] = -1
            affine[0, 2] = kwargs["width"] - 1
        if kwargs["invert_y"]:
            affine[1, 1] = -1
            affine[1, 2] = kwargs["height"] - 1


        ## Find Inverse of Affine Matrix
        inverse: np.ndarray = np.identity(3, dtype=np.double)
        if kwargs["invert_x"]:
            inverse[0, 2] = -affine[0, 2]   # R1 += -(R3 * delta_x)
            inverse[0] *= -1                # R1 *= -1
        if kwargs["invert_y"]:
            inverse[1, 2] = -affine[1, 2]   # R2 += -(R3 * delta_y)
            inverse[1] *= -1                # R2 *= -1

        self._inverse = inverse

class Scaling(Affine):
    def __init__(self):
        super().__init__()

        self._default |= {"scale_x": 1,
                          "scale_y": 1}

    def _preview_shape(self, height_0: int, width_0: int, channel: int=3, **kwargs) -> tuple[int, int, int]:
        return (round(height_0 * kwargs["scale_y"]),
                round(width_0 * kwargs["scale_x"]),
                channel)

    def _config(self, **kwargs) -> None:
        ## Fetch Parameters
        scale_x: float = kwargs["scale_x"]
        scale_y: float = kwargs["scale_y"]
        if abs(scale_x) < 1e-6:
            raise ValueError(f"'scale_x' must not be 0")
        if abs(scale_y) < 1e-6:
            raise ValueError(f"'scale_y' must not be 0")


        ## Building Affine Matrix
        affine: np.ndarray = np.identity(3, dtype=np.double)
        affine[0, 0] = scale_x
        affine[1, 1] = scale_y

        ## Find Inverse of Affine Matrix
        inverse: np.ndarray = np.identity(3, dtype=np.double)
        inverse[0, 0] = 1 / affine[0, 0]
        inverse[1, 1] = 1 / affine[1, 1]

        self._inverse = inverse


class Shearing(Affine):
    def __init__(self):
        super().__init__()

        self._default |= {"shear_x": 0,
                          "shear_y": 0}

    def _preview_shape(self, height_0: int, width_0: int, channel: int=3, **kwargs) -> tuple[int, int, int]:
        shear_x: float = abs(kwargs["shear_x"])
        shear_y: float = abs(kwargs["shear_y"])

        width_1: int = width_0 + round(height_0 * shear_x)      # apply on x first
        height_1: int = height_0 + round(width_1 * shear_y)     # apply on y later
        return height_1, width_1, channel

    def _config(self, **kwargs) -> None:
        ## Fetching Parameters
        shear_x: float = kwargs["shear_x"]
        shear_y: float = kwargs["shear_y"]
        h_0: int = kwargs["height"]
        w_0: int = kwargs["width"]
        h_1, w_1, _ = self._preview_shape(h_0, w_0, shear_x=shear_x, shear_y=shear_y)

        ## Building Affine Matrix
        affine_x: np.ndarray = np.identity(3, dtype=np.double)
        affine_x[0, 1] = shear_x
        if shear_x < 0:
            affine_x[0, 2] = w_1 - w_0

        affine_y: np.ndarray = np.identity(3, dtype=np.double)
        affine_y[1, 0] = shear_y
        if shear_y < 0:
            affine_y[1, 2] = h_1 - h_0
        #affine: np.ndarray = affine_y @ affine_x    # apply on x first

        ## Find Inverse of Affine Matrix
        inverse_x: np.ndarray = np.identity(3, dtype=np.double)
        inverse_y: np.ndarray = np.identity(3, dtype=np.double)

        inverse_x[0, 1] = -affine_x[0, 1]   # R1 += shear_x * R2
        inverse_x[0, 2] = -affine_x[0, 2]   # R1 -= delta_x * R3
        inverse_y[1, 0] = -affine_y[1, 0]   # R2 += shear_y * R1
        inverse_y[1, 2] = -affine_y[1, 2]   # R2 -= delta_y * R3

        self._inverse = inverse_x @ inverse_y   # apply on y first when reversed


class Rotation(Affine):
    def __init__(self):
        super().__init__()

        self._default |= {"degree": 0}

    def _preview_shape(self, height_0: int, width_0: int, channel: int=3, **kwargs) -> tuple[int, int, int]:
        degree: float = kwargs["degree"]
        degree %= 180                           # rotating 180 degree reset the shape; also set degree to range [0, 180]
        degree = min(degree, 180 - degree)      # rotating an angle required the same shape as rotating (180 - angle)

        rad: float = radians(degree)
        h_1: int = round(width_0 * sin(rad) + height_0 * cos(rad))
        w_1: int = round(width_0 * cos(rad) + height_0 * sin(rad))
        return h_1, w_1, channel

    def _config(self, **kwargs) -> None:
        ## Fetching Parameters
        degree: float = kwargs["degree"]
        degree = -degree    # invert y-axis to match image display convention
        degree %= 360       # set to range [0, 360]
        rad: float = radians(degree)

        w_0: int = kwargs["width"]
        h_0: int = kwargs["height"]

        ## Building Affine Matrix
        rotate: np.ndarray = np.array([[cos(rad), -sin(rad), 0],
                                       [sin(rad), cos(rad), 0],
                                       [0, 0, 1]],
                                      dtype=np.double)
        corner: np.ndarray = np.array([[0, 0, w_0-1, w_0-1],
                                       [0, h_0-1, h_0-1, 0],
                                       [1, 1, 1, 1]],
                                      dtype=np.double)
        corner = rotate @ corner

        shift: np.ndarray = np.array([[1, 0, -corner[0].min()],
                                      [0, 1, -corner[1].min()],
                                      [0, 0, 1]],
                                     dtype=np.double)

        # affine: np.ndarray = shift @ rotate   # apply rotation first

        ## Finding the Inverse of Affine Matrix
        # the reverse operation of rotating rad is rotating (-rad)
        rotate[0, 1] = -rotate[0, 1]
        rotate[1, 0] = -rotate[1, 0]

        shift[0, 2] = -shift[0, 2]
        shift[1, 2] = -shift[1, 2]

        self._inverse = rotate @ shift      # apply shifting first when reversed
