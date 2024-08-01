if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <audio_file> <text_file>"
    exit 1
fi


audio_file="$1"
text_file="$2"
output_file="map.json"

python3 -m aeneas.tools.execute_task "$audio_file" "$text_file" "task_language=en|os_task_file_format=json|is_text_type=plain" "$output_file"
