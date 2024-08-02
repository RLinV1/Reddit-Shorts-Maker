import random
import re
import os

from video import generate_video
from voice import generate_audio_and_text
from pyt2s.services import oddcast, stream_elements

from audio_to_srt import audio_to_json, json_to_srt


# run reddit.py to generate the reddit posts
# then run voice.py to generate the clips for one reddit post


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


def process_post(file_name, gender):
    if gender == "male" or gender == "m":
        tts_service = oddcast
        voice = "5-4-1"  # Adjust if necessary
    else:
        tts_service = stream_elements
        voice = "Joanna"  # Adjust if necessary

    match = re.search(r'(\d+)$', file_name)

    if match:
        # Extract the number from the match
        post_num = int(match.group(1))
        # print(f"The extracted number is: {post_num}")
    else:
        print("No number found in the file name.")
        post_num = 0

    # Generate audio and text chunks
    generate_audio_and_text(voice, file_name, tts_service, post_num)

    lst = os.listdir("./audio")  # your directory path
    count = len(lst) - 1

    bg_video = os.listdir("./bg_video")
    dir_len = len(bg_video)
    video_path = bg_video[random.randint(0, dir_len - 1)]

    for index in range(count):
        print(f"Creating Video #{index + 1}")

        audio_path = f"audio/audio_{index}.mp3"

        audio_to_json(index)

        # Convert map.json to srt
        json_to_srt("map.json", index)

        print("Subtitles Made")

        with open(f"./posts/{file_name}.txt", 'r', encoding='utf-8') as f:
            title = f.readline()

        description = generate_description("Subscribe now and never miss an update!")
        # Creates video based on bg_video, audio
        finished_video_path = generate_video(video_path, audio_path, index, post_num)

        # Upload video if content limit then comment this out and manually upload
        # upload_video(finished_video_path, title, description)

    # Test the function
    remove_all_files_in_directory("audio")
    remove_all_files_in_directory("text")
    remove_all_files_in_directory("subtitles")


def main():
    gender = input("What gender do you want the voice to be? Male or Female? \n").strip().lower()
    loop_choice = input("Do you want to loop through all posts in the posts directory? (y/n):\n").strip().lower()
    posts_dir = './posts'

    if loop_choice == "yes" or loop_choice == "y":
        # Loop over all files in the posts directory
        for file_name in os.listdir(posts_dir):
            if file_name.endswith('.txt'):
                process_post(file_name[:-4], gender)  # Remove '.txt' from file name
    else:
        file_name = input("What is the file name? Make sure it's in the posts dir:\n").strip()
        process_post(file_name, gender)


if __name__ == "__main__":
    main()
