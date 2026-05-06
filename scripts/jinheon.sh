#!/bin/bash
# Usage:
#   ./run.sh <day> submit   # morning
#   ./run.sh <day> save     # ~1 hour later, after the email

EMAIL="jinheon.baek@kaist.ac.kr"
DAY=$1
MODE=${2:-submit}

case $DAY in
    0) S="72 76"; O=""      ;;
    1) S="77 81"; O="77 79" ;;
    2) S="82 85"; O="80 82" ;;
    3) S="";      O="72 74" ;;
    4) S="";      O="75 76" ;;
    5) S="";      O="83 85" ;;
    *) echo "Usage: $0 <0-5> [submit|save]"; exit 1 ;;
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
