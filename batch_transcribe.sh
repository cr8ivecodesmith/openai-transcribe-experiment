#!/bin/bash

# Check if directory is passed as an argument
if [ -z "$1" ]; then
  echo "Usage: $0 <directory>"
  exit 1
fi

input_dir="$1"
output_dir="$2"

# Loop through all mp3 files in the directory
for file in "$input_dir"/*.mp3; do
  if [ -f "$file" ]; then
    echo "Processing file: $file"
    
    # Run the transcript conversion
    python transcribe.py "$file" -o "$output_dir"
    
    # Pause for 60 seconds
    echo "Pausing for 60 seconds..."
    sleep 60
  else
    echo "No mp3 files found in the directory."
  fi
done

