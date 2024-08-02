import warnings

import whisper
import json
import os

warnings.filterwarnings("ignore", category=DeprecationWarning)


# uses whisper to convert audio to transcript
def audio_to_json(index):
    # Load the Whisper model
    model = whisper.load_model("base")

    # Transcribe the audio file
    result = model.transcribe(f"./audio/audio_{index}.mp3", word_timestamps=True)

    segments = result['segments']
    word_segments = []

    # Process each segment to break it down into individual words or pairs of words
    for segment in segments:
        words = segment['words']

        i = 0
        while i < len(words):
            if len(words[i]['word']) <= 12:
                # Check the next word if within bounds
                if i + 1 < len(words) and len(words[i]['word'] + ' ' + words[i + 1]['word']) <= 12:
                    combined_text = words[i]['word'] + ' ' + words[i + 1]['word']
                    combined_start = words[i]['start']
                    combined_end = words[i + 1]['end']
                    i += 2  # Move to the next pair
                else:
                    combined_text = words[i]['word']
                    combined_start = words[i]['start']
                    combined_end = words[i]['end']
                    i += 1  # Move to the next word
            else:
                combined_text = words[i]['word']
                combined_start = words[i]['start']
                combined_end = words[i]['end']
                i += 1  # Move to the next word

            word_segments.append({
                'text': combined_text.strip(),
                'start': combined_start,
                'end': combined_end
            })

    # Print the transcribed text
    # print(f'The text in video: \n{word_segments}')

    # Write the segments to a JSON file
    with open("map.json", "w") as file:
        json.dump(word_segments, file, indent=2)


def read_json_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)


def format_time(seconds):
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"


def convert_fragments_to_srt(fragments):
    srt_content = ""

    for index, fragment in enumerate(fragments):
        begin = float(fragment['start'])
        end = float(fragment['end'])

        start_time = format_time(begin)
        end_time = format_time(end)

        srt_content += f"{index + 1}\n"
        srt_content += f"{start_time} --> {end_time}\n"
        srt_content += fragment['text'] + "\n\n"

    return srt_content


def write_srt_file(filename, srt_content):
    with open(filename, 'w') as file:
        file.write(srt_content)


def json_to_srt(json_path, index):

    srt_filename = f'subtitles/subtitle_{index}.srt'  # Replace with your desired output file path

    # Read JSON data
    data = read_json_file(json_path)

    # Convert JSON data to SRT format
    srt_content = convert_fragments_to_srt(data)

    # Write SRT content to file
    write_srt_file(srt_filename, srt_content)

    # remove map.json
    os.remove(json_path)

    # print("SRT file created successfully.")
