# About
A simple python implementation to generate a "barcode" or "palette" from any video file.

# Prerequisites
- OpenCV
- Numpy

# Usage
```python make-palette.py -i inputfile.mp4 [-o outputfile.png] [-r 1920x1080]```

# Supported codecs and containers
| Codec/Container | Support  |
| --------------- | -------- |
| H264            | ✅        |
| H265            | ➖        |
| ProRes          | ✅        |
| AV1             | ✅ (Slow) |
| MKV             | ❌        |