# Chinese Communist Party Bitcoin Miner

Tacotron 2 synthesis wrapper with syntax based on/similar to notaistreamer's
Forsen TTS donation system.

<p align="center">
    <img src="https://cdn.7tv.app/emote/6109df1e49dcebc8a39247eb/2x.webp">
    <img src="https://cdn.7tv.app/emote/6144a5317b14fdf700b94310/2x.webp">
    <br>
    +1 BTC +10 社会信用
</p>

# Installation

Required:

- Python \>= 3.8
- Pytorch 1
- sox (for sound filters)

Then install the rest (in a virtual env)

```
pip install -r requirements.txt
```

## Tacotron Models

Tacotron models I have pretrained can be downloaded [from
here](https://drive.google.com/drive/folders/1hpLQuRck0yUWv1w4mFhPzqm7TAX6FxFk)
(338M per model).

You can instead run/edit `download-models.py` which handles naming
automatically (otherwise you would have to type `udisen2-114:` instead of
`udisen:`)

If you want to use your own models, place them in the `models` directory.

# Usage

Run `main.py` to launch interactive prompt, or with `--stdin` to read from
standard input.

To use CPU for inference: `./main.py --cpu`

You can also set the number of threads: `./main.py --cpu --threads 2`

## Models/Speakers

Using the syntax `speaker: ...rest of message` will use the file
`models/speaker`.

## Examples

```
./main.py --stdin <<< "peroni: are you happy? to steal my voice? fakin tresh."
mpv audio.wav
```

```
./main.py --stdin < example-texts/poem.txt
mpv audio.wav
```

```
./main.py --stdin <<< "{fembaj.py} velcuz: remember to subscribe to my only \
    fans, fifty percent off. only fans slash velcuz, limited time offer."

mpv audio.wav
```

## Filters

The filters are the same as notaistreamer's filters (with the exception
that *every* filter can stack as much as you want).

```
{1}  room echo
{2}  hall echo
{3}  outside echo
{4}  pitch down
{5}  pitch up
{6}  telephone
{7}  muffled
{8}  quieter
{9}  ghost
{10} chorus
{11} slow down
{12} speed up
{.}  stop previous filter
```

### Custom Filters

You can write a script in the `sound-filters` directory that takes the first
argument as the input audio file and the second argument as the destination
file. Scripts that return a non-zero exit code will have no filter applied.

See `sound-filters/fembaj.py` and `sound-filters/fembaj.sh` for examples.

## Sound Effects

Sound effects are mostly the same, except that sound names can be
anything; `[abc]` will use the file `sound-effects/abc.wav`.

notaistreamer's sound effects from 101soundboard can be downloaded [from here
](https://drive.google.com/drive/folders/1g3gY0xG-F_4HFrlXSk55sbgoC5QNTRQt)
(5.6M), which should save a lot of time from having to click every single sound
effect and wait for an advertisement.

# HTTP Server

You can host an HTTP server with `flask`, which allows you to synthesize audio
on another machine or automate synthesis. This can be useful when stream
sniping, for example.

The HTTP server will accept POST requests at `/`. It will take data as plain
text and synthesize audio from it with flask's `send_file`.

On the machine you will be hosting the server on:

```
flask run
```

On your local machine that will make requests:

```
curl -X POST http://{IP_ADDRESS_OF_SERVER}:{PORT} \
    -d "udisen: hello today will show how can stream snipe with text to speech" \
    --output audio.wav
```

## Supa Streamsaver Rofi/dmenu Script

This takes input from `rofi` and synthesizes speech then plays it back.

``` sh
rofi -dmenu | curl -X POST http://{IP_ADDRESS}:{PORT} \
    -d @- \
    --output /tmp/tts.wav && mpv /tmp/tts.wav
```
