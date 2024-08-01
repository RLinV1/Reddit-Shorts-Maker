import random
import re
import subprocess
import os
from srt import generate_srt
from video import generate_video
from voice import generate_audio_and_text
from pyt2s.services import oddcast, stream_elements
from upload_video import upload_video

# run reddit.py to generate the reddit posts
# then run voice.py to generate the clips for one reddit post

# Define the path to your Bash script
script_path = './sync.sh'


# Convert paths to WSL format
def windows_to_wsl_path(path):
    return path.replace("\\", "/").replace("C:", "/mnt/c")


def remove_all_files_in_directory(directory):
    # Check if the directory exists
    if not os.path.exists(directory):
        print(f"The directory {directory} does not exist.")
        return

    print(f"Removing all files in the directory: {directory}")

    # Iterate over all the files in the given directory
    for filename in os.listdir(directory):

        file_path = os.path.join(directory, filename)
        print(f"Checking file: {file_path}")

        try:
            # Check if it is a file and remove it
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Removed file: {file_path}")
            else:
                print(f"Skipped non-file item: {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


def generate_description(call_to_action):
    # Define templates for the description
    templates = [
        f"🌟 Enjoying our content? Don't miss out on future updates!  {call_to_action}",
        f"🔥 We love sharing great stories with you! Stay tuned and {call_to_action}",
        f"🚀 Join our community for more exciting content and updates. {call_to_action}",
        f"📚 Love what you see? Hit subscribe and follow us for more amazing posts! {call_to_action}",
        f"🎉 Be part of our journey! Follow us for the latest updates and more great content. {call_to_action}"
    ]

    # Randomly select a template
    description = random.choice(templates) + "\n#reddit #redditstories #shorts"
    return description


# Example usage
call_to_action = "Subscribe now and never miss an update!"
description = generate_description(call_to_action)


def main():
    post_num = 0
    gender = input("What gender do you want? Male or Female? \n").strip().lower()

    if gender == "male" or gender == "m":
        tts_service = oddcast
        voice = "5-4-1"  # Adjust if necessary
    else:
        tts_service = stream_elements
        voice = "Joanna"  # Adjust if necessary

    file_name = input("What is the file name? Make sure it's in the posts dir:\n").strip()

    match = re.search(r'(\d+)$', file_name)

    if match:
        # Extract the number from the match
        post_num = match.group(1)
        # print(f"The extracted number is: {post_num}")
    else:
        print("No number found in the file name.")

    # generate audio and text chunks
    generate_audio_and_text(voice, file_name, tts_service, post_num)

    lst = os.listdir("./audio")  # your directory path
    count = len(lst) - 1

    bg_video = os.listdir("./bg_video")
    dir_len = len(bg_video)
    video_path = bg_video[random.randint(0, dir_len - 1)]

    for index in range(count):
        # creates a map.json
        audio_path_wsl = windows_to_wsl_path(os.path.join('audio', f"audio_{index}.mp3"))
        text_path_wsl = windows_to_wsl_path(os.path.join('text', f"text_{index}.txt"))

        # # Print paths for debugging
        # print(f"Script path: {script_path}")
        # print(f"Audio path (WSL): {audio_path_wsl}")
        # print(f"Text path (WSL): {text_path_wsl}")

        # Run the script using WSL
        result = subprocess.run(['wsl', 'bash', script_path, audio_path_wsl, text_path_wsl],
                                capture_output=True, text=True)

        # Print output and error messages
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        # convert map.json to srt
        generate_srt(index)

        with open(f"./posts/{file_name}.txt", 'r', encoding='utf-8') as f:
            title = f.readline()

        generate_description("Subscribe now and never miss an update!")
        # creates video based on bg_video, audio
        finished_video_path = generate_video(video_path, audio_path_wsl, index, post_num)

        # upload video if content limit then comment this out and manually upload
        # upload_video(finished_video_path, title, description)

        # Test the function
    remove_all_files_in_directory("audio")
    remove_all_files_in_directory("text")
    remove_all_files_in_directory("subtitles")


if __name__ == "__main__":
    main()
