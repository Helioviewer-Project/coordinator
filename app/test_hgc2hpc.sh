#!/usr/bin/env bash
#
# Smoke-test /hgc2hpc (Heliographic Carrington -> Helioprojective) with curl and
# random data. By default it does one GET per random coordinate, then one POST
# batch with all of them. Pure bash + curl + awk + date, no extra tooling.
#
# Options:
#   -x   batch-only: skip the per-coordinate GETs and just POST the batch,
#        printing timing statistics (how long the server takes to answer).
#
# Usage:
#   ./app/test_hgc2hpc.sh                 # production, 5 random coords, earth
#   ./app/test_hgc2hpc.sh 10              # 10 coords
#   ./app/test_hgc2hpc.sh -x 100          # batch-only, 100 coords, with stats
#   BASE_URL=http://localhost:8000 ./app/test_hgc2hpc.sh -x 50
#   OBSERVER=mars TARGET=2015-01-01T00:00:00 ./app/test_hgc2hpc.sh 4
#
set -euo pipefail

BASE_URL="${BASE_URL:-https://coordinator.necdet.helioviewer.org}"
OBSERVER="${OBSERVER:-earth}"
TARGET="${TARGET:-2024-06-01T00:00:00}"
BATCH_ONLY=0
N=5

# Parse args: -x flag (any position) plus an optional coordinate count.
positional=()
for arg in "$@"; do
  case "$arg" in
    -x) BATCH_ONLY=1 ;;
    *) positional+=("$arg") ;;
  esac
done
[ "${#positional[@]}" -gt 0 ] && N="${positional[0]}"

echo "url=$BASE_URL  n=$N  observer=$OBSERVER  target=$TARGET  batch_only=$BATCH_ONLY"

# Random value helpers ($RANDOM is 0..32767).
rand_lat()  { awk -v r="$RANDOM" 'BEGIN { printf "%.4f", -89 + (r/32767)*178 }'; }  # -89..89
rand_lon()  { awk -v r="$RANDOM" 'BEGIN { printf "%.4f", (r/32767)*360 }'; }        # 0..360
rand_time() { date -u -d "2024-01-01 -$((RANDOM % 3650)) days" +"%Y-%m-%dT%H:%M:%S"; }

# Build the coordinate list (and, unless batch-only, GET each one individually).
coords=""
for i in $(seq 1 "$N"); do
  lat="$(rand_lat)"; lon="$(rand_lon)"; ct="$(rand_time)"

  if [ "$BATCH_ONLY" -eq 0 ]; then
    printf '\n[%d] lat=%s lon=%s coord_time=%s\n' "$i" "$lat" "$lon" "$ct"
    printf '  GET  -> '
    curl -sS --get "$BASE_URL/hgc2hpc" \
      --data-urlencode "lat=$lat" \
      --data-urlencode "lon=$lon" \
      --data-urlencode "coord_time=$ct" \
      --data-urlencode "target=$TARGET" \
      --data-urlencode "observer=$OBSERVER"
    echo
  fi

  [ -n "$coords" ] && coords="$coords,"
  coords="$coords{\"lat\":$lat,\"lon\":$lon,\"coord_time\":\"$ct\"}"
done

payload="{\"coordinates\":[$coords],\"target\":\"$TARGET\",\"observer\":\"$OBSERVER\"}"

if [ "$BATCH_ONLY" -eq 1 ]; then
  # POST the batch once and capture curl's timing breakdown. The body goes to a
  # temp file; the -w line gives the metrics (space-separated) on stdout.
  body="$(mktemp)"
  stats=$(curl -sS -X POST "$BASE_URL/hgc2hpc" \
    -H "Content-Type: application/json" \
    -d "$payload" \
    -o "$body" \
    -w '%{http_code} %{size_download} %{time_pretransfer} %{time_total}')
  read -r code size t_pre t_total <<<"$stats"

  # "server response" = wall-clock minus connection setup (DNS+TCP+TLS+request
  # send), i.e. time from sending the request to receiving the full response.
  server=$(awk -v a="$t_total" -v b="$t_pre" 'BEGIN { printf "%.4f", a - b }')
  returned=$(grep -o '"x":' "$body" | wc -l | tr -d ' ') || returned=0
  rate=$(awk -v n="$N" -v s="$server" 'BEGIN { if (s > 0) printf "%.1f", n / s; else printf "n/a" }')

  printf '\nPOST batch (%d coords) -- statistics\n' "$N"
  printf '  status:            %s\n' "$code"
  printf '  coords returned:   %s\n' "$returned"
  printf '  response size:     %s bytes\n' "$size"
  printf '  connection setup:  %ss  (DNS + TCP + TLS)\n' "$t_pre"
  printf '  server response:   %ss  (request sent -> full response)\n' "$server"
  printf '  total:             %ss\n' "$t_total"
  printf '  throughput:        %s coords/sec\n' "$rate"
  rm -f "$body"
else
  printf '\nPOST batch (%d coords) ->\n' "$N"
  curl -sS -X POST "$BASE_URL/hgc2hpc" \
    -H "Content-Type: application/json" \
    -d "$payload"
  echo
fi
