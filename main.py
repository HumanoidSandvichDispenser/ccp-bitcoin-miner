#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2023 sandvich <sandvich@archtop>
#
# Distributed under terms of the MIT license.

import sys
import click


@click.command()
@click.option("--cpu", is_flag=True, default=False, help="Enables/disables CPU inference")
@click.option("--threads", default=2, help="Number of threads (CPU only)")
@click.option("--stdin", is_flag=True, default=False, help="Read from standard input")
@click.option("--outfile", default="audio.wav", help="Audio file to write to")
def main(cpu, threads, stdin, outfile):
    import tokens
    from tokens import Token, Group
    from tokenizer import Tokenizer
    from bitcoin_miner import BitcoinMiner

    bitcoin_miner = BitcoinMiner(not cpu, threads)
    bitcoin_miner.update_model("udisen")
    tokens.speech_synthesizer = bitcoin_miner

    while True:
        try:
            # dash argument to read from stdin
            if stdin:
                line = sys.stdin.read().replace("\n", " ")
            else:
                print("-" * 50)
                line = input()
            if line == "":
                continue
            root = Group([])
            Tokenizer(line, root).tokenize(root)
            root.outfile = outfile
            root.synthesize()

            if stdin:
                exit(0)
            #if line.startswith("model:"):
            #    words = line.split(" ")
            #    speech = " ".join(words[1:])
            #    speaker = words[0].split(":")[-1]
            #    bitcoin_miner.update_model(speaker)
            #    line = speech
            #audio = bitcoin_miner.end_to_end_infer(line, None)
            #if audio is not None:
            #    sf.write("audio.wav", audio.to("cpu").numpy(), 22050)
        except EOFError:
            break
        except KeyboardInterrupt:
            print("Stopping...")
            break

if __name__ == "__main__":
    main()
