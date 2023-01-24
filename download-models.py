#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2023 sandvich <sandvich@archtop>
#
# Distributed under terms of the GPLv3 license.


import os
import gdown

GDRIVE_URL = "https://drive.google.com/uc?id="

models = {
    "udisen": "1qSqro99klbS9_7xWUYUNGjUowiYdAKas",
    "peroni": "1TgczU3dRKnudJgXI9ATk_heH8kI-3UKk",
    "velcuz": "1p6bjamvYffJa-2jMBD39PktuiKjZHh2u"
}

if not os.path.exists("models"):
    os.mkdir("models")

for model, id in models.items():
    if not os.path.exists("models/" + model):
        gdown.download(GDRIVE_URL + id, "models/" + model)
