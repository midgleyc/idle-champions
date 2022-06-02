if [ $# -eq 0 ]; then
  echo "Usage: ./super.sh <id>"
  exit 1
fi

for i in "$@"; do
  ./master.sh $i
done
