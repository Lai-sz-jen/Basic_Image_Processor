from PIL import Image
from abc import ABC, abstractmethod


class Transform(ABC):   # Interface
    @abstractmethod
    def apply(self, img: Image.Image, **kwargs) -> Image.Image:
        pass

    def _config(self, **kwargs) -> None:
        if kwargs:
            raise TypeError(f"{self.__class__.__name__} does not accept configuration arguments!")
