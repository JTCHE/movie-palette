# About
A simple python implementation to generate a "barcode" or "palette" from any video file.

# Prerequisites
- Wand
- FFmpeg
- Inquierer

# Usage
1. Have the make-palette.py and input/ folder in the same directory 
2. Place an image sequence or a video in the output/ folder
3. Run `python make-palette.py`
4. Admire the result in the ouput/ folder

# Roadmap
- I'd love if the script could be used as a standalone script, without the need for an input/ directory, like `python make-palette.py -v VIDEO -w WIDTH -h HEIGHT ...`
- Replace the current way of sizing images (by providing a width and an aspect ratio) with setting the width and height
- Add a way to switch between an image mode (movie frames) and a swatch mode (solid colours). Currently, there are only solid colours.