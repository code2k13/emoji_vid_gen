
from abc import abstractmethod
from typing import Dict
from plugins.plugin_base import PluginBase

class BaseText2Audio(PluginBase):

    def __init__(self, config):
        super().__init__(config)

    @abstractmethod
    def generate_audio(self, script_file: str) -> Dict[str, str]:
        pass
