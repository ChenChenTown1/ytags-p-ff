#!/usr/bin/env python3

import subprocess
import argparse
import re
from pathlib import Path

def get_main_part(filename):
    name = str(filename)
    
    if '｜' in name:
        main_part = name.split('｜')[0].strip()
    elif '|' in name:
        main_part = name.split('|')[0].strip()
    else:
        main_part = name
    
    patterns_to_remove = [
        r'\[[^\]]+\]',
        r'\.en_fixed',
        r'\.zh_fixed',
        r'_fixed',
        r'\.en',
        r'\.zh',
        r'\.srt$',
        r'\.mp4$',
        r'\.MP4$',
    ]
    
    for pattern in patterns_to_remove:
        main_part = re.sub(pattern, '', main_part)
    
    main_part = main_part.replace('The Henry Ford\'s Innovation Nation', '')
    main_part = main_part.replace('The Henry Ford’s Innovation Nation', '')
    main_part = main_part.replace('The Henry Fords Innovation Nation', '')
    main_part = main_part.replace('Innovation Nation', '')
    main_part = main_part.replace('Henry Ford', '')
    
    return main_part.strip()

def find_best_mp4_for_srt(srt_file, all_mp4_files):
    srt_path = Path(srt_file)
    srt_main = get_main_part(srt_path.name)
    
    if not srt_main:
        return None
    
    best_match = None
    best_score = 0
    
    for mp4 in all_mp4_files:
        mp4_main = get_main_part(mp4.name)
        
        if not mp4_main:
            continue
        
        score = 0
        
        if srt_main.lower() == mp4_main.lower():
            score = 1.0
        elif srt_main.lower() in mp4_main.lower():
            score = 0.8
        elif mp4_main.lower() in srt_main.lower():
            score = 0.8
        
        if score > best_score:
            best_score = score
            best_match = mp4
    
    if best_score < 0.5:
        return None
    
    return best_match

def get_real_mp4_files(mp4_list):
    return [mp4 for mp4 in mp4_list if not mp4.name.startswith('._')]

def add_subtitles(mp4_file, srt_file, output_dir=None):
    mp4_path = Path(mp4_file)
    srt_path = Path(srt_file)
    
    if output_dir:
        out_path = Path(output_dir) / f"{mp4_path.stem}_hardsub.mp4"
    else:
        out_path = mp4_path.parent / f"{mp4_path.stem}_hardsub.mp4"
    
    if out_path.exists():
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
        return result.returncode == 0
    except:
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
    
    processed_mp4s = set()
    ok = 0
    fail = 0
    
    for srt in srt_files:
        srt_main = get_main_part(srt.name)
        
        if not srt_main:
            continue
        
        best_mp4 = find_best_mp4_for_srt(srt, mp4_files)
        if not best_mp4:
            continue
        
        if best_mp4 in processed_mp4s:
            continue
        
        print(f"\n{srt.name}")
        print(f"-> {best_mp4.name}")
        
        if add_subtitles(best_mp4, srt, args.o):
            processed_mp4s.add(best_mp4)
            ok += 1
            print("OK")
        else:
            fail += 1
            print("Fail")
    
    print(f"\nDone: {ok} OK, {fail} Fail")

if __name__ == '__main__':
    main()
