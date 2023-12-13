import random
import logging
import datetime
import pytz

from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, Message
from pyrogram import Client, filters, enums
from pyrogram.errors import MessageNotModified, PeerIdInvalid

from info import ADMINS, PICS
from database.users_chats_db import db

from Script import script
from utils import temp

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

@Client.on_message(filters.photo & filters.private)
async def handle_payment_screenshot(client: Client, message: Message, bot_name: str):
    # Wait for the user to send a screenshot
    user_id = message.from_user.id
    user_name = message.from_user.username
    if message.photo:
        # Send message to user and admin about payment screenshot received      
        admin_notification = f"{user_name}'s payment screenshot has been received for {bot_name}, Checking the payment..."
        user_notification = "Payment screenshot received. ADMINS will check the payment."
        for admin_id in ADMINS:
            await client.send_photo(user_id=admin_id, photo=message.photo.file_id, caption=admin_notification)
        await message.reply_text(user_notification)
    else:
        # If user sends anything other than a photo
        for admin_id in ADMINS:
            await client.send_message(admin_id, "Process cancelled for user who tried to buy a premium plan.")
        await message.reply_text("Process cancelled!")
        await message.reply_text("Process cancelled!")


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    is_admin = query.from_user.id in ADMINS
    if query.data == "close_data":
        await query.message.delete()

    elif query.data == "start":
        buttons = [
            [
                    InlineKeyboardButton('Bots Premium', callback_data="bots"),
                    InlineKeyboardButton('Database Premium', callback_data="database")
                ]
            ]
        reply_markup = InlineKeyboardMarkup(buttons)
        caption = script.START_TXT.format(user=query.from_user.mention, bot=temp.B_LINK)

        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=caption,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "bots":
        buttons = [
            [
                InlineKeyboardButton('Movies Bot', callback_data='mbot'),
                InlineKeyboardButton('Anime Bot', callback_data='abot')
            ],
            [
                InlineKeyboardButton('Rename Bot', callback_data='rbot'),
                InlineKeyboardButton('Yt & Insta Bot', callback_data='yibot')
            ],
            [
                InlineKeyboardButton('Back', callback_data='start')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.BOTS.format(user=query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "database":
        buttons = [
            [
                InlineKeyboardButton('Movies Database', callback_data='mdb'),
                InlineKeyboardButton('Anime Database', callback_data='adb')
            ],
            [
                InlineKeyboardButton('TV Show Database', callback_data='tvsdb'),
                InlineKeyboardButton('Back', callback_data='start')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.DATABSE.format(user=query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "mbot" or query.data == "abot" or query.data == "rbot" or query.data == "yibot":
        # Display monthly plan message for selected bot
        validity_date = datetime.datetime.now() + datetime.timedelta(days=30)
        validity_formatted = validity_date.strftime("%B %d, %Y")

        buttons = [
            [
                InlineKeyboardButton('Confirmed', callback_data=f'confirm_bot_{query.data}'),
                InlineKeyboardButton('Description', callback_data=f'description_{query.data}')
            ],
            [
                InlineKeyboardButton('Back', callback_data='bots')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        message_text = f"🍿 **{query.data.capitalize()} Premium Plan** 🍿\n\n"
        message_text += f"This plan is valid until {validity_date}.\n\n"
        message_text += "Make Payments And Then Select **Confirmed** Button:"
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=message_text,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.MARKDOWN
        )

    elif query.data.startswith("confirm_bot_"):
        # Handle user confirming bot subscription
        selected_bot = query.data.replace("confirm_bot_", "")
        user_name = query.from_user.username
        bot_name = selected_bot.capitalize()
        current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        validity_date = datetime.datetime.now() + datetime.timedelta(days=30)
        validity_formatted = validity_date.strftime("%B %d, %Y")
    
        confirmation_message = f"Subscription Confirmed for {selected_bot.capitalize()}!\n\n"
        confirmation_message += f"Please send a payment screenshot for confirmation to the admins."
    
        admin_confirmation_message = (
            f"Subscription Confirmed:\n\n"
            f"User: {user_name}\n"
            f"Bot: {bot_name}\n"
            f"Date: {current_date_time}\n"
            f"Validity: {validity_formatted}\n\n"
            f"Please verify and handle the payment."
        )
    
        # Notify admins
        for admin_id in ADMINS:
            await client.send_message(admin_id, admin_confirmation_message)
    
        # Notify user about successful subscription
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=confirmation_message
        )
        # Wait for user to send a screenshot
        await handle_payment_screenshot(client, message, bot_name)

    
    elif query.data.startswith("description_"):
        selected_bot_type = query.data.replace("description_", "")
        description_text = ""

        if selected_bot_type == "mbot":
            description_text = script.MOVIES_TEXT.format(user=query.from_user.mention)
        elif selected_bot_type == "abot":
            description_text = script.ANIME_TEXT.format(user=query.from_user.mention)
        elif selected_bot_type == "rbot":
            description_text = script.RENAME_TEXT.format(user=query.from_user.mention)
        elif selected_bot_type == "yibot":
            description_text = script.YT_TEXT.format(user=query.from_user.mention)

        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=description_text,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    elif query.data == "mdb" or query.data == "adb" or query.data == "tvsdb":
        # Display monthly plan message for selected bot
        validity_date = datetime.datetime.now() + datetime.timedelta(days=30)
        validity_formatted = validity_date.strftime("%B %d, %Y")

        buttons = [
            [
                InlineKeyboardButton('Confirmed', callback_data=f'confirm_db_{query.data}'),
                InlineKeyboardButton('Description', callback_data=f'description_db_{query.data}')
            ],
            [
                InlineKeyboardButton('Back', callback_data='bots')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        message_text = f"🍿 **{query.data.capitalize()} Premium Database** 🍿\n\n"
        message_text += f"This plan is valid until {validity_date}.\n\n"
        message_text += "Make Payments And Then Select **Confirmed** Button:"
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=message_text,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    elif query.data.startswith("confirm_db_"):
        # Handle user confirming bot subscription
        selected_db = query.data.replace("confirm_db_", "")
        user_name = query.from_user.username
        db_name = selected_db.capitalize()
        current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        validity_date = datetime.datetime.now() + datetime.timedelta(days=30)
        validity_formatted = validity_date.strftime("%B %d, %Y")
    
        confirmation_message = f"Subscription Confirmed for {selected_db.capitalize()}!\n\n"
        confirmation_message += f"Please send a payment screenshot for confirmation to the admins."
    
        admin_confirmation_message = (
            f"Subscription Confirmed:\n\n"
            f"User: {user_name}\n"
            f"Database: {db_name}\n"
            f"Date: {current_date_time}\n"
            f"Validity: {validity_formatted}\n\n"
            f"Please verify and handle the payment."
        )
    
        # Notify admins
        for admin_id in ADMINS:
            await client.send_message(admin_id, admin_confirmation_message)
    
        # Notify user about successful subscription
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=confirmation_message
        )
    
    elif query.data.startswith("description_db_"):
        selected_bot_type = query.data.replace("description_", "")
        description_text = ""

        if selected_bot_type == "mdb":
            description_text = script.MOVIESDB_TEXT.format(user=query.from_user.mention)
        elif selected_bot_type == "adb":
            description_text = script.ANIMEDB_TEXT.format(user=query.from_user.mention)
        elif selected_bot_type == "tvsdb":
            description_text = script.SERIESDB_TEXT.format(user=query.from_user.mention)
        
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=description_text,
            parse_mode=enums.ParseMode.MARKDOWN
        )

