#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2023 sandvich <sandvich@archtop>
#
# Distributed under terms of the MIT license.

from sys import stderr


import sys
import os
import json
import gdown
import torch
import numpy as np


if __name__ == "__main__":
    from .tacotron2.hparams import create_hparams
    from .tacotron2.model import Tacotron2
    from .tacotron2.layers import TacotronSTFT
    from .tacotron2.audio_processing import griffin_lim
    from .tacotron2.text import text_to_sequence

    from .hifigan.env import AttrDict
    from .hifigan.meldataset import MAX_WAV_VALUE
    from .hifigan.models import Generator
else:
    sys.path.append("hifigan")
    sys.path.append("tacotron2")
    from hparams import create_hparams  # type: ignore
    from model import Tacotron2  # type: ignore
    from layers import TacotronSTFT  # type: ignore
    from audio_processing import griffin_lim  # type: ignore
    from text import text_to_sequence  # type: ignore

    from env import AttrDict  # type: ignore
    from meldataset import MAX_WAV_VALUE  # type: ignore
    from models import Generator  # type: ignore


class BitcoinMiner():
    thisdict = {}
    HIFIGAN_ID = "1qpgI41wNXFcH-iKq1Y42JlBC9j0je8PW"
    GDRIVE_PREFIX = "https://drive.google.com/uc?id="

    model_name = ""
    model = None
    hparams = None

    hifigan = None
    device: torch.device

    def __init__(self, is_using_cuda=True, cpu_threads=1):
        # allows user to choose CPU or CUDA inference
        import os
        #pbar.update(1) # downloaded TT2 and HiFi-GAN
        import gdown

        #import IPython.display as ipd
        import numpy as np
        import torch
        import json

        if is_using_cuda:
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")
            torch.set_num_threads(cpu_threads)

        print("INFO: torch.device.type == \"%s\"" % self.device.type)

        self.hifigan, _ = self.get_hifigan()

    def arpa(self, text, punctuation=r"!?,.;", EOS_Token=True):
        out = ""
        for word_ in text.split(" "):
            word = word_
            end_chars = ""
            while any(elem in word for elem in punctuation) and len(word) > 1:
                if word[-1] in punctuation: end_chars = word[-1] + end_chars; word = word[:-1]
                else: break
            try:
                word_arpa = self.thisdict[word.upper()]
                word = "{" + str(word_arpa) + "}"
            except KeyError:
                pass
            out = (out + " " + word + end_chars).strip()
        if EOS_Token and out[-1] != ";":
            out += ";"
        return out

    def get_hifigan(self):
        # Download HiFi-GAN
        hifimodel_outfile = "hifimodel"
        if not os.path.exists(hifimodel_outfile):
            gdown.download(self.GDRIVE_PREFIX + self.HIFIGAN_ID,
                    hifimodel_outfile, quiet=False)
        if not os.path.exists(hifimodel_outfile):
            raise Exception("HiFI-GAN model failed to download!")

        # Load HiFi-GAN
        conf = os.path.join("hifigan", "config_v1.json")
        with open(conf) as f:
            json_config = json.loads(f.read())
        h = AttrDict(json_config)
        torch.manual_seed(h["seed"])
        #hifigan = Generator(h).to(torch.device("cuda"))
        hifigan = Generator(h).to(self.device)
        #state_dict_g = torch.load(hifimodel_outfile, map_location=torch.device("cuda"))
        state_dict_g = torch.load(hifimodel_outfile, map_location=self.device)
        hifigan.load_state_dict(state_dict_g["generator"])
        hifigan.eval()
        hifigan.remove_weight_norm()
        return hifigan, h

    def has_MMI(self, state_dict):
        return any(True for x in state_dict.keys() if "mi." in x)

    def get_tacotron2(self, model_path):
        # Download Tacotron2
        if not os.path.exists(model_path):
            raise FileNotFoundError("\"%s\" does not exist" % model_path)

        hparams = create_hparams()
        hparams["sampling_rate"] = 22050
        hparams["max_decoder_steps"] = 3000
        hparams["gate_threshold"] = 0.25

        model = Tacotron2(hparams)

        state_dict = torch.load(model_path,
                                map_location=self.device)["state_dict"]

        if self.has_MMI(state_dict):
            raise Exception("ERROR: This notebook does not currently support MMI models.")
        model.load_state_dict(state_dict)
        model.to(self.device).eval()
        if self.device.type != "cpu":
            model.half()
        return model, hparams

    def end_to_end_infer(self, text, pronunciation_dictionary):
        if self.model is None:
            raise Exception("No Tacotron model is loaded")

        if self.hifigan is None:
            raise Exception("HifiGAN is not loaded")

        for i in [x for x in text.split("\n") if len(x)]:
            if not pronunciation_dictionary:
                if i[-1] != ";":
                    i += ";" 
            else:
                i = self.arpa(i)

            with torch.no_grad(): # save VRAM by not including gradients
                sequence = np.array(text_to_sequence(i, ["english_cleaners"]))[None, :]
                sequence = torch.autograd.Variable(torch.from_numpy(sequence)) \
                        .to(self.device).long()
                #mel_outputs, mel_outputs_postnet, _, alignments = self.model.inference(sequence)

                _, mel_outputs_postnet, _, _ = self.model.inference(sequence)
                #if show_graphs:
                #    plot_data((mel_outputs_postnet.float().data.cpu().numpy()[0],
                #            alignments.float().data.cpu().numpy()[0].T))
                y_g_hat = self.hifigan(mel_outputs_postnet.float())
                audio = y_g_hat.squeeze()
                #audio = audio * MAX_WAV_VALUE FeelsGoodMan Clap
                return audio

    def update_model(self, model_name):
        # don't update if requested model is the same as the current one
        if self.model_name != model_name:
            if self.model is not None:
                del self.model
            print("Updating models...")
            self.model, self.hparams = self.get_tacotron2("models/" + model_name)
            self.model_name = model_name
