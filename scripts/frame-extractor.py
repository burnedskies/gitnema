import subprocess
import pathlib
import argparse
import re


def ffmpeg_extract_frames(
    pathstr: str,
    outpathstr: str | None = None,
    framerate: str = 24,
    grayscale: bool = False,
) -> subprocess.CompletedProcess:
    path = pathlib.Path(pathstr)
    if not path.exists():
        raise Exception(f"path `{path}` does not exist")

    outpath = None
    if outpathstr == None or len(outpathstr) == 0:
        outpath = pathlib.Path(".") / f"frames_{path.name}"
    else:
        outpath = pathlib.Path(outpathstr)

    outpath.mkdir(exist_ok=True, parents=True)

    filters = [f"fps={framerate}"]
    if grayscale:
        filters.append("format=gray")

    command = [
        "ffmpeg",
        "-i",
        path,
        "-vf",
        ",".join(filters),
        outpath / r"frame%05d.png",
    ]

    return subprocess.run(command, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("-o", "--output-dir", type=str)
    parser.add_argument("-f", "--framerate", type=str, default="24")
    parser.add_argument("-g", "--grayscale", action="store_true")

    args = parser.parse_args()
    if not re.match(r"^\d+(\/\d+)?$", args.framerate):  # `number` or `number/number`
        raise Exception(f"invalid framerate passed `{args.framerate}`")

    ffmpeg_extract_frames(
        args.input,
        outpathstr=args.output_dir,
        framerate=args.framerate,
        grayscale=args.grayscale,
    )


if __name__ == "__main__":
    main()
