	tdirs=()
	for d in "$projects/$(slugify "$main_wt")"* "$projects/$(slugify "$wt")"*; do
		[ -d "$d" ] && tdirs+=("$d")
	done
	if [ "${#tdirs[@]}" -gt 0 ]; then
		f=$(rg -l -e "${wt}/" -e "${wt}\"" "${tdirs[@]}" 2>/dev/null \
			| while read -r p; do stat "${stat_fmt[@]}" "$p" 2>/dev/null; done | sort -rn | head -1)
		if [ -n "$f" ]; then last_ts=$(echo "$f" | awk '{print $1}')
			last=$(fmt_day "$last_ts" 2>/dev/null); fi
