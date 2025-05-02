# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re, logging
from pyrogram import Client, filters
from info import DELETE_CHANNELS
from database.ia_filterdb import col, sec_col, unpack_new_file_id

logger = logging.getLogger(__name__)
media_filter = filters.document | filters.video

@Client.on_message(filters.chat(DELETE_CHANNELS) & media_filter)
async def deletemultiplemedia(bot, message):
    """Delete Multiple files from database"""
    for file_type in ("document", "video", "audio"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return  # No media found in the message

    # Attempt to delete by file_id
    file_id = unpack_new_file_id(media.file_id)
    result = col.delete_one({'file_id': file_id})
    if not result.deleted_count and sec_col:
        result = sec_col.delete_one({'file_id': file_id})

    if result.deleted_count:
        logger.info(f"File with ID {file_id} successfully deleted from database.")
        return

    # Clean file_name for deletion by name and size
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
    unwanted_chars = ['[', ']', '(', ')']
    for char in unwanted_chars:
        file_name = file_name.replace(char, '')
    file_name = ' '.join(filter(lambda x: not x.startswith('@'), file_name.split()))
    logger.debug(f"Cleaned file_name for deletion: {file_name}")

    # Attempt to delete by file_name and file_size
    result = col.delete_many({'file_name': file_name, 'file_size': media.file_size})
    if not result.deleted_count and sec_col:
        result = sec_col.delete_many({'file_name': file_name, 'file_size': media.file_size})

    if result.deleted_count:
        logger.info(f"File with name '{file_name}' and size {media.file_size} successfully deleted from database.")
        return

    # Final attempt to delete with original file_name
    result = col.delete_many({'file_name': media.file_name, 'file_size': media.file_size})
    if not result.deleted_count and sec_col:
        result = sec_col.delete_many({'file_name': media.file_name, 'file_size': media.file_size})

    if result.deleted_count:
        logger.info(f"File with original name '{media.file_name}' and size {media.file_size} successfully deleted.")
    else:
        logger.warning(f"File with ID {file_id}, name '{media.file_name}', and size {media.file_size} not found in database.")
