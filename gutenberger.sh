#!/bin/bash

#
# Simple script to easily download books from Project Gutenberg
#

read -r -p "PG BOOK ID #: " BOOK_ID
read -r -p "BASE NAME: " BASE_NAME

BOOK_URL="https://www.gutenberg.org/ebooks/${BOOK_ID}.kindle.images"
BOOK_FILE_NAME="/mnt/volume_nyc1_01/media/Books/auto-add/${BASE_NAME}.mobi"

wget "${BOOK_URL}" -O "${BOOK_FILE_NAME}"
