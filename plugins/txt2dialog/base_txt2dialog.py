
from abc import ABC, abstractmethod
from typing import Dict
from typing import Literal

class BaseText2Dialog(ABC):
    def __init__(self, width: int, height: int):
        self.height = height
        self.width = width

    @abstractmethod
    def create_dialog(self, image_path, text: str, type: Literal["text", "emoji"] = "text")-> str:
        pass
