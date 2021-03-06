#!/usr/bin/env python2.7

#(c) 2015-2016 by Authors
#This file is a part of Nano-Align program.
#Released under the BSD license (see LICENSE file)

"""
Merges multiple files with blockades into one
"""

import sys
import os

nanoalign_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, nanoalign_root)
from nanoalign.blockade import read_mat, write_mat


def main():
    if len(sys.argv) < 3:
        print("usage: merge-mat.py mat_1[,mat_2..] out_mat\n\n"
              "Merge multiple files with blockades into one")
        return 1

    blockades = []
    for mat_file in sys.argv[1:-1]:
        blockades.extend(read_mat(mat_file))

    write_mat(blockades, sys.argv[-1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
