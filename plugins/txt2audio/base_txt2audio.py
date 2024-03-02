
from abc import ABC, abstractmethod
from typing import Dict


class BaseText2Audio(ABC):
    @abstractmethod
    def generate_audio(self, script_file: str) -> Dict[str, str]:
        pass
