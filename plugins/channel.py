from pyrogram import Client, filters
from info import CHANNELS, UPDATE_CHANNEL, IMDB_TEMPLATE
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from utils import get_poster
from Script import script
import re

media_filter = filters.document | filters.video | filters.audio

# Your settings dictionary (update this as per your needs)
admin_settings = {
    "update": True  # Default value, you can change it
}

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    """Media Handler"""
    for file_type in ("document", "video", "audio"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return

    # Check if the message is a reply to another message
    if message.reply_to_message:
        # Save the original file message as a quote
        quote_message = await message.reply_to_message.copy()

    # Remove the original file message
    await message.delete()

    # Send the appropriate media type based on the detected type
    if file_type == "document":
        sent_message = await bot.send_document(message.chat.id, media.file_id, caption=message.caption)
    elif file_type == "video":
        sent_message = await bot.send_video(message.chat.id, media.file_id, caption=message.caption)
    elif file_type == "audio":
        sent_message = await bot.send_audio(message.chat.id, media.file_id, caption=message.caption)

    # Add file name and size to the channel
    file_name = media.file_name
    file_size = media.file_size

    # Extracting the search query from the file name
    full_file_name = media.file_name.replace('_', ' ').replace('(', ' ').replace(')', ' ').replace('.', ' ')
    file_name = ""

    # Extract year using regular expression
    year_match = re.search(r'\b\d{4}\b', file_name)
    year = year_match.group() if year_match else "N/A"

    # Extract video resolution using regular expression
    video_resolution_match = re.search(r'\b\d{3,4}p\b', file_name)
    video_resolution = video_resolution_match.group() if video_resolution_match else "N/A"

    # Extract video format using regular expression
    video_format_match = re.search(r'(Bluray|HDRip|WEB-DL|WebRip)', file_name)
    video_format = video_format_match.group() if video_format_match else "N/A"

    # Extract HEVC match
    hevc_match = re.search(r'HEVC', file_name)

    # Extract HEVC match
    uncut_match = re.search(r'UNCUT|UnCut', file_name)

    # Extract audio codec using regular expression
    audio_codec_match = re.search(r'(\dx|H{3})', file_name)
    audio_codec = audio_codec_match.group() if audio_codec_match else "N/A"

    # Extract subtitle match
    sub_match = re.search(r'(Subtitle|ESub|MSub|Hindi-Sub|HC-Sub)', file_name)

    # Define LANGUAGE_KEYWORDS dictionary
    LANGUAGE_KEYWORDS = {
        'English': ['English', 'english', 'Eng', 'eng'],
        'Marathi': ['Marathi', 'marathi', 'Mar', 'mar'],
        'Hindi': ['Hindi', 'hindi', 'Hin', 'hin'],
        'Malayalam': ['Malayalam', 'malayalam', 'Mal', 'mal'],
        'Kannada': ['Kannada', 'kannada', 'Kan', 'kan'],
        'Bengali': ['Bengali', 'bengali', 'Ben', 'ben'],
        'Punjabi': ['Punjabi', 'punjabi', 'Pun', 'pun'],
        'Bhojpuri': ['Bhojpuri', 'bhojpuri', 'Bhoj', 'bhoj'],
        'Korean': ['Korean', 'korean', 'Kor', 'kor'],
        'Chinese': ['Chinese', 'chinese', 'Chi', 'chi']
    }

    # Extract language match using regular expression
    language_match = "N/A"
    for language, keywords in LANGUAGE_KEYWORDS.items():
        if any(keyword in file_name for keyword in keywords):
            language_match = language
            break

    series_season_match = re.search(r'\b[Ss]|Season\b\d+\b', full_file_name)
    season_episode_match = re.search(r'\bSeason\b\s*(\d+)\b.*?\bEpisode\b\s*(\d+)\b', full_file_name)

    if year_match:
        file_name = re.search(r'^.*?(?=\d{4}\b|\b[Ss]|Season\b\d+\b)', full_file_name).group().strip()
    elif series_season_match:
        file_name = re.search(r'^.*?(?=\b[Ss]|Season\b\d+\b)', full_file_name).group().strip()

    # Construct the info_text with the extracted information
    info_text = ""
    if season_episode_match:
        info_text += f"Title 🎬: {file_name} ({year or ''})\nSeries Info: Season {season_episode_match.group(1)} Episode {season_episode_match.group(2)}\nQuality 💿: {video_resolution} {hevc_match or ''} {uncut_match or ''} {video_format} {audio_codec or ''}\nAudio 🔊: #{language_match} {(sub_match) or ''}"
    else:
        info_text += f"Title 🎬: {file_name} ({year or ''})\nQuality 💿: {video_resolution} {hevc_match or ''} {uncut_match or ''} {video_format} {audio_codec or ''}\nAudio 🔊: #{language_match} {(sub_match) or ''}"

    # Edit the sent message with new text
    await sent_message.edit_text(info_text)

    # Save the file to the database
    media.file_type = file_type
    media.caption = message.caption
    await save_file(media)

    # Extracting the search query from the file name
    full_file_name = media.file_name.replace('_', ' ').replace('(', ' ').replace(')', ' ').replace('.', ' ')
    file_name = ""

    # Detecting the year in 4-digit number format
    year_match = re.search(r'\b\d{4}\b', full_file_name)

    # Updated: Detecting series season using a more comprehensive pattern
    series_season_match = re.search(r'\b[Ss]|Season\b\d+\b', full_file_name)

    if year_match or series_season_match:
        # Extracting the part before year or series season
        file_name = re.search(r'^.*?(?=\d{4}\b|\b[Ss]|Season\b\d+\b)', full_file_name).group().strip()

    if not file_name:
        # If no year or series season is found, use the  entire file name
        file_name = full_file_name

    # Detecting Episodes match
    series_season_episode_match = re.search(r'\b[Ee]|Episode\b\d+\b', full_file_name)

    # Detecting video resolution
    video_resolution_match = re.search(r'\b\d{3,4}p\b', file_name)
    video_resolution = video_resolution_match.group() if video_resolution_match else None

    LANGUAGE_KEYWORDS = {
        'English': ['English', 'english', 'Eng', 'eng'],
        'Marathi': ['Marathi', 'marathi', 'Mar', 'mar'],
        'Hindi': ['Hindi', 'hindi', 'Hin', 'hin'],
        'Malayalam': ['Malayalam', 'malayalam', 'Mal', 'mal'],
        'Kannada': ['Kannada', 'kannada', 'Kan', 'kan'],
        'Bengali': ['Bengali', 'bengali', 'Ben', 'ben'],
        'Punjabi': ['Punjabi', 'punjabi', 'Pun', 'pun'],
        'Bhojpuri': ['Bhojpuri', 'bhojpuri', 'Bhoj', 'bhoj'],
        'Korean': ['Korean', 'korean', 'Kor', 'kor'],
        'Chinese': ['Chinese', 'chinese', 'Chi', 'chi']
    }

    language_match = LANGUAGE_KEYWORDS

    if year_match:
        # Remove the year from the file name
        file_name_without_year = file_name.replace(year_match.group(), '').strip()

        # Combine the file name and year for search query
        search_query = f"{file_name_without_year} {year_match.group()}"
    else:
        # If year is not found, use entire file name for search query
        search_query = file_name

    # Check if the "update" setting is enabled
    if admin_settings["update"]:
        # Get IMDb data and poster based on search query
        imdb = await get_poster(search_query)

        # Send log in UPDATE_CHANNEL with IMDB_TEMPLATE and IMDb poster
        if imdb:
            buttons = [
                [
                    InlineKeyboardButton('Join', url='https://t.me/PremiumMHBot'),
                    InlineKeyboardButton('Join', url='https://t.me/PremiumMHBot')
                ],
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
            await bot.send_message(chat_id=UPDATE_CHANNEL, text=f"New File Added In Bot\n{file_name}")

    else:
        # Your code to send IMDb poster with FILE_INFO format
        file_info_caption = FILE_INFO.format(
            title=f"Title 🎬: {imdb['title']}\nQuality 💿 : {video_resolution}\nAudio 🔊: {language_match}",
            search_query=search_query
        )
        if imdb.get('poster'):
            try:
                await bot.send_photo(chat_id=UPDATE_CHANNEL, photo=imdb['poster'], caption=file_info_caption)
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                poster = imdb['poster'].replace('.jpg', '._V1_UX360.jpg')
                await bot.send_photo(chat_id=UPDATE_CHANNEL, photo=poster, caption=file_info_caption)
            except Exception as e:
                logger.exception(e)
                await bot.send_message(chat_id=UPDATE_CHANNEL, text=file_info_caption)
        else:
            await bot.send_message(chat_id=UPDATE_CHANNEL, text=file_info_caption)

@Client.on_message(filters.command("admin_settings"))
async def admin_settings_command(bot, message):
    # Assuming this command is meant to be sent only in private chats with the bot
    buttons = [
        [
            InlineKeyboardButton('IMDB Button', callback_data='imdb_button'),
            InlineKeyboardButton('🔘 ON' if admin_settings["update"] else '🔳 OFF', callback_data='toggle_update')
        ]
    ]
    await message.reply_text("Admin Settings:", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex('^imdb_button$'))
async def imdb_button_callback(bot, callback_query: CallbackQuery):
    # Your logic for sending IMDb data here...
    await query.answer(text="ℹ️ Here is the detailed information:", show_alert=True)

@Client.on_callback_query(filters.regex('^toggle_update$'))
async def toggle_update_callback(bot, callback_query: CallbackQuery):
    admin_settings["update"] = not admin_settings["update"]

    new_button_text = '🔘 ON' if admin_settings["update"] else '🔳 OFF'
    buttons = [
        [
            InlineKeyboardButton('IMDB Button', callback_data='imdb_button'),
            InlineKeyboardButton(new_button_text, callback_data='toggle_update')
        ]
    ]

    await callback_query.message.edit_text("Admin Settings:", reply_markup=InlineKeyboardMarkup(buttons))
    await callback_query.answer(text="Update setting has been changed.")
