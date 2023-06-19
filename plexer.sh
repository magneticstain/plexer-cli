#!/bin/bash

#
# Plexer
# DESC: Normalize media files for use with Plex Media Server
#

# enable/disable debug mode
# DEBUG=true
DEBUG=false

INITIAL_MEDIA_DIR="$1"
if [ -z "${INITIAL_MEDIA_DIR}" ]
then
    echo "[ERROR] current directory for media required"
    exit 1
elif [ ! -d "${INITIAL_MEDIA_DIR}" ]
then
    echo "[ERROR] [ ${INITIAL_MEDIA_DIR} ] is not a directory"
    exit 1
fi


DST_MEDIA_DIR="$2"
if [ -z "${DST_MEDIA_DIR}" ]
then
	echo "[ERROR] destination directory for media required"
	exit 1
elif [ ! -d "${DST_MEDIA_DIR}" ]
then
	echo "[ERROR] [ ${DST_MEDIA_DIR} ] is not a directory"
	exit 1
fi

### FUNCTIONS
normalize_directory() {
	# ensure name of directory conforms to Plex naming standards
	echo "[INFO] normalizing directory..."

	# required to match formatting within function
	MEDIA_FILE_DIR="${MEDIA_FILE_DIR}/"
    
	# get parent directory of media file directory and append the base name to it to get the new media file directory name
	BASE_DIR=$(echo "${MEDIA_FILE_DIR}" | rev | cut -d'/' -f3- | rev)
	NEW_MEDIA_FILE_DIR="${BASE_DIR}/${BASE_NAME}/"

	if [ "${DEBUG}" = true ]
	then
		echo "[DEBUG] [ ${MEDIA_FILE_DIR} => ${NEW_MEDIA_FILE_DIR} ]"
	fi

    if [ "${MEDIA_FILE_DIR}" == "${NEW_MEDIA_FILE_DIR}" ]
	then
		echo "[INFO] current media directory and new media file directory are the same, not doing anything..."
	else
		if [ "${DEBUG}" = false ]
		then
			mv "${MEDIA_FILE_DIR}" "${NEW_MEDIA_FILE_DIR}"
        
			MEDIA_FILE_DIR="${NEW_MEDIA_FILE_DIR}"
		else
			echo "[DEBUG] debug enabled, not moving directory"
		fi
	fi
}

normalize_files() {
    echo "[INFO] normalizing media files..."

	# TODO: handle filenames with spaces to prevent reading in each word as a file
	for MEDIA_FILE in $(ls "${MEDIA_FILE_DIR}")
	do
		if [ "${DEBUG}" = true ]
		then
			echo "[DEBUG] FILE: ${MEDIA_FILE}"
		fi

		CURRENT_MEDIA_FILE_ABS_PATH="${MEDIA_FILE_DIR}/${MEDIA_FILE}"

        MEDIA_FILE_EXT=$(echo "${MEDIA_FILE}" | rev | cut -d'.' -f1 | rev)
		if [ "${MEDIA_FILE_EXT}" == "avi" ] || [ "${MEDIA_FILE_EXT}" == "mkv" ] || [ "${MEDIA_FILE_EXT}" == "mp4" ]
		then
			echo "[INFO] media file found - [ ${MEDIA_FILE} ] - renaming..."

			if [ "${DEBUG}" = false ]
			then
				# normalize file
				NEW_MEDIA_FILE_ABS_PATH="${MEDIA_FILE_DIR}/${BASE_NAME}.${MEDIA_FILE_EXT}"
				mv "${CURRENT_MEDIA_FILE_ABS_PATH}" "${NEW_MEDIA_FILE_ABS_PATH}"

				echo "[INFO] normalization complete - [ ${CURRENT_MEDIA_FILE_ABS_PATH} => ${NEW_MEDIA_FILE_ABS_PATH} ]"
			else
				echo "[DEBUG] debug enabled, not renaming files"
			fi
			
		else
			echo "[INFO] non-media file found - [ ${CURRENT_MEDIA_FILE_ABS_PATH} ] - deleting..."

			if [ "${DEBUG}" = false ]
			then
				rm "${CURRENT_MEDIA_FILE_ABS_PATH}"
			else
				echo "[DEBUG] debug enabled, not deleting file"
			fi
		fi
	done
}

move_media() {
	echo "[INFO] moving to target media directory..."

	if [ "${DEBUG}" = true ]
	then
    	echo "[DEBUG] [ ${MEDIA_FILE_DIR} => ${DST_MEDIA_DIR} ]"
	fi

	if [ "${DEBUG}" = false ]
	then
		mv "${MEDIA_FILE_DIR}" "${DST_MEDIA_DIR}"
	else
		echo "[DEBUG] debug enabled, not migrating media directories"
	fi
}

fix_media_file_perms() {
	if [ "${DEBUG}" = false ]
	then
		chown -R josh:media "${DST_MEDIA_DIR}"
		chmod -R 755 "${DST_MEDIA_DIR}"
	else
		echo "[DEBUG] debug enabled, not updating file permissions"
	fi
}


### MAIN
echo "[INFO] starting Plexer..."
echo "[INFO] INITIAL MEDIA DIR: [ ${INITIAL_MEDIA_DIR} ] // DESTINATION MEDIA DIR: [ ${DST_MEDIA_DIR} ]"

for MEDIA_FILE_DIR in ${INITIAL_MEDIA_DIR}*
do
	echo "[INFO] CURRENT MEDIA FILE DIR: ${MEDIA_FILE_DIR}"
	read -r -p "[PROMPT] BASE NAME: " BASE_NAME

	normalize_directory

	normalize_files

	move_media

	fix_media_file_perms
done
