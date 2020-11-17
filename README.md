# speech2text

Speech to Text command line utility based on SpeechRecognition Python library

## install dependencies

```bash
pip3 install -r requirements.txt
```

## How to run it

```bash
python3 speech2text.py [OPTIONS] input-file.wav [output-file.txt]
```

### options

**--silence-length *length*, -l *length* :** Split sentences when silence is *length* ms. or more. Default: *700* ms

**--silence-thresh *amount*, -t *amount* :** Consider silent if quitter than *amount* dBFS. Default: *-40*

**--temp-dir *path*, -T *path* :** Path to store temporary files. Default: *./tmp*

**--padding *padding* -p *padding* :** How much silence to add at both ends so audio slice doesn’t seem abruptly cut. Default: *100* ms.

**--language *language*, -L *language* :** Language to use for speech recognition. Default: *en-US*

**--ambient-noise, -n :** Try to mitigate ambient noise. Not always improves conversion. So off by default

**--keep-temporary, -k :** Do not remove temporary files created during conversion. Useful for debugging

**--silent, -s :** Do not show progress on console

**--max-workers *workers*, -m *workers* :** Number of concurrent conversions threads. Default: *number of OS reported CPUs*.
