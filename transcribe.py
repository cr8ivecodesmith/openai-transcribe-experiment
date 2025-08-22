import os
from pathlib import Path
from shutil import rmtree
from time import sleep

from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment
from pydub.utils import make_chunks

PROJECT_DIR = Path(__file__).parent
PROJECT_ENV = PROJECT_DIR.joinpath('.env')

load_dotenv(PROJECT_ENV)

# Set up your API key from the environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)


def split_audio_segments(file_path, exist_delete=True):
    full_audio = AudioSegment.from_mp3(file_path)
    segment_mins = 10 * 60 * 1000  # 10 mins in milliseconds
    chunks = make_chunks(full_audio, segment_mins)

    chunk_dir = Path(f'{file_path.stem}_segments')

    if exist_delete and chunk_dir.exists():
        rmtree(chunk_dir)

    chunk_dir.mkdir(mode=0o755, exist_ok=True)
    segment_files = []

    for idx, chunk in enumerate(chunks):
        audio_chunk = chunk_dir.joinpath(
            f'{file_path.stem}_segment_{idx}.mp3')
        chunk.export(audio_chunk, format='mp3')
        segment_files.append(audio_chunk)

    return segment_files


def transcribe_audio(file_path):
    # Send the audio data to OpenAI for transcription
    response = client.audio.transcriptions.create(
        model='whisper-1',
        file=file_path.open('rb'),
        response_format='text',
    )
    return response


def main(args):
    # Path to your audio file (MP3, WAV, etc.)
    audio_file_path = Path(args.AUDIO_FILE)

    print('Splitting audio into segments ...')
    segment_files = split_audio_segments(audio_file_path)
    print(f'Segement directory created in {segment_files[0].parent}')

    transcription_texts = []
    for audio_segment in segment_files:
        # Transcribe the audio
        print(f'Transcribing {audio_segment.name} ...')
        response_text = transcribe_audio(audio_segment)
        response_text = response_text.strip()
        transcription_texts.append(response_text)
        print(f'Transcription:\n{response_text}\n')
        sleep(1)

    print('Saving transcription...')
    output_path = Path(f'{args.output_dir or "."}')
    transcription_file = output_path.joinpath(
        f'{audio_file_path.stem}_transcription.txt')
    with transcription_file.open('w') as fh:
        fh.write('\n'.join(transcription_texts))

    print(f'Transcription written to {transcription_file}')

    print('Cleaning up segments ...')
    segment_dir = segment_files[0].parent
    rmtree(segment_dir)

    print('Done!')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('AUDIO_FILE')
    parser.add_argument(
        '-o', '--output-dir',
        dest='output_dir'
    )

    params = parser.parse_args()

    main(params)
