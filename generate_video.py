from dotenv import load_dotenv
load_dotenv()
from utils.script_parser import ScriptParser
import sys
from rich.traceback import install
install(show_locals=False)

def main():
    
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print("Usage: python generate_video.py script_file.txt output_filename.mp4 [--preset <preset_name>]")
        return

    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    preset = "local_basic"  
    preset_index = sys.argv.index("--preset") if "--preset" in sys.argv else None
    if preset_index is not None and preset_index + 1 < len(sys.argv):
        preset = sys.argv[preset_index + 1]

    preset_file_path = f"./presets/{preset}.yaml"
    ScriptParser.parse_script(input_filename, output_filename, preset_file_path)

if __name__ == "__main__":
    main()
