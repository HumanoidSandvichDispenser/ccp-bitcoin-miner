#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2023 sandvich <sandvich@archtop>
#
# Distributed under terms of the GPLv3 license.

from tokens import Token, Group, Speech, SoundEffect, SoundFilter
import re


class Tokenizer:
    input_str: str
    index: int

    current_text: str
    current_speaker: str = "udisen"

    def __init__(self, input_str: str, root: Group) -> None:
        self.input_str = input_str
        self.index = -1
        self.context = root

    def get_next(self) -> str | None:
        if self.index < len(self.input_str) - 1:
            return self.input_str[self.index + 1]

    def move_next(self):
        next = self.get_next()
        self.index += 1
        return next

    def tokenize(self, root: Group):
        tokens = self.lex()
        self.parse(list(tokens), root)
        root.validate()
        root.gen_file_name(0)
        return root

    def parse(self, tokens: list[Token], root: Group):
        stack: list[Group] = [root]
        for token in tokens:
            # this can happen if there are more filter end tokens {.} than
            # filter start tokens {x}
            if len(stack) == 0:
                break

            group = stack[-1]
            if isinstance(token, SoundFilter):
                if token.index == ".":
                    stack.pop()
                    continue
                else:
                    token.group = Group([])
                    stack.append(token.group)
            group.tokens.append(token)
        return root

    def scan_to_delimiter(self, delimiter) -> str | None:
        ret = ""
        while self.get_next() != delimiter:
            c = self.move_next()
            if c is None:
                return None
            ret += c

        self.move_next()

        if len(ret) > 0:
            #filter = SoundFilter()
            #filter.index = filter_str
            return ret

    def lex(self):
        text = ""
        while True:
            #input_string = ""
            c = self.move_next()

            if c is None:
                # yield remaining text as speech
                yield Speech(self.current_speaker, text)
                return

            if c in ":":
                tokens = re.split(" |\\n", text)
                previous_speech = " ".join(tokens[0:-1])
                yield Speech(self.current_speaker, previous_speech)
                self.current_speaker = tokens[-1]
                text = ""
            elif c in "{":
                yield Speech(self.current_speaker, text)
                text = ""

                index = self.scan_to_delimiter("}")
                if index:
                    filter = SoundFilter()
                    filter.index = index
                    yield filter
            elif c in "[":
                yield Speech(self.current_speaker, text)
                text = ""

                index = self.scan_to_delimiter("]")
                if index:
                    filter = SoundEffect()
                    try:
                        filter.index = int(index)
                        yield filter
                    except ValueError:
                        continue
            else:
                text += c
            #context.append_token(self.scan_text())
