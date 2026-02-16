#!/bin/sh
for f in *; do
    [ -e "$f" ] || continue
    n=$(echo "$f" | tr -d ' ')
    [ "$f" != "$n" ] && mv "$f" "$n"
done
