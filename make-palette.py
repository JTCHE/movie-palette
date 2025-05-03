#!/usr/bin/env python3
import os
import time
import inquirer
from wand.color import Color
from wand.image import Image
import ffmpeg
import sys
from pathlib import Path
import mimetypes
mimetypes.add_type('image/webp', '.webp')
global filename
filename = ''


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def cleanup(path):
    if Path(path).exists():
        path = path.replace("/", "\\")
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(path)


def ensure_directories(temp_dir="temp", output_dir="output"):
    """Create necessary directories if they don't exist."""
    swatches_dir = temp_dir + "/swatches"

    for directory in [temp_dir, output_dir, swatches_dir]:
        Path(directory).mkdir(exist_ok=True)

    return temp_dir, output_dir, swatches_dir


def get_average_color(image_path):
    """Extract the average color from an image."""
    with Image(filename=image_path) as img:
        # Resize to 1x1 to get average color
        img.resize(1, 1)

        # Get the color of the single pixel
        pixel = img[0, 0]

        # Format as hex color
        color = f"#{pixel.red_int8:02x}{pixel.green_int8:02x}{pixel.blue_int8:02x}"

    return color


def create_swatch(swatch_color, filename, swatches_dir):
    """Create a solid color swatch with the given color."""
    swatch_path = Path(swatches_dir) / f"{filename}.png"

    with Image(width=100, height=100, background=Color(swatch_color)) as img:
        img.format = 'png'
        img.save(filename=str(swatch_path))

    return swatch_path


def create_combined_image(
    swatches_paths, output_dir, target_width, aspect_ratio
):
    """Create a combined image from all swatches using wand."""
    global filename
    if (filename != ''):
        output_file_name = filename + ".png"
    else:
        output_file_name = "output.png"
    output_file = Path(output_dir) / output_file_name

    swatch_count = len(swatches_paths)
    target_height = int(target_width//aspect_ratio)
    swatch_width = int(target_width / swatch_count) + (target_width % swatch_count > 0)

    print("Combining images into a single canvas...")
    # Create a blank white canvas
    with Image(width=target_width, height=target_height, background=Color("black")) as canvas:
        position = 0

        for index, swatch_path in enumerate(swatches_paths, start=1):
            with Image(filename=str(swatch_path)) as swatch:
                sys.stdout.write(f"\rCombining image [{index}/{swatch_count}]")
                sys.stdout.flush()
                swatch.resize(swatch_width, target_height)
                # Composite resized swatch onto canvas
                canvas.composite(swatch, left=position, top=0)
                position += swatch_width

        canvas.format = "png"
        canvas.save(filename=str(output_file))
        print()
        print(f"Combined image created: {output_file}")

    return output_file


def video_to_sequence(input_file_path, input_file_name, temp_dir):
    if not Path(input_file_path).is_file():
        sys.exit("Input file is invalid")
    movie_frames_dir = temp_dir + "/movie_frames/"
    cleanup(movie_frames_dir)
    Path(movie_frames_dir).mkdir(exist_ok=True)

    # target_swatches_per_second = input("Target swatches per second ?")
    seconds_between_frames = 10
    target_fps = 1 / seconds_between_frames

    start = time.time()
    # Use ffmpeg to extract frames as .jpeg images
    (
        ffmpeg
        .input(input_file_path, threads=0)
        .output(
            f"{movie_frames_dir}/{input_file_name}_%05d.webp",
            q=3,
            vf=f"fps={target_fps},scale=256:-1",
            vcodec="libwebp",
        )
        .run()
    )

    clear()
    print(f"Frame extraction took {time.time() - start:.2f}s")
    input("Press Enter to continue...")
    clear()

    return movie_frames_dir


def check_input_dir(input_files):
    if not input_files:
        sys.exit("The input directory is empty")

    if len(input_files) > 1:
        input_mode = input("What mode do you want to run the script as ?[video/image]")
        return input_mode

    first_file_path = str(input_files[0])
    mime_type, _ = mimetypes.guess_type(first_file_path)

    if mime_type and mime_type.startswith('video'):
        input_mode = 'video'
    elif mime_type and mime_type.startswith('image'):
        input_mode = 'image'
    else:
        sys.exit("Unsupported file type")

    return input_mode


def pick_input_mode(input_dir, temp_dir, skip_movie_frame_generation=False):
    input_files = list(Path(input_dir).iterdir())
    input_mode = check_input_dir(input_files)
    global filename

    if input_mode == 'video':
        video_files = [file.name for file in input_files if mimetypes.guess_type(file).startswith('video')]
        if not video_files:
            sys.exit("No video files found in the directory.")

        if len(video_files) > 1:
            questions = [
                inquirer.List(
                    'video_file',
                    message="Select a video file to process:",
                    choices=video_files,
                )
            ]
            answers = inquirer.prompt(questions)
            input_file_name = answers['video_file']
        else:
            input_file_name = video_files[0]

        input_file_path = f"{input_dir}/{input_file_name}"
        filename = Path(input_file_name).stem

        if not skip_movie_frame_generation:
            sequence_path = video_to_sequence(input_file_path, filename, temp_dir)
            input_path = Path(sequence_path)
        else:
            input_path = Path(temp_dir) / "movie_frames"

    elif input_mode == 'image':
        filename = input_files[0].stem
        input_path = Path(input_dir)

    print(f"Processing {filename}")
    return input_path


def process_images(input_path, swatches_dir):
    swatches_paths = []
    image_files = list(input_path.glob("*.*"))
    total_images = len(image_files)

    print("Processing images...")
    # Process each image
    for index, image_file in enumerate(image_files, start=1):
        if image_file.is_file():
            sys.stdout.write(f"\rProcessing image [{index}/{total_images}]")
            sys.stdout.flush()

            filename = image_file.stem
            image_file_path = str(image_file)

            # Get average color
            swatch_color = get_average_color(image_file_path)

            # Create color swatch
            swatch_path = create_swatch(swatch_color, filename, swatches_dir)
            swatches_paths.append(swatch_path)
    print()  # Move to the next line after processing
    return swatches_paths


def paletify_main(target_width=8192, aspect_ratio=2.55, skip_movie_frame_generation=True, skip_swatch_generation=False):
    clear()
    """Process all images in the input directory."""
    temp_dir, output_dir, swatches_dir = ensure_directories()
    input_dir = "input/"

    input_path = pick_input_mode(input_dir, temp_dir, skip_movie_frame_generation)

    swatches_paths = process_images(input_path, swatches_dir)

    # Create combined image
    combined_path = create_combined_image(
        swatches_paths, output_dir, target_width, aspect_ratio
    )

    # cleanup(temp_dir)

    return combined_path


if __name__ == "__main__":
    paletify_main()
