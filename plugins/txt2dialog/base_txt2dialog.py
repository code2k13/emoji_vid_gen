
from abc import abstractmethod
from typing import Literal
from plugins.plugin_base import PluginBase

class BaseText2Dialog(PluginBase):

    def __init__(self, config):
        super().__init__(config)

    @abstractmethod
    def create_dialog(self, image_path, text: str, type: Literal["text", "emoji"] = "text")-> str:
        pass
