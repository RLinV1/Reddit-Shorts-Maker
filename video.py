import os
import random
import math
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip, TextClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.fx.resize import resize
from moviepy.video.tools.subtitles import SubtitlesClip


def create_text_clip(txt: str) -> CompositeVideoClip:
    """
    Create a TextClip with a shadow effect by duplicating text and adjusting its position.

    Args:
        txt (str): The text to display.

    Returns:
        CompositeVideoClip: A CompositeVideoClip object with a shadow effect.
    """
    # Create the shadow effect by duplicating the text, setting it to black, and adjusting its position
    shadow = TextClip(txt, fontsize=110, color='black', font="Montserrat",
                      stroke_width=3, stroke_color="black")
    shadow = shadow.set_position((5, 5))  # Adjust position to create shadow effect
    shadow = shadow.set_opacity(0.5)  # Adjust opacity to make the shadow semi-transparent

    # Create the main text layer
    main_text = TextClip(txt, fontsize=110, color='white', font="Montserrat",
                         stroke_width=3, stroke_color="black")

    # Overlay the shadow on the main text
    text_clip = CompositeVideoClip([shadow, main_text.set_position((0, 0))], size=main_text.size)

    return text_clip


def generate_video(video_path: str, audio: str = None,
                   index: int = None, post_num: int = None) -> str:
    """Generate a video with background video, audio, and subtitles."""

    # Generate subtitles
    subs = SubtitlesClip(f'./subtitles/subtitle_{index}.srt', create_text_clip)

    # Pick a random bg video

    # Load background video and audio clips
    video = VideoFileClip(f"bg_video/{video_path}")
    audioclip = AudioFileClip(audio)

    # Calculate a random start time for the video clip
    start = math.floor(random.uniform(0, video.duration - audioclip.duration))

    # Trim the video to match the audio length
    video = video.subclip(start, start + audioclip.duration)

    target_width = 1080
    target_height = 1920

    # Calculate new dimensions maintaining the aspect ratio
    original_width, original_height = video.size
    if original_width / original_height > target_width / target_height:
        # Crop width if the original video is too wide
        new_width = int(original_height * target_width / target_height)
        new_height = original_height
        x_center = original_width / 2
        x1 = int(x_center - new_width / 2)
        x2 = int(x_center + new_width / 2)
        y1, y2 = 0, original_height
    else:
        # Crop height if the original video is too tall
        new_width = original_width
        new_height = int(original_width * target_height / target_width)
        y_center = original_height / 2
        y1 = int(y_center - new_height / 2)
        y2 = int(y_center + new_height / 2)
        x1, x2 = 0, original_width

    # Crop video
    cropped_video = video.crop(x1=x1, x2=x2, y1=y1, y2=y2)

    # Resize video to target dimensions
    video = cropped_video.resize(newsize=(target_width, target_height))

    # Set the new audio for the video
    new_audioclip = CompositeAudioClip([audioclip])
    video = video.set_audio(new_audioclip)

    # add screenshot of reddit post for 3 seconds
    image = ImageClip(f"screenshots/post_{post_num}.png")

    # Resize the image.
    image = resize(image, width=1200, height=300)

    # show image for 1 second
    image = image.set_duration(1)

    # Set the position of the image
    image = image.set_position(("center", "center"))

    # Add subtitles to the video
    result = CompositeVideoClip([video, subs.set_position('center'), image])

    # Create the output directory if it doesn't exist
    output_dir = f"finished_videos/post_{post_num}"
    os.makedirs(output_dir, exist_ok=True)

    # Write the final video to file
    result.write_videofile(f"{output_dir}/video_{index}.mp4")

    return f"{output_dir}/video_{index}.mp4"
