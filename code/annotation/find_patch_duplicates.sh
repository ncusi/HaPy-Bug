#!/usr/bin/env bash
#

echo "Looking for diff duplicates" in $@
shopt -s nullglob

TMP_DIR=`mktemp -d`

for data in $@;
do
	for diff in $data/*/patches/*.diff;
	do
		fname=`echo $(basename $diff) |grep -v "\.\.\."`
		bug=`echo $diff | awk 'BEGIN { FS = "," }; { print $(NF-1)}'`
		if [ ! -z  "$fname" ];
		then
			OUT=$TMP_DIR/$diff
			mkdir -p $(dirname $OUT)
			cat $diff | grep "^[+-]" |grep -v "^[+-][+-][+-]" > "$OUT"&
		fi;
	done
done
fdupes -f -r $TMP_DIR > bug_duplicates

rm -r $TMP_DIR
