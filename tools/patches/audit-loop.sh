	tdirs=()
	for d in "$projects/$(slugify "$main_wt")"* "$projects/$(slugify "$wt")"*; do
		[ -d "$d" ] && tdirs+=("$d")
	done
	if [ "${#tdirs[@]}" -gt 0 ]; then
		f=$(rg -l -e "${wt}/" -e "${wt}\"" "${tdirs[@]}" 2>/dev/null \
			| while read -r p; do mtime "$p"; done | sort -rn | head -1)
		if [ -n "$f" ]; then last_ts=$(echo "$f" | awk '{print $1}')
			last=$(date -r "$last_ts" '+%Y-%m-%d' 2>/dev/null || date -d "@$last_ts" '+%Y-%m-%d'); fi
