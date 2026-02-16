#!/bin/sh
for f in "$1"/*; do
    [ -e "$f" ] || continue
    d=$(dirname "$f")
    b=$(basename "$f")
    n=$(echo "$b" | tr -d ' ')
    [ "$b" != "$n" ] && mv "$f" "$d/$n"
    [ -d "$d/$n" ] && $0 "$d/$n"
done
