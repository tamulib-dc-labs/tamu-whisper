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
    "transcribe", 
    help="Create VTTs with FADGI Embedded Metadata and Whisper JSON"
)
@click.option(
    "--directory",
    "-d",
    help="The path to your media files",
)
@click.option(
    "--output",
    "-o",
    default="output",
    help="The output directory to write your generated vtts and json to",
)
@click.option(
    "--model",
    "-m",
    default="base",
    help="Which Whisper model to use",
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
    '-f',
    '--fp16',
    is_flag=True,
    help='Use FP16 instead of FP32'
)
@click.option(
    '-i', 
    '--ignore-existing', 
    is_flag=True,
    help='Skip A/V files that already have a transcription'
)
@click.option(
    "-c",
    "--creator",
    help="Name of person using the tool. Used for embedded metadata.",
    default="Unknown"
)
@click.option("--check_silence", is_flag=True, help="Run a check if files are silent first.")
@click.option(
    "-t", 
    '--temperature', 
    type=float, 
    help='Controls randomness in text decoding. Lower values (e.g., 0.0) make output more deterministic and accurate; higher values (e.g., 1.0) increase diversity and may improve results on noisy or ambiguous audio.', 
    default=0
)
def run(
        directory: str,
        output: str,
        model: str,
        language: str,
        fp16: bool,
        ignore_existing: bool,
        creator: str,
        temperature: float,
        check_silence: bool,
) -> None:
    x = Transcriber(
        directory, output, model, language, fp16, ignore_existing, creator=creator, check_for_silence=check_silence, temperature=temperature
        )
    x.batch_transcribe()

