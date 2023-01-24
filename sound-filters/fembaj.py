#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2023 sandvich <sandvich@archtop>
#
# Distributed under terms of the MIT license.

# This is the python script version of the fembaj.sh filter

import sox
import sys


print("Input file: " + sys.argv[1])
print("Output file: " + sys.argv[2])

tfm = sox.Transformer()
tfm.treble(4).bass(-2).pitch(2)  # pitch in semitones

tfm.build_file(sys.argv[1], sys.argv[2])
