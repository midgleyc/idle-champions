if [ $# -eq 0 ]; then
  echo "Usage: ./master.sh <id>"
  exit 1
fi

url=$(< $FULLJS jq -r '.graphic_defines | map(select(.id == '"$*"')) | .[0] | "https://ps20.idlechampions.com/~idledragons/mobile_assets/\(.graphic)"')
filename="$(basename "$url").png"

wget "$url" -O "$filename"

if $(file $filename | grep -q 'zlib compressed data'); then
  ./decompress_image.sh "$filename"
fi

./fixup_png.py "$filename"
mogrify -trim +repage "$filename"
optipng "$filename"

mv "$filename" $OUTPUT_BASE_DIR/portraits
