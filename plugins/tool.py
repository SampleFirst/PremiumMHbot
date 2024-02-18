from pyrogram import Client, filters
import requests
from bs4 import BeautifulSoup

# Function to extract text and links from a website
async def extract_text_links(website_url):
    try:
        # Make a GET request to the website
        response = requests.get(website_url, timeout=10)  # Set a timeout to prevent hanging requests
        response.raise_for_status()  # Raise an exception if request fails

        # Extract text and links using Beautiful Soup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get all text content that is not within script or style tags
        text = soup.get_text(strip=True, separator=' ')
        text = " ".join(text.split('\n'))  # Join lines with spaces to improve readability

        # Find all anchor tags (links)
        links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href.startswith('http'):  # Filter valid links
                links.append(href)

        # Combine extracted text and links, ensuring links open in Telegram
        combined_text = text + "\n\n".join(f"* [{link}]({link})" for link in links)

        return combined_text

    except Exception as e:
        # Handle errors gracefully and send an informative message to the user
        print(f"Error extracting content from {website_url}: {e}")
        return f"An error occurred while processing the website. Please try again later."

# Filter for messages starting with a slash followed by any word (command-like format)
@Client.on_message(filters.command(["extract"]))
async def handle_extarct_command(client, message):
    try:
        command, website_url = message.text.split(' ', 1)
    except ValueError:
        await message.reply_text("Please provide a website URL to extract text and links.")
        return

    if command.lower() == "/extract":
        # Check if a website URL is provided
        if not website_url:
            await message.reply_text("Please provide a website URL to extract text and links.")
            return

        # Validate website URL format
        if not website_url.startswith("http"):
            website_url = f"https://{website_url}"  # Add missing protocol if necessary

        # Extract text and links concurrently to improve performance
        try:
            extracted_text = await extract_text_links(website_url)
            await message.reply_text(extracted_text, disable_web_page_preview=True)  # Prevent automatic link preview
        except Exception as e:
            await message.reply_text(f"An error occurred: {e}")
