#!/bin/bash
FOLDER="${1:-$(pwd)}"
OUTPUT="$FOLDER/output_with_subtitles"
mkdir -p "$OUTPUT"

find "$FOLDER" -maxdepth 1 -name "*.mp4" -o -name "*.MP4" | while read mp4; do
    base=$(basename "$mp4" .mp4)
    base=${base%.MP4}
    dir=$(dirname "$mp4")
    
    srt="$dir/$base.srt"
    [ -f "$srt" ] || srt="$dir/$base.SRT"
    [ -f "$srt" ] || continue
    
    echo "Processing: $base"
    ffmpeg -i "$mp4" -vf "subtitles='$srt':force_style='FontName=SourceHanSansCN-Bold,FontSize=15,PrimaryColour=&H00FFFFFF,OutlineColour=&H66000000,BorderStyle=3'" -c:v libx264 -crf 19 -c:a copy -y "$OUTPUT/${base}_subtitled.mp4"
done

echo "Output folder: $OUTPUT"
