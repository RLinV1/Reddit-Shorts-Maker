import json
import os


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
        begin = float(fragment['begin'])
        end = float(fragment['end'])

        start_time = format_time(begin)
        end_time = format_time(end)

        srt_content += f"{index + 1}\n"
        srt_content += f"{start_time} --> {end_time}\n"
        srt_content += "\n".join(fragment['lines']) + "\n\n"

    return srt_content


def write_srt_file(filename, srt_content):
    with open(filename, 'w') as file:
        file.write(srt_content)


def generate_srt(index):

    json_filename = 'map.json'  # Replace with your JSON file path
    srt_filename = f'subtitles/subtitle_{index}.srt'  # Replace with your desired output file path

    # Read JSON data
    data = read_json_file(json_filename)

    # Convert JSON data to SRT format
    srt_content = convert_fragments_to_srt(data['fragments'])

    # Write SRT content to file
    write_srt_file(srt_filename, srt_content)

    os.remove("map.json")

    print("SRT file created successfully.")


