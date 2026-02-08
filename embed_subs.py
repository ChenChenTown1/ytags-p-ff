#!/usr/bin/env python3

import subprocess
import argparse
import re
from pathlib import Path
from difflib import SequenceMatcher

def extract_main_title(filename):
    name = str(filename)
    
    patterns_to_remove = [
        r'\[[^\]]+\]',  # 移除YouTube ID
        r'\.en_fixed',  # 移除后缀
        r'\.zh_fixed',
        r'\.en',
        r'\.zh',
        r'_fixed',
        r'\.srt$',
        r'\.mp4$',
        r'\.MP4$',
    ]
    
    for pattern in patterns_to_remove:
        name = re.sub(pattern, '', name)
    
    return name.strip()

def get_common_words(text):
    words = re.findall(r'\b\w+\b', text.lower())
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'has', 'have', 'had', 'do', 'does', 'did', 'will', 'would', 'shall', 'should', 'may', 'might', 'must', 'can', 'could', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs'}
    return [word for word in words if word not in common_words and len(word) > 2]

def calculate_similarity(text1, text2):
    text1_clean = extract_main_title(text1)
    text2_clean = extract_main_title(text2)
    
    words1 = get_common_words(text1_clean)
    words2 = get_common_words(text2_clean)
    
    if not words1 or not words2:
        return 0
    
    common_count = len(set(words1) & set(words2))
    total_unique = len(set(words1) | set(words2))
    
    if total_unique == 0:
        return 0
    
    word_similarity = common_count / total_unique
    
    sequence_similarity = SequenceMatcher(None, text1_clean.lower(), text2_clean.lower()).ratio()
    
    return max(word_similarity, sequence_similarity)

def find_best_mp4_for_srt(srt_file, all_mp4_files):
    srt_path = Path(srt_file)
    
    best_match = None
    best_score = 0
    
    for mp4 in all_mp4_files:
        score = calculate_similarity(srt_path.name, mp4.name)
        
        if score > best_score:
            best_score = score
            best_match = mp4
    
    if best_score < 0.3:
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
        print("  Skip: exists")
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
            print("  Success")
            return True
        else:
            print("  Failed")
            return False
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
    
    if mp4_files:
        print("MP4 files:")
        for mp4 in mp4_files:
            clean = extract_main_title(mp4.name)
            print(f"  - {mp4.name}")
            print(f"    Clean: {clean}")
    
    ok = 0
    fail = 0
    
    for srt in srt_files:
        print(f"\n{srt.name}")
        print(f"Clean: {extract_main_title(srt.name)}")
        
        best_mp4 = find_best_mp4_for_srt(srt, mp4_files)
        if not best_mp4:
            print("No match")
            fail += 1
            continue
        
        score = calculate_similarity(srt.name, best_mp4.name)
        print(f"Match: {best_mp4.name} (score: {score:.2f})")
        
        if add_subtitles(best_mp4, srt, args.o):
            ok += 1
        else:
            fail += 1
    
    print(f"\nDone: {ok} OK, {fail} Fail")

if __name__ == '__main__':
    main()
