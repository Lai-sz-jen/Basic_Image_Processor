from abc import abstractmethod
from interface import Transform
from PIL import Image
import numpy as np

class Affine(Transform):
    def __init__(self):
        self.__inverse: np.ndarray = np.array([[1, 0, 0],
                                               [0, 1, 0],
                                               [0, 0, 1]],
                                             dtype=np.double)    # initialize as Identity Matrix


    @staticmethod
    @abstractmethod
    def _get_result_shape(height_0: int, width_0: int, channel: int=3) -> tuple[int, int, int]:
        pass

    @staticmethod
    def _bilinear_interpolation(adjacent_pixels: np.ndarray,
                                point: np.ndarray) -> np.ndarray:
        """
        Getting the RGB values of a non-discrete point on an image using bilinear interpolation.

        :param adjacent_pixels: a submatrix of the image containing the 4 adjacent pixels RGB values.
        :param point: the non-discreate point's offset from the top-left pixel as a vector, delta_x first.
        :return: the resulting RGB value.
        """
        def interpolate(endpoint: np.ndarray,
                        d: float) -> np.ndarray[tuple[int], np.dtype[np.double]]:
            """
            Getting the RGB values of a non-discrete point on a line using linear interpolation.

            :param endpoint: a matrix containing the 2 adjacent pixels RGB values.
            :param d: the non-discreate point's distance to the first endpoint
            :return: the resulting RGB value.
            """
            delta: np.ndarray = endpoint[1] - endpoint[0]
            return endpoint[0] + delta * d

            # an + bm = an + (a + (b-a)) * m
            #         = a (n+m) + (b-a) * m
            #         = a + (b-a) * m

        delta_x, delta_y = point
        adjacent_pixels = adjacent_pixels.astype(np.double)

        top: np.ndarray = interpolate(adjacent_pixels[0], delta_x)
        bottom: np.ndarray = interpolate(adjacent_pixels[1], delta_x)
        result: np.ndarray = interpolate(np.array([top, bottom], dtype=np.double),
                                         delta_y)

        return np.round(result).astype(np.uint8)

    def apply(self, img: Image.Image, **kwargs) -> Image.Image:
        arr: np.ndarray = np.array(img)
        h_0, w_0, c = arr.shape
        h_1, w_1, c = self._get_result_shape(h_0, w_0)
        result: np.ndarray = np.zeros((h_1, w_1, c), dtype=np.uint8)

        for y in range(h_1):
            for x in range(w_1):
                coord: np.ndarray = np.array([x, y, 1], dtype=np.double)
                mapping: np.ndarray = (self.__inverse @ coord)[:2]
                left, top = np.floor(mapping).astype(np.int32)

                if left < 0 or left > w_0 - 2:
                    continue
                elif top < 0 or top > h_0 - 2:
                    continue

                rgb: np.ndarray = self._bilinear_interpolation(arr[top: top+2, left: left+2], mapping % 1)
                result[y, x] = rgb

        return Image.fromarray(result)


class Identity(Affine):
    @staticmethod
    def _get_result_shape(height_0: int, width_0: int, channel: int=3) -> tuple[int, int, int]:
        return height_0, width_0, channel

    def config(self, **kwargs) -> None:
        return


if __name__ == "__main__":
    image = Image.open("Munich.png").convert("RGB")
    image = Identity().apply(image)

    image.save("altered.png")


