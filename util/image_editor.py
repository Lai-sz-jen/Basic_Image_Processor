from PIL import Image
from .transform import GrayScale, Monochrome, Transform


class ImageEditor:
    def __init__(self, file_path):
        self.__cur: Image.Image | None = None
        self.__origin: Image.Image | None = None
        self.__tools: dict[str, Transform] = {}
        self.load(file_path)

    @property
    def cur(self) -> Image.Image | None:
        return self.__cur


    def load(self, file_path: str) -> None:
        self.__cur = Image.open(file_path).convert("RGB")
        self.__origin = self.__cur
        self.__tools |= {"gray": GrayScale(),
                         "mono": Monochrome(self.__cur)}


    def save(self, file_path) -> None:
        if not self.__cur:
            return

        self.__cur.save(file_path)

    def restore(self) -> None:
        self.__cur = self.__origin

    def apply(self, tool: str) -> None:
        result = self.preview(tool)

        if result:
            self.__cur = result

    def preview(self, tool: str) -> Image.Image | None:
        if not self.__cur:
            return None

        transform: Transform | None = self.__tools.get(tool, None)
        if not transform:
            return None

        return transform.apply(self.__cur)

    def config(self, tool: str, **kwargs) -> None:
        transform: Transform | None  = self.__tools.get(tool, None)
        if transform:
            transform.config(**kwargs)

    def gray_histogram(self) -> list[int]:
        return self.__tools["mono"].hist_bins


if __name__ == '__main__':
    ImageEditor("Munich.png")