# About
A simple python implementation to generate a "barcode" or "palette" from any video file.

# Prerequisites
- [OpenCV](https://opencv.org/)
- Numpy

# Examples

# Usage
```
python make-palette.py -i inputfile.mp4 [-o outputfile.png] [-d output] [-r 1920x1080] [-a 10] [-s 00:00:00] [-e 01:20:03]
```

- ```-i``` ```--input```: The path to the input video. The supported formats are written down below.
- ```-o``` ```--output```: Optional. Output path of the final image including the filename and extension. If it's not specified, the output's filename will be the same as the input's.
- ```-d``` ```--directory```: Optional. Output directory of the final image. Can be used in conjonction or not with the ```-o``` flag. The script Will create the directory automatically.
- ```-r``` ```--resolution```: Optional. The resolution of the output image. If it's not specified, it will be set to the input's resolution. Can be set to one of the preset value listed below. It should be formatted as ```1920x1080````
- ```-a``` ```--sampling```: Optional. Default : 10. Arbitrary value for the sampling rate. Higher value means less frames will be sampled, and will result in bigger columns. The default will sample a lot of frames.
- ```-s``` ```--start```: Optional. Allows to set the start timecode. Should be formatted as ```hh:mm:ss```.
- ```-e``` ```--end```: Optional. Allows to set the end timecode, to skip credits for instance. Should be formatted as ```hh:mm:ss```.

# Supported codecs and containers
| Codec/Container | Support  |
| --------------- | -------- |
| H264            | ✅        |
| ProRes          | ✅        |
| AV1             | ✅ (Slow) |
| H265            | ➖        |
| MKV             | ❌        |

# List of preset resolutions
| Preset Name | Resolution |
| ----------- | ---------- |
| ultrawide   | 8976x3544  |
| u           | 8976x3544  |
| phone       | 1080x1920  |
| HD          | 1920x1080  |
| 2K          | 2560x1440  |
| 4K          | 3840x2160  |
| 8K          | 7680x4320  |
| 2.39        | 4096x1716  |
| 1.85        | 4096x2214  |
| 16:9        | 1920x1080  |
| A4          | 3508x2480  |
| A3          | 4960x3508  |
| A5          | 2480x1748  |
