#!/bin/bash

#
# Plexer
# DESC: Normalize media files for use with Plex Media Server
#

INITIAL_MEDIA_DIR="$1"
if [ -z "${INITIAL_MEDIA_DIR}" ]
then
        echo "ERROR: current directory for media required"
        exit 1
elif [ ! -d "${INITIAL_MEDIA_DIR}" ]
then
        echo "ERROR: [ ${INITIAL_MEDIA_DIR} ] is not a directory"
        exit 1
fi


DST_MEDIA_DIR="$2"
if [ -z "${DST_MEDIA_DIR}" ]
then
	echo "ERROR: destination directory for media required"
	exit 1
elif [ ! -d "${DST_MEDIA_DIR}" ]
then
	echo "ERROR: [ ${DST_MEDIA_DIR} ] is not a directory"
	exit 1
fi

### FUNCTIONS
normalize_directory() {
	echo "Normalizing directory..."
        
	BASE_DIR=$(echo "${MEDIA_FILE_DIR}" | rev | cut -d'/' -f3- | rev)
	NEW_MEDIA_FILE_DIR="${BASE_DIR}/${BASE_NAME}/"

	echo "[ ${MEDIA_FILE_DIR} => ${NEW_MEDIA_FILE_DIR} ]"

        if [ "${MEDIA_FILE_DIR}" == "${NEW_MEDIA_FILE_DIR}" ]
	then
		echo "[INFO] current media directory and new media file directory are the same, not doing anything..."
	else
		mv "${MEDIA_FILE_DIR}" "${NEW_MEDIA_FILE_DIR}"
        
		MEDIA_FILE_DIR="${NEW_MEDIA_FILE_DIR}"
	fi
}

normalize_files() {
        echo "Normalizing media files..."

	for MEDIA_FILE in "${MEDIA_FILE_DIR}"/*
	do
        	MEDIA_FILE_EXT=$(echo "${MEDIA_FILE}" | rev | cut -d'.' -f1 | rev)
		if [ "${MEDIA_FILE_EXT}" == "avi" ] || [ "${MEDIA_FILE_EXT}" == "mkv" ] || [ "${MEDIA_FILE_EXT}" == "mp4" ]
		then
			# normalize file
			NEW_MEDIA_FILE="${NEW_MEDIA_FILE_DIR}/${BASE_NAME}.${MEDIA_FILE_EXT}"

			echo "Media file found [ ${MEDIA_FILE} ], renaming..."
			mv "${MEDIA_FILE}" "${NEW_MEDIA_FILE}"
        		echo "[ ${MEDIA_FILE} => ${NEW_MEDIA_FILE} ]"
		else
			# delete it
			echo "Non-media file found [ ${MEDIA_FILE} ], deleting..."
			rm "${MEDIA_FILE}"
		fi
	done
}

move_media() {
	echo "Moving to target media directory..."
        echo "[ ${NEW_MEDIA_FILE_DIR} => ${DST_MEDIA_DIR} ]"
	mv "${NEW_MEDIA_FILE_DIR}" "${DST_MEDIA_DIR}"
}

fix_media_file_perms() {
        chown -R josh:media "${DST_MEDIA_DIR}"
        chmod -R 775 "${DST_MEDIA_DIR}"
}


### MAIN
echo "Starting Plexer..."
echo "============================="
echo "INITIAL MEDIA DIR: [ ${INITIAL_MEDIA_DIR} ] // DESTINATION MEDIA DIR: [ ${DST_MEDIA_DIR} ]"
echo ""

for MEDIA_FILE_DIR in /mnt/volume_nyc1_01/media/Completed/*
do
	MEDIA_FILE_DIR="${MEDIA_FILE_DIR}/"

	echo "############################################"
	echo "CURRENT MEDIA DIR: ${MEDIA_FILE_DIR}"

	read -r -p "BASE NAME: " BASE_NAME

	echo ""
	normalize_directory
	echo ""
	normalize_files
	echo ""
	move_media
	fix_media_file_perms
	echo "############################################"
done
