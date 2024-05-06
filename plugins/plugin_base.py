from abc import ABC
from rich.console import Console
import os


class PluginBase(ABC):

    def __load_characters(self, config):
        console = Console()
        character_data = config.get('characters', [])

        if character_data:
            console.print("[grey] loading character data")

        self.characters = {}
        for character in character_data:
            name = character.get('name', '')
            if not name:
                console.print(
                    "\n[bold red]Error: `name` of character is required.")
                raise ValueError("name of character is required.")
            else:
                self.characters[name] = {}

            voice = character.get('voice', '')
            if voice:
                self.characters[name]["voice"] = voice

            image = character.get('image', '')
            if image:
                if os.path.exists(image):
                    self.characters[name]["image"] = image
                else:
                    raise FileNotFoundError(image)

    def __init__(self, config):
        self.config = config
        self.validate_config()

        global_config = config.get("global", {})
        self.width = global_config.get("width", 0)
        self.height = global_config.get("height", 0)
        self.use_cuda = global_config.get("use_cuda", False)
        if self.use_cuda == "true":
            self.use_cuda = True
        else:
            self.use_cuda = False

    def get_character_data(self, line):
        character_name = line.split(":")[0].strip()
        character = self.characters.get(character_name, "")
        if character:
            voice = character.get("voice", "")
            image = character.get("image", "")
            return voice, image
        else:
            return "",""

    def validate_config(self):
        console = Console()
        global_config = self.config.get("global", {})

        if "width" not in global_config or "height" not in global_config:
            console.print(
                "\n[bold red]Error: Width and height must be present.")
            raise ValueError(
                "Width and height must be present in the configuration.")

        if not isinstance(global_config["width"], (int, float)) or not isinstance(global_config["height"], (int, float)):
            console.print(
                "\n[bold red]Error: Width and height must be numbers.")
            raise ValueError("Width and height must be numerical values.")

        if global_config["width"] <= 0 or global_config["height"] <= 0:
            console.print(
                "\n[bold red]Error: Width and height must be positive.")
            raise ValueError("Width and height must be positive numbers.")

        if global_config["use_cuda"] not in ["true", "false"]:
            console.print(
                "\n[bold red]Error: use_cuda must be 'true' or 'false' (case-sensitive).")
            raise ValueError(
                "use_cuda must be 'true' or 'false' (case-sensitive).")

        self.__load_characters(global_config)
