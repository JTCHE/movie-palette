#!/usr/bin/env python3
import getopt
import os
import sys
from pathlib import Path
import cv2
import numpy
import time


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def format_eta(eta):  # Format ETA as h:mm:ss, m:ss, or s
    if eta >= 3600:
        hours = eta // 3600
        minutes = (eta % 3600) // 60
        seconds = eta % 60
        normalized_eta = f"{hours}h {minutes}m {seconds}s"
    elif eta >= 60:
        minutes = eta // 60
        seconds = eta % 60
        normalized_eta = f"{minutes}m {seconds}s"
    else:
        normalized_eta = f"{eta}s"
    return normalized_eta


def resolution_presets(resolution):
    presets = {
        "ultrawide": "8976x3544",
        "u": "8976x3544",
        "phone": "1080x1920",
        "HD": "1920x1080",
        "2K": "2560x1440",
        "4K": "3840x2160",
        "8K": "7680x4320",
        "2.39": "4096x1716",
        "1.85": "4096x2214",
        "16:9": "1920x1080",
        "A4": "3508x2480",
        "A3": "4960x3508",
        "A5": "2480x1748",
    }
    return presets.get(resolution, resolution)


def check_if_output_already_exists(output_file):
    output_file = Path(output_file)
    if output_file.exists():
        print(f"Output file '{output_file}' already exists.")
        overwrite = input("Do you want to overwrite it? (y/n): ").strip().lower()
        if overwrite != 'y':
            quit("Operation cancelled by the user.")


def write_placeholder(output_path):
    # Write a blank (black) image as a placeholder
    cv2.imwrite(output_path, True)


def time_to_frame(timestamp, fps):
    h, m, s = map(float, timestamp.split(":"))
    return int((h * 3600 + m * 60 + s) * fps)


def define_output_path(input_file, output_file, output_dir):
    # Determine output filename
    if not output_file and input_file:
        output_file = Path(input_file).with_suffix('.jpg').name
    elif output_file:
        output_file = Path(output_file).name

    # Add output directory if specified
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = str(output_dir / output_file)

    return output_file


def get_output_resolution(input_file, output_image_resolution):
    capture = cv2.VideoCapture(input_file)

    # If no input image resolution is provided, set it to the input file's resolution
    if output_image_resolution == '':
        input_file_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        input_file_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        output_image_resolution = f"{input_file_width}x{input_file_height}"

    capture.release()
    return (output_image_resolution)


def assemble_colors(colors, output_path, output_image_resolution):
    output_image_width = int(output_image_resolution.split("x")[0])
    output_image_height = int(output_image_resolution.split("x")[1])

    # Create a barcode-like palette: each color is a vertical stripe
    palette = numpy.zeros((output_image_height, output_image_width, 3), dtype=numpy.uint8)
    num_colors = len(colors)

    for i, color in enumerate(colors):
        start_x = int(i * output_image_width / num_colors)
        end_x = int((i + 1) * output_image_width / num_colors)
        palette[:, start_x:end_x] = color

    try:
        cv2.imwrite(output_path, palette)
        print(f"Successfully wrote {output_path}")
    except cv2.error as e:
        print(f"Encountered error when trying to write {output_path} : {e}")


def video_to_colors(input_file, output_file, output_image_resolution, sampling_rate, start_point, end_point):
    clear()

    try:
        capture = cv2.VideoCapture(input_file)

        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        target_width = int(output_image_resolution.split("x")[0])
        nth_frame = max(1, int(total_frames/target_width*sampling_rate))
        colors = []

        fps = capture.get(cv2.CAP_PROP_FPS)
        start_frame = time_to_frame(start_point, fps)
        end_frame = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) if end_point == '' else time_to_frame(end_point, fps)
        # Figure out what frames to process, with in and out points
        frames_to_process = list(range(start_frame, min(end_frame, total_frames), nth_frame))
        total_samples = len(frames_to_process)

        # Print header
        print(f"INPUT FILE PATH : {input_file}")
        print(f"OUTPUT FILE PATH : {output_file}")
        print(f"OUTPUT IMAGE RESOLUTION : {output_image_resolution}")
        print(f"SAMPLING 1 FRAME EVERY {nth_frame} FRAMES")
        print("—" * 50)
        print()
        print("Processing frames...")
        print()

        start_time = time.time()

        for index, frame_number in enumerate(frames_to_process):
            capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)  # Skip to a frame we know we're going to sample
            current_frame = int(capture.get(cv2.CAP_PROP_POS_FRAMES))
            sucess, frame = capture.read()

            if not sucess:
                break

            # Figure out the average color of the current frame
            average_color = numpy.mean(frame, axis=(0, 1)).astype(numpy.uint8)
            colors.append(average_color)  # Add the current color to the array

            # ETA Calculation
            elapsed_time = time.time() - start_time
            frames_left = total_samples - (index + 1)
            eta = format_eta(int((elapsed_time / (index + 1)) * frames_left) if index > 0 else 0)

            # Progress percentage calculation
            progress_percentage = ((index+1) / total_samples) * 100

            # Progress display
            sys.stdout.write(
                f"\rProgress: {progress_percentage:.1f}% | Sampling 1 frame evey {nth_frame} frames | Current Frame: {current_frame}/{end_frame} | Frames processed: {index+1}/{total_samples} | ETA: {eta}"
            )
            sys.stdout.flush()

        capture.release()

        print("\nFrame processing complete")
    except cv2.error as error:
        print(f"Encountered error when trying to process {input_file} : {error}")

    return colors


def process_video(input_file, output_file, sampling_rate, output_image_resolution, start_point, end_point):
    colors = video_to_colors(input_file, output_file, output_image_resolution, sampling_rate, start_point, end_point)
    assemble_colors(colors, output_file, output_image_resolution)


def make_palette_main():
    input_file = ''
    output_file = ''
    output_dir = './'
    output_image_resolution = ''
    sampling_rate = 10
    start_point = "00:00:00"
    end_point = ''

    try:
        # Get command line arguments, -i inputfile [-o outputfile.[png/jpg]] [-r resolution] ...
        options, argvs = getopt.getopt(sys.argv[1:], "i:o:d:r:a:s:e:", [
                                       "input=", "output=", "directory", "resolution=", "sampling=", "start=", "end="])
        for opt, arg in options:
            if opt in ("-i", "--input"):
                input_file = arg
            elif opt in ("-o", "--output"):
                output_file = arg
            elif opt in ("-d", "--directory"):
                output_dir = arg
            elif opt in ("-r", "--resolution"):
                output_image_resolution = resolution_presets(arg)
            elif opt in ("-a", "--sampling"):
                sampling_rate = int(arg)
            elif opt in ("-s", "--start"):
                start_point = arg
            elif opt in ("-e", "--end"):
                end_point = arg

        # If no input file is provided, throw an error and exit
        if not input_file:
            raise getopt.GetoptError("Error : no input provided")

        output_image_resolution = get_output_resolution(input_file, output_image_resolution)
        output_file = define_output_path(input_file, output_file, output_dir)

        check_if_output_already_exists(output_file)
        write_placeholder(output_file)

        process_video(input_file, output_file, sampling_rate, output_image_resolution, start_point, end_point)

    except getopt.GetoptError:
        print('python make-palette.py -i inputfile.mp4 [-o outputfile.jpg] [-r 1920x1080]')


if __name__ == "__main__":
    make_palette_main()
