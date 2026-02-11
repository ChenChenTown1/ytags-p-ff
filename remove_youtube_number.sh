for file in *; do
    if [ -f "$file" ]; then
        newname=$(echo "$file" | sed 's/\[[^]]*\]//g')
        if [ "$file" != "$newname" ]; then
            mv "$file" "$newname"
        fi
    fi
done
