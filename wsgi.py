#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2023 sandvich <sandvich@artix>
#
# Distributed under terms of the GPLv3 license.


from flask import Flask, request, send_file
import tokens
from tokens import Group
from tokenizer import Tokenizer
from bitcoin_miner import BitcoinMiner


app = Flask(__name__)

bitcoin_miner = BitcoinMiner(False, 4)
bitcoin_miner.update_model("udisen")
tokens.speech_synthesizer = bitcoin_miner

@app.route("/")
def root_path():
    return "Your mom"

@app.route("/", methods=["POST"])  # type: ignore
def request_synthesis():
    content = request.get_data(as_text=True)
    if content is None:
        return "Bad request", 400

    outfile = synthesize(content)
    if outfile is None:
        return 500

    return send_file(outfile, mimetype="audio/wav")

def synthesize(text: str) -> str | None:
    root = Group([])
    Tokenizer(text, root).tokenize(root)
    root.outfile = "audio.wav"
    if root.synthesize():
        return root.outfile
    return None
