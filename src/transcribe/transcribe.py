import os
from tqdm import tqdm
import whisper
from whisper.utils import get_writer
import time
import logging
import datetime
import importlib.metadata
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import subprocess
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

# Configure logging
logging.basicConfig(
    filename="default.log",  # Log file name
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)


class Transcriber:
    def __init__(self, directory, output, language_model, language, fp16, ignore_existing=False, creator="Unknown", temperature=0, check_for_silence=True):
        self.directory = directory
        self.files_to_transcribe = (".mp3", ".mp4", ".avi", ".flac", ".mkv", ".wmv", ".wma", ".wav", ".webm")
        self.output = output
        self.model = language_model
        self.language = language
        self.temperature = temperature
        self.check_for_silence = check_for_silence
        self.fp16 = fp16
        self.ignore_existing = ignore_existing
        self.creator = creator
        self.whisper_version = importlib.metadata.version("openai-whisper")
        self.tamuwhisper_version = importlib.metadata.version("tamuwhisper")
        self.whisper_options = {
            "highlight_words": False,
            "max_line_count": 2,
            "max_line_width": 80
        }
        if self.ignore_existing:
            self.existing = self.__cache_existing()
        else:
            self.existing = []

    def __cache_existing(self):
        existing = []
        for dirpath, dirnames, filenames in os.walk(self.output):
            for filename in filenames:
                if filename.endswith('.vtt'):
                    existing.append(f'{os.path.splitext(filename)[0]}')
        return existing

    def batch_transcribe(self):
        for dirpath, dirnames, filenames in os.walk(self.directory):
            for filename in tqdm(filenames):
                if f'{os.path.splitext(filename)[0]}_{self.model}' not in self.existing and filename.endswith(self.files_to_transcribe):
                    self.__transcribe(os.path.join(self.directory, filename))
                else:
                    print(f"Skipping {filename}:  already exists!")
        return
    
    def __check_if_silent(self, filename):
        audio = AudioSegment.from_file(filename)
        nonsilent_parts = detect_nonsilent(audio, min_silence_len=1000, silence_thresh=-50)
        if not nonsilent_parts:
            return True
        else:
            return False

    def __transcribe(self, file):
        # @todo: Clean this entire method up
        if self.check_for_silence == True:
            silent_start = time.time()
            is_silent = self.__check_if_silent(file)
            silent_finish = time.time()
            silence_elapsed = silent_finish - silent_start
        else:
            # Assume it's not silent unless told otherwise
            is_silent = False
        os.makedirs(self.output, exist_ok=True)
        output_file = f'{os.path.splitext(file)[0]}_{self.model}.vtt'
        known_languages = {
                "English": "eng",
                "Spanish": "spa",
        }
        embedded_metadata = {
            "Type": "caption",
            "Language": known_languages[self.language],
            "Responsible Party": "US, Texas A&M University Libraries",
            "Originating File": file,
            "File Creator": self.creator,
            "File Creation Date": str(datetime.datetime.now()),
            "Local Usage Element": f"[version history] {str(datetime.datetime.now())}: WebVTT initially generated by "
                                f"OpenAI Whisper v. {self.whisper_version} and model '{self.model}' with tamu_whisper"
                                f" v. {self.tamuwhisper_version}.",
        }
        if not is_silent:
            model = whisper.load_model(self.model)
            # Right now, start time and end time only apply to Whisper -- not other parts of the process.
            start_time = time.time()
            result = model.transcribe(
                file, fp16=self.fp16, language=self.language, word_timestamps=True, temperature=self.temperature
            )
            end_time = time.time()
            elapsed_time = end_time - start_time
            writer = get_writer('vtt', self.output)
            writer_json = get_writer('json', self.output)
            writer(result, output_file.replace(f"_{self.model}", f".caption"), self.whisper_options)
            print(
                f"{self.output}/{output_file.split('/')[-1].replace(
                    f"_{model}", ".caption")}"
            )
            self.add_embedded_metadata(
                f"{self.output}/{output_file.split('/')[-1].replace(f"_{self.model}", f".caption")}", embedded_metadata
            )
            writer_json(result, output_file.replace('.vtt', '.json'), self.whisper_options)

            logging.info(f"Transcription completed for {file} in {elapsed_time:.2f} seconds using model {self.model}. Results written to {output_file}.")
        else:
            self.write_no_audio(file, f"{self.output}/{output_file.split('/')[-1].replace(f"_{self.model}", f".caption")}")
            embedded_metadata["Local Usage Element"] = f"[version history] {str(datetime.datetime.now())}: WebVTT initially generated by tamu_whisper v. {self.tamuwhisper_version}. OpenAI Whisper was not used due to the media file being silent."
            self.add_embedded_metadata(
                f"{self.output}/{output_file.split('/')[-1].replace(f"_{self.model}", f".caption")}", embedded_metadata
            )
            logging.info(f"Transcription completed for {file} in {silence_elapsed:.2f}. The file was silent. Results written to {output_file}.")
        return

    def write_no_audio(self, filename, output):
        def get_duration():
            command = [
                "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        def seconds_to_timestamp(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds - int(seconds)) * 1000)
            return f"{hours:02}:{minutes:02}:{secs:02}.{millis:03}"
        duration = get_duration()
        start = 0
        with open(output, "w") as my_vtt:
            my_vtt.write("WEBVTT\n\n")
            while start < duration:
                start_time = seconds_to_timestamp(start)
                if start + 10 < duration:
                    end_time = seconds_to_timestamp(start + 10)
                else:
                    end_time = seconds_to_timestamp(duration)
                my_vtt.write(f"{start_time} --> {end_time}\n[No audio]\n\n")
                start += 10.01
        return
            
    @staticmethod
    def add_embedded_metadata(file_path, comments):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        if not lines[0].startswith('WEBVTT'):
            raise ValueError("Not a valid WebVTT file")

        for k, v in reversed(comments.items()):
            comment_line = f"{k}: {v}\n"
            lines.insert(1, comment_line)
        with open(file_path, 'w') as file:
            file.writelines(lines)
