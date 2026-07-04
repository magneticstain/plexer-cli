#!/usr/bin/env bash

set -euo pipefail
IFS=$'\n\t'

BASE_DIR="/tmp/plexer-e2e"
SRC_MEDIA_DIR="$BASE_DIR/plexer-cli-test"
DST_MEDIA_DIR="$BASE_DIR/plexer-cli-test-dst"

rm -rf $BASE_DIR && \
    mkdir -p $SRC_MEDIA_DIR $DST_MEDIA_DIR

# create media dirs
mkdir $SRC_MEDIA_DIR/'Blade Runner (1982) {edition-Final Cut}' \
    $SRC_MEDIA_DIR/'Blade Runner 2049 (2017)' \
    $SRC_MEDIA_DIR/'Once Upon A Time In China And America (1997) [BluRay] [1080p] [YTS.AM]' \
    $SRC_MEDIA_DIR/The.Black.Phone.2021.1080p.WEBRip.x265-RARBG

# generate test media files
cp tests/bootstrap/blank.mkv $SRC_MEDIA_DIR/'Blade Runner (1982) {edition-Final Cut}'/Blade.Runner.1982.Final.Cut.1080p.BluRay.x264.DTS-WiKi.mkv
cp tests/bootstrap/blank.mkv $SRC_MEDIA_DIR/'Blade Runner 2049 (2017)'/Blade.Runner.2049.1080p.BluRay.x264.BONE.mkv
cp tests/bootstrap/blank.mp4 $SRC_MEDIA_DIR/'Once Upon A Time In China And America (1997) [BluRay] [1080p] [YTS.AM]'/'Once Upon A Time In China And America (1997) [BluRay] [1080p] [YTS.AM].mp4'
cp tests/bootstrap/blank.mp4 $SRC_MEDIA_DIR/The.Black.Phone.2021.1080p.WEBRip.x265-RARBG/The.Black.Phone.2021.1080p.WEBRip.x265-RARBG.mkv
