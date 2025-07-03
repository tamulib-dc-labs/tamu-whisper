# tamuwhisper

Tool for initializing subtitle, caption, and transcript files and embedding metadata about the process according to
[FADGI Metadata Guidelines](https://www.digitizationguidelines.gov/guidelines/FADGI_WebVTT_embed_guidelines_v0.1_2024-04-18.pdf).

## Requires

* Python ~3.9 - Python ~3.12
* ffmpeg

## Running

`tamuwhisper` is designed to run as a cli program versus a directory of media files like:

```shell
tamuwhisper transcribe -d path/to/files -m turbo -c "Surname, Given name " -o path/to/where/to/write/vtts
```

## Arguments

```shell
Usage: tamuwhisper transcribe [OPTIONS]

  Create VTTs with FADGI Embedded Metadata and Whisper JSON

Options:
  -d, --directory TEXT            The path to your media files
  -o, --output TEXT               The output directory to write your generated
                                  vtts and json to
  -m, --model [tiny|base|small|medium|large|turbo]
                                  Which Whisper model to use
  -l, --language TEXT             Specify language of media file
  -f, --fp16                      Use FP16 instead of FP32
  -i, --ignore-existing           Skip A/V files that already have a
                                  transcription
  -c, --creator TEXT              Name of person using the tool. Used for
                                  embedded metadata.
  --check_silence                 Run a check if files are silent first.
  -t, --temperature FLOAT         Controls randomness in text decoding. Lower
                                  values (e.g., 0.0) make output more
                                  deterministic and accurate; higher values
                                  (e.g., 1.0) increase diversity and may
                                  improve results on noisy or ambiguous audio.
  --help                          Show this message and exit.
```
