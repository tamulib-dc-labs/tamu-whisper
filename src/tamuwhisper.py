import click
from transcribe import Transcriber
import logging

logging.basicConfig(
    filename="default.log",  # Log file name
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)

@click.group()
def cli() -> None:
    pass

@cli.command(
    "transcribe", help="Create VTTs with FADGI Embedded Metadata and Whisper JSON"
)
@click.option(
    "--directory",
    "-d",
    help="The directory to read files from",
)
@click.option(
    "--output",
    "-o",
    default="output",
    help="The output directory to write vtts and json to",
)
@click.option(
    "--model",
    "-m",
    default="base",
    help="The Whisper model to use",
    type=click.Choice(
        ['tiny', 'base', 'small', 'medium', 'large', 'turbo']
    )
)
@click.option(
    "--language",
    "-l",
    default="English",
    help="Specify language of media file",
)
@click.option(
    '-f', '--fp16', is_flag=True, help='Use FP16 instead of FP32'
)
@click.option(
    '-i', '--ignore-existing', is_flag=True,
              help='Ignore A/V files that already have a transcription'
)
def run(directory: str, output: str, model: str, language: str, fp16: bool, ignore_existing: bool) -> None:
    x = Transcriber(directory, output, model, language, fp16, ignore_existing)
    x.batch_transcribe()

