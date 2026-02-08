#!/usr/bin/env python3

import subprocess
import argparse
from pathlib import Path
from difflib import SequenceMatcher

def find_mp4_for_srt(srt_file):
    srt_path = Path(srt_file)
    srt_name = srt_path.stem.replace('_fixed', '')
    
    for mp4 in srt_path.parent.glob('*.mp4'):
        mp4_name = mp4.stem
        score = SequenceMatcher(None, srt_name.lower(), mp4_name.lower()).ratio()
        if srt_name.lower() in mp4_name.lower():
            score += 0.2
        if score > 0.3:
            return mp4
    return None

def add_subtitles(mp4_file, srt_file, output_dir=None):
    mp4_path = Path(mp4_file)
    srt_path = Path(srt_file)
    
    if output_dir:
        out_path = Path(output_dir) / f"{mp4_path.stem}_hardsub.mp4"
    else:
        out_path = mp4_path.parent / f"{mp4_path.stem}_hardsub.mp4"
    
    if out_path.exists():
        print(f"Skip: {out_path.name} exists")
        return False
    
    style = "FontName=SourceHanSansCN-Bold,FontSize=15,PrimaryColour=&H00FFFFFF,OutlineColour=&H66000000,BorderStyle=3"
    
    cmd = [
        'ffmpeg',
        '-i', str(mp4_path),
        '-vf', f"subtitles={repr(str(srt_path))}:force_style={repr(style)}",
        '-c:v', 'libx264',
        '-crf', '19',
        '-c:a', 'copy',
        '-y',
        str(out_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"OK: {mp4_path.name}")
            return True
        else:
            print(f"Fail: {mp4_path.name}")
            return False
    except:
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', nargs='?', default='.')
    parser.add_argument('-r', action='store_true')
    parser.add_argument('-o')
    
    args = parser.parse_args()
    
    srt_files = []
    path = Path(args.dir)
    
    if args.r:
        srt_files = list(path.rglob('*_fixed.srt')) + list(path.rglob('*_fixed.SRT'))
    else:
        srt_files = list(path.glob('*_fixed.srt')) + list(path.glob('*_fixed.SRT'))
    
    ok = 0
    fail = 0
    
    for srt in srt_files:
        mp4 = find_mp4_for_srt(srt)
        if not mp4:
            print(f"No MP4 for {srt.name}")
            fail += 1
            continue
        
        print(f"\n{srt.name} -> {mp4.name}")
        
        if add_subtitles(mp4, srt, args.o):
            ok += 1
        else:
            fail += 1
    
    print(f"\nDone: {ok} OK, {fail} Fail")

if __name__ == '__main__':
    main()
