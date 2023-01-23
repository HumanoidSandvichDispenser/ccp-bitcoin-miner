#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2023 sandvich <sandvich@archtop>
#
# Distributed under terms of the MIT license.

from bitcoin_miner import BitcoinMiner
import soundfile as sf
import sox
import os
import shutil


BUFFER_PATH = ".buffer"
speech_synthesizer: BitcoinMiner


class Token:
    outfile: str

    def synthesize(self):
        raise NotImplementedError()

    def __str__(self) -> str:
        return "Token()"

    def validate(self):
        return self

    def gen_file_name(self, id: int):
        self.outfile = "%s/%03d.wav" % (BUFFER_PATH, id)
        return id + 1


class Group(Token):
    tokens: list[Token]

    def __init__(self, tokens) -> None:
        self.tokens = tokens

    def synthesize(self):
        if len(self.tokens) == 0:
            return False

        #buffer = AudioSegment.empty()
        combiner = sox.Combiner()
        filenames: list[str] = []

        for token in self.tokens:
            if token.synthesize():
                filenames.append(token.outfile)
        print("Synthesizing group: " + ", ".join(filenames))
        if len(filenames) > 1:
            combiner.build(filenames, self.outfile, "concatenate")
        else:
            #combiner.build(filenames, self.outfile, "concatenate")
            shutil.copy(filenames[0], self.outfile)
        return True

    def __str__(self) -> str:
        tokens_str: list[str] = []
        for token in self.tokens:
            tokens_str.append(str(token))
        return "Group(\n%s\n)" % ("\n".join(tokens_str))

    def validate(self):
        valid_tokens = []
        for token in self.tokens:
            valid_token = token.validate()
            if valid_token is not None:
                valid_tokens.append(valid_token)
        self.tokens = valid_tokens
        if len(self.tokens) > 1:
            return self
        if len(self.tokens) > 0:
            # dissolve group to reduce overhead during synthesis
            return self.tokens[0]

    def gen_file_name(self, id: int):
        # traverse tree
        self.outfile = "/%03d.wav" % id
        id += 1
        for token in self.tokens:
            id = token.gen_file_name(id)
        return id
        #return super().gen_file_name(id)


class Sound(Token):
    pass


class Speech(Sound):
    speaker: str
    text: str
    #synthesizer: BitcoinMiner

    def __init__(self, speaker, text) -> None:
        self.speaker = speaker
        self.text = text

    def synthesize(self) -> bool:
        speech_synthesizer.update_model(self.speaker)
        audio = speech_synthesizer.end_to_end_infer(self.text, None)
        print("Synthesizing %s speaking: %s" % (self.speaker, self.text))
        if audio is not None:
            sf.write(self.outfile, audio.to("cpu").numpy(), 22050)
            return True
        return False

    def __str__(self) -> str:
        return "Speech(%s, %s)" % (self.speaker, self.text)

    def validate(self):
        self.text = self.text.strip()
        if len(self.text) > 0:
            return self


class SoundEffect(Sound):
    index: str

    def synthesize(self):
        print("Synthesizing sound effect %s" % self.index)
        if os.path.exists("sound-effects/%s.wav" % self.index):
            shutil.copy("sound-effects/%s.wav" % self.index, self.outfile)
            return True
        #elif os.path.exists("sound-effects/%s.mp3" % self.index):
        #    buf: AudioSegment
        #    buf = AudioSegment().from_mp3("sound-effects/%s.mp3" % self.index)
        #    buf.export(self.outfile, format="wav")

    def __str__(self) -> str:
        return "SoundEffect(%d)" % self.index


class SoundFilter(Token):
    group: Group | Token
    index: str

    def synthesize(self):
        if not self.group.synthesize():
            return False

        tfm = sox.Transformer()

        if self.index == "1":
            # room echo
            tfm.reverb(50, room_scale=25)
        elif self.index == "2":
            # hall echo
            tfm.reverb(75, room_scale=75, wet_gain=1)
        elif self.index == "3":
            # outside echo
            tfm.reverb(5, room_scale=5)
        elif self.index == "4":
            # pitch down
            tfm.pitch(-6)  # half an octave
        elif self.index == "5":
            # pitch up
            tfm.pitch(6)  # half an octave
        elif self.index == "6":
            # telephone
            tfm.highpass(800).gain(2)
        elif self.index == "7":
            # muffled
            tfm.lowpass(1200).gain(1)
        elif self.index == "8":
            # quieter
            tfm.gain(-4)
        elif self.index == "9":
            # ghost
            (tfm
             .pad(0.5, 0.5)
             .reverse()
             .reverb(reverberance=50, wet_gain=1)
             .reverse()
             .reverb())
        elif self.index == "10":
            # chorus
            tfm.chorus()
        elif self.index == "11":
            # slow down
            tfm.tempo(0.5)
        elif self.index == "12":
            # speed up
            tfm.tempo(1.5)
        elif self.index == "13":
            # velcuz real voice
            tfm.treble(4).bass(-4).pitch(2)

        print("Synthesizing filter %s" % self.index)
        tfm.build_file(self.group.outfile, self.outfile)
        return True

    def __str__(self) -> str:
        if self.group is not None:
            return "SoundFilter(%s, \n%s\n)" % (self.index, self.group)
        return "SoundFilter(%s)" % (self.index)

    def validate(self):
        group = self.group.validate()
        if group is not None:
            self.group = group
            return self

    def gen_file_name(self, id: int):
        # traverse tree
        self.outfile = "%s/%03d.wav" % (BUFFER_PATH, id)
        return self.group.gen_file_name(id + 1)
