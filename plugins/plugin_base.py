from abc import ABC
from rich.console import Console


class PluginBase(ABC):
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
