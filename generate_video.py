from dotenv import load_dotenv
load_dotenv()
from script_parser import ScriptParser
import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_video.py script_file.txt output_filename.mp4")
        return

    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    ScriptParser.parse_script(input_filename, output_filename)

if __name__ == "__main__":
    main()