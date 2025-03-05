"""
This script is used fo create ICO from SVG.

Be aware, that installation of CairoSVG requires dependencies
beyond that pypi offers (see: https://cairosvg.org/documentation/#installation)
"""

import argparse
import os
import tempfile

import cairosvg
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description="Generate ICO from SVG")
    parser.add_argument("source", help="Source SVG location")
    parser.add_argument("target", help="Target ICO location")
    args = parser.parse_args()

    f = tempfile.NamedTemporaryFile(delete=False)
    cairosvg.svg2png(url=args.source, write_to=f.name)
    img = Image.open(f.name)
    img.save(
        args.target,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (256, 256)],
    )
    f.close()
    os.unlink(f.name)


if __name__ == "__main__":
    main()
