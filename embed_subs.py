#!/usr/bin/env python3

import subprocess
import argparse
import re
from pathlib import Path
from difflib import SequenceMatcher

def clean_name(filename):
    name = str(filename)
    name = re.sub(r'\[[^\]]+\]', '', name)
    name = name.split('.')[0]
    name = name.replace('_fixed', '')
    name = name.replace('.en', '').replace('.zh', '')
    return name.strip()

def get_real_mp4_files(mp4_list):
    real_files = []
    for mp4 in mp4_list:
        if not mp4.name.startswith('._'):
            real_files.append(mp4)
    return real_files

def find_best_mp4_for_srt(srt_file, all_mp4_files):
    srt_path = Path(srt_file)
    srt_name_clean = clean_name(srt_path.name)
    
    best_match = None
    best_score = 0
    
    for mp4 in all_mp4_files:
        mp4_name_clean = clean_name(mp4.name)
        
        score = SequenceMatcher(None, srt_name_clean.lower(), mp4_name_clean.lower()).ratio()
        
        if srt_name_clean.lower() in mp4_name_clean.lower():
            score = max(score, 0.8)
        
        if mp4_name_clean.lower() in srt_name_clean.lower():
            score = max(score, 0.8)
        
        if score > best_score:
            best_score = score
            best_match = mp4
    
    return best_match if best_score > 0.5 else None

def add_subtitles(mp4_file, srt_file, output_dir=None):
    mp4_path = Path(mp4_file)
    srt_path = Path(srt_file)
    
    if output_dir:
        out_path = Path(output_dir) / f"{mp4_path.stem}_hardsub.mp4"
    else:
        out_path = mp4_path.parent / f"{mp4_path.stem}_hardsub.mp4"
    
    if out_path.exists():
        print("  Output exists, skipping")
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
        print(f"  Running ffmpeg...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  Success")
            return True
        else:
            print(f"  Failed")
            if result.stderr:
                for line in result.stderr.split('\n')[-5:]:
                    if line.strip():
                        print(f"    {line}")
            return False
    except Exception as e:
        print(f"  Exception: {e}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', nargs='?', default='.')
    parser.add_argument('-r', action='store_true')
    parser.add_argument('-o')
    
    args = parser.parse_args()
    
    path = Path(args.dir)
    
    if args.r:
        all_mp4_files = list(path.rglob('*.mp4')) + list(path.rglob('*.MP4'))
        srt_files = list(path.rglob('*_fixed.srt')) + list(path.rglob('*_fixed.SRT'))
    else:
        all_mp4_files = list(path.glob('*.mp4')) + list(path.glob('*.MP4'))
        srt_files = list(path.glob('*_fixed.srt')) + list(path.glob('*_fixed.SRT'))
    
    mp4_files = get_real_mp4_files(all_mp4_files)
    
    print(f"MP4: {len(mp4_files)}, SRT: {len(srt_files)}")
    
    if mp4_files:
        print("Available MP4 files:")
        for mp4 in mp4_files:
            print(f"  - {mp4.name}")
    
    ok = 0
    fail = 0
    
    for srt in srt_files:
        print(f"\n{srt.name}")
        
        best_mp4 = find_best_mp4_for_srt(srt, mp4_files)
        if not best_mp4:
            print(f"No match found")
            fail += 1
            continue
        
        print(f"Match: {best_mp4.name}")
        
        if add_subtitles(best_mp4, srt, args.o):
            ok += 1
        else:
            fail += 1
    
    print(f"\nDone: {ok} OK, {fail} Fail")

if __name__ == '__main__':
    main()
