import random
import re

from pydub import AudioSegment
from pyt2s.services import streamlabs, stream_elements
import os


def create_directories():
    directories = ["subtitles", "text", "bg_video", "audio", "combined_audio"]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


# run this once for each file
# Function to split text into chunks based on sentence boundaries
def split_text(text, title, chunk_size=925):
    sentences = re.split(r'(?<=[.!?]) +', text)  # Split text into sentences
    chunks = []
    current_chunk = [title.strip("\n")]
    current_length = len(title) + 1  # Initialize with the length of the title

    for sentence in sentences:
        sentence_length = len(sentence) + 1  # +1 for space or newline
        # Check if adding the sentence exceeds the adjusted chunk size
        if current_length + sentence_length > chunk_size:
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
            current_chunk = [title.strip("\n"), sentence]
            current_length = len(title) + 1 + sentence_length  # Reset length with title and sentence length
        else:
            current_chunk.append(sentence)
            current_length += sentence_length

    if current_chunk:
        chunks.append('\n'.join(current_chunk))  # Append the last chunk

    return chunks


def generate_audio_and_text(voice, file_name, tts_service, post_num):
    # Example usage
    create_directories()
    # Get user input for gender and file name

    # Read text from file
    with open(f"./posts/{file_name}.txt", 'r', encoding='utf-8') as f:
        title = f.readline()
        text = ' '.join([l.strip() for l in f.readlines()])

    # Split text into chunks
    chunks = split_text(text, title, chunk_size=1000)

    # Generate MP3 files for each chunk and save text chunks
    mp3_files = []
    for i, chunk in enumerate(chunks):
        # Create audio file for chunk
        audio_file_path = f"audio/audio_{i}.mp3"
        data = tts_service.requestTTS(chunk, voice=voice)  # Adjust service call if necessary
        with open(audio_file_path, 'wb') as file:
            file.write(data)
        mp3_files.append(audio_file_path)

        # Save text chunk with each word on a new line
        text_file_path = f"text/text_{i}.txt"
        with open(text_file_path, 'w', encoding='utf-8') as file:
            # Split the chunk into words
            words = chunk.split()

            # Initialize the index for iterating through words
            index = 0

            # Iterate through the words
            while index < len(words):
                # If word is greater than 15 characters
                if len(words[index]) > 15:
                    num_words = 1
                else:
                    # Randomly choose to take one or two words
                    num_words = random.choice([1, 2])

                # Get the words slice (ensure not to exceed the length of words list)
                selected_words = words[index:index + num_words]

                # Join the selected words with a space and write to the file
                file.write(' '.join(selected_words).strip() + "\n")

                # Increment the index by the number of words taken
                index += num_words

    # Combine the MP3 files
    combined = AudioSegment.empty()
    for file in mp3_files:
        combined += AudioSegment.from_mp3(file)

    # Export the combined audio
    combined_file_path = f"combined_audio/final_audio_{post_num}.mp3"
    combined.export(combined_file_path, format="mp3")

    print("Audio processing complete.")
