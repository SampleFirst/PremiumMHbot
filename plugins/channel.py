from pyrogram import Client, filters
from info import CHANNELS, UPDATE_CHANNEL, IMDB_TEMPLATE
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from utils import get_poster
from database.ia_filterdb import save_file
from Script import script

media_filter = filters.document | filters.video | filters.audio

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    for file_type in ("document", "video", "audio"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return

    media.file_type = file_type
    media.caption = message.caption
    await save_file(media)

    # Extracting the search query and year from the file name
    file_name = media.file_name
    search_query = file_name.split(' (')[0]  # Using the part before the first ' (' as the search query
    year = None

    # Check if year is present in the file name
    if "(" in file_name and ")" in file_name:
        year_start = file_name.find("(") + 1
        year_end = file_name.find(")")
        year = file_name[year_start:year_end]

    # Get the IMDB data and poster based on the search query and year
    imdb = await get_poster(search_query, year)

    # Send log in UPDATE_CHANNEL with IMDB_TEMPLATE and IMDB poster
    if imdb:
        buttons = [
            [
                InlineKeyboardButton('Join', url='https://t.me/join')
            ]
        ]
        TEMPLATE = IMDB_TEMPLATE
        cap = TEMPLATE.format(
            query=search_query,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )

        if imdb.get('poster'):
            try:
                await bot.send_photo(chat_id=UPDATE_CHANNEL, photo=imdb['poster'], caption=cap, reply_markup=InlineKeyboardMarkup(buttons))
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                poster = imdb['poster'].replace('.jpg', '._V1_UX360.jpg')
                await bot.send_photo(chat_id=UPDATE_CHANNEL, photo=poster, caption=cap, reply_markup=InlineKeyboardMarkup(buttons))
            except Exception as e:
                logger.exception(e)
                await bot.send_message(chat_id=UPDATE_CHANNEL, text=cap, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await bot.send_message(chat_id=UPDATE_CHANNEL, text=cap, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await bot.send_message(chat_id=UPDATE_CHANNEL, text=f"Here is what I found for your query {search_query}")
