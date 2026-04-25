#!/bin/bash
# Usage:
#   ./run.sh <day> submit   # morning
#   ./run.sh <day> save     # ~1 hour later, after the email

EMAIL="jinheon.baek@kaist.ac.kr"
DAY=$1
MODE=${2:-submit}

case $DAY in
    1) S="72 76"; O="72 74" ;;
    2) S="77 81"; O="75 77" ;;
    3) S="82 85"; O="78 80" ;;
    4) S="";      O="81 83" ;;
    5) S="";      O="84 85" ;;
    *) echo "Usage: $0 <1-5> [submit|save]"; exit 1 ;;
esac

if [ "$MODE" = "submit" ]; then
    [ -n "$S" ] && python submit_stanford.py $S "$EMAIL"
    [ -n "$O" ] && python submit_openaireview.py $O "$EMAIL"
elif [ "$MODE" = "save" ]; then
    [ -n "$S" ] && python save_stanford.py "access_tokens/stanford/$(echo $S | tr ' ' _).json"
    [ -n "$O" ] && python save_openaireview.py "access_tokens/openaireview/$(echo $O | tr ' ' _).json"
else
    echo "Mode must be 'submit' or 'save'"; exit 1
fi
