
from abc import ABC, abstractmethod
from typing import Dict
from plugins.plugin_base import PluginBase

class BaseTTS(PluginBase):
    def __init__(self, config):
        super().__init__(config)

    @abstractmethod
    def generate_voices(self, script_file: str) -> Dict[str, str]:
        pass
