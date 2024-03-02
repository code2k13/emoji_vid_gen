
from abc import ABC, abstractmethod
from typing import Dict


class BaseTxt2Img(ABC):
    def __init__(self, width: int, height: int):
        self.height = height
        self.width = width

    @abstractmethod
    def generate_images(self, script_file: str) -> Dict[str, str]:
        pass
