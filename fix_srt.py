#!/usr/bin/env python3
import os, sys, glob

for srt in glob.glob("**/*.srt", recursive=True):
    try:
        with open(srt, "rb") as f:
            content = f.read().decode("utf-8", errors="ignore")
        
        lines = [l.strip() for l in content.replace("\r", "").split("\n")]
        blocks, block = [], []
        for line in lines:
            if not line and block:
                blocks.append(block)
                block = []
            elif line:
                block.append(line)
        if block: blocks.append(block)
        
        subs = []
        for b in blocks:
            if len(b) > 2 and b[0].isdigit() and "-->" in b[1]:
                s, e = b[1].split("-->", 1)
                subs.append([s.strip(), e.strip(), " ".join(b[2:])])
        
        for i in range(len(subs)-1):
            subs[i][1] = subs[i+1][0]
        
        out = srt.replace(".srt", "_fixed.srt")
        with open(out, "w", encoding="utf-8") as f:
            for n, (st, ed, txt) in enumerate(subs, 1):
                f.write(f"{n}\n{st} --> {ed}\n{txt}\n\n")
        
        print(f"✓ {srt} -> {len(subs)}lines")
    except:
        print(f"✗ {srt}")
