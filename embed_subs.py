#!/usr/bin/env python3
import os, subprocess, glob, re

def clean_name(name):
    return re.sub(r'\[.*?\]|\.en|\.srt|\.mp4', '', name.lower().strip())

def find_matching_mp4(srt_file):
    srt_name = clean_name(os.path.basename(srt_file).replace('_fixed.srt', ''))
    
    mp4_files = glob.glob('**/*.mp4', recursive=True) + glob.glob('**/*.MP4', recursive=True)
    
    for mp4 in mp4_files:
        mp4_name = clean_name(os.path.basename(mp4))
        
        if srt_name in mp4_name or mp4_name in srt_name:
            return mp4
        
        srt_words = set(srt_name.split())
        mp4_words = set(mp4_name.split())
        if srt_words.intersection(mp4_words):
            return mp4
    
    return None

def embed_subtitle(video, srt):
    video_base = os.path.splitext(video)[0]
    output = f"{video_base}_subtitled.mp4"
    
    srt_escaped = srt.replace("'", "'\\''")
    filter_str = f"subtitles='{srt_escaped}':force_style='Alignment=2,Fontsize=24,MarginV=40'"
    
    cmd = [
        'ffmpeg',
        '-i', video,
        '-vf', filter_str,
        '-c:a', 'copy',
        '-y',
        output
    ]
    
    print(f'Processing: {os.path.basename(video)}')
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f'Success: {os.path.basename(output)}\n')
            return True
        else:
            error_msg = result.stderr[:300] if result.stderr else 'Unknown error'
            print(f'FFmpeg failed: {error_msg}\n')
            return False
    except Exception as e:
        print(f'Error: {e}\n')
        return False

def main():
    fixed_srts = glob.glob('**/*_fixed.srt', recursive=True)
    
    if not fixed_srts:
        print('No _fixed.srt files found')
        return
    
    print(f'Found {len(fixed_srts)} _fixed.srt files\n')
    
    success = 0
    for srt in fixed_srts:
        mp4 = find_matching_mp4(srt)
        if mp4:
            print(f'Match: {os.path.basename(srt)} -> {os.path.basename(mp4)}')
            if embed_subtitle(mp4, srt):
                success += 1
        else:
            print(f'No match for: {os.path.basename(srt)}')
    
    print(f'Completed: {success}/{len(fixed_srts)}')

if __name__ == '__main__':
    main()
