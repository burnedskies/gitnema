import argparse
import pathlib

from PIL import Image
from PIL.ImageFile import ImageFile


GRAYSCALE_CHARSET = r" .:-=+*#%@"


def resize_image(image: ImageFile, columns=106):
    # https://github.com/LeandroBarone/python-ascii_magic/blob/dc16cd04e0de23d0c902be8c8556d790f3d08136/ascii_magic/ascii_art.py#L236
    width, height = image.size
    scalar = width * 2.2 / columns

    return image.resize(
        (
            int(width * 2.2 / scalar),
            int(height / scalar),
        )
    )


def convert_image_to_ascii(image: ImageFile, columns: int = 106) -> str:
    image = resize_image(image, columns)
    image = image.convert("L")  # convert it grayscale (maybe add color later)

    pixels = image.get_flattened_data()
    output = ""

    for idx, pixel in enumerate(pixels):
        color_idx = pixel * (len(GRAYSCALE_CHARSET) - 1) // 255
        output += GRAYSCALE_CHARSET[color_idx]

        if (idx + 1) % columns == 0:
            output += "\n"

    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("-o", "--output", type=str)
    parser.add_argument("-c", "--columns", type=int, default=106)
    args = parser.parse_args()

    input_path = pathlib.Path(args.input)

    input_targets: list[pathlib.Path] = []
    if input_path.is_dir():
        input_targets = list(input_path.glob("*.png"))
    elif input_path.is_file():
        input_targets = [input_path]

    outpathstr = args.output if args.output else f"ascii_{input_path.stem}.gitnema"
    outpath = pathlib.Path(outpathstr)
    outpath.unlink(missing_ok=True)

    for target in input_targets:
        image = Image.open(target)
        image_ascii = convert_image_to_ascii(image, args.columns)

        # store all the frames in one file
        with open(outpath, "a+", newline="") as file:
            file.write(image_ascii)
            file.write("EOF\r\n")  # EOF (End of Frame) marker.


if __name__ == "__main__":
    main()
