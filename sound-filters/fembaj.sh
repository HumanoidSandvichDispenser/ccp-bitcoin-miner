#! /usr/bin/env sh
# vim:fenc=utf-8
#
# Copyright © 2023 sandvich <sandvich@archtop>
#
# Distributed under terms of the GPLv3 license.

# This is the shell script version of the fembaj.py filter

# first argument $1 is the input filename
# first argument $2 is the output filename

sox $1 $2 \
    treble 4 \
    bass -2 \
    pitch 200  # pitch in cents of a semitone
