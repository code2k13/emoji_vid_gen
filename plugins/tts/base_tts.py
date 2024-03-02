
from abc import ABC, abstractmethod
from typing import Dict


class BaseTTS(ABC):
    @abstractmethod
    def generate_voices(self, script_file: str) -> Dict[str, str]:
        pass
