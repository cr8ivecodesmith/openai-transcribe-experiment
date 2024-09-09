#!/bin/bash

# Check if the correct number of parameters is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_directory> <output_directory>"
    exit 1
fi

input_dir="$1"
output_dir="$2"

# Create output directory if it doesn't exist
mkdir -p "$output_dir"

# Loop through all mp4 files in the input directory
for input_file in "$input_dir"/*.mp4; do
    if [ -f "$input_file" ]; then
        # Extract the filename without the path and extension
        filename=$(basename "$input_file" .mp4)

        # Convert the filename to snake_case and remove non-alphanumeric characters
        sanitized_filename=$(echo "$filename" | tr '[:upper:]' '[:lower:]' | tr -cs '[:alnum:]' '_')

        # Define the output mp3 file path
        output_file="$output_dir/${sanitized_filename}.mp3"

        # Run the ffmpeg command to convert mp4 to mp3
        ffmpeg -i "$input_file" -q:a 0 -map a "$output_file"

        echo "Converted $input_file to $output_file"
    else
        echo "No mp4 files found in $input_dir"
    fi
done

