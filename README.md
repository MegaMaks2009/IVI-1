# IVI V1
Fast offline voice-controlled app launcher for Windows.

## How to install?
1. Download the project.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Run the program:
   `python main.py`

## How to use?
1. IVI listens to your microphone and recognizes English voice commands.
2. To open a program: say "open" or "close" and program name, for example: open chrome.
3. Say "exit" or press "Ctrl+C" to close IVI
4. `programs.json` contains the names IVI can recognize and the paths to the programs. The left side is what you say: "chrome", The right side is the path to the program: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe".
