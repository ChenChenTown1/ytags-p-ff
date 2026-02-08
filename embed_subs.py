#!/usr/bin/env python3
import os, subprocess, re

def find_video_for_srt(srt_file):
    srt_name = os.path.basename(srt_file).replace('_fixed.srt', '').lower()
    srt_dir = os.path.dirname(srt_file)
    
    for video in os.listdir(srt_dir or '.'):
        if video.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
            video_name = os.path.splitext(video)[0].lower()
            if video_name in srt_name or srt_name in video_name:
                return os.path.join(srt_dir or '.', video)
    
    return None

def embed_subtitle(video, srt, fontsize=24):
    output = video.replace('.mp4', '_subtitled.mp4')
    output = output.replace('.mkv', '_subtitled.mp4')
    output = output.replace('.avi', '_subtitled.mp4')
    output = output.replace('.mov', '_subtitled.mp4')
    
    cmd = [
        'ffmpeg', '-i', video,
        '-vf', f"subtitles={srt}:force_style='Alignment=2,Fontsize={fontsize},MarginV=40'",
        '-c:a', 'copy', '-y', output
    ]
    
    print(f'Embedding: {os.path.basename(video)} + {os.path.basename(srt)}')
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f'Success -> {os.path.basename(output)}\n')
        return True
    except subprocess.CalledProcessError as e:
        print(f'Failed: {e.stderr.decode()[:100]}\n')
        return False

def main():
    print('=' * 50)
    print('Subtitle Embedding Tool')
    print('=' * 50)
    
    fixed_srts = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('_fixed.srt'):
                fixed_srts.append(os.path.join(root, file))
    
    if not fixed_srts:
        print('No _fixed.srt files found')
        return
    
    success = 0
    for srt in fixed_srts:
        video = find_video_for_srt(srt)
        if video and embed_subtitle(video, srt):
            success += 1
    
    print(f'Completed: {success}/{len(fixed_srts)}')

if __name__ == '__main__':
    main()
