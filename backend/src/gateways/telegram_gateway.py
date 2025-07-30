import asyncio
from telethon import TelegramClient, events
import os

# TODO: Move these to a proper config management system
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")

client = TelegramClient('telegram_session', int(API_ID), API_HASH)

async def send_doc_and_get_reports(path: str) -> tuple[bytes, bytes]:
    """
    Handles the conversation with the Turnitin Telegram bot to get similarity and AI reports.

    Args:
        path: The local file path of the document to be checked.

    Returns:
        A tuple containing the bytes of the similarity PDF and the AI PDF.
    """
    async with client:
        async with client.conversation(BOT_USERNAME, timeout=720) as conv:
            try:
                await conv.send_message('/start')
                # Wait for the initial response and click the 'YES' button
                response = await conv.get_response()
                await response.click(data=b'YES')

                # Wait for the next response and click the 'NO' button
                response = await conv.get_response()
                await response.click(data=b'NO')

                # Send the document file
                await conv.send_file(path)

                # Wait for the "processing" message
                await conv.wait_event(
                    events.NewMessage(pattern='.*processing.*'),
                    timeout=120
                )

                # Get the similarity report
                sim_response = await conv.get_response(timeout=600)
                if not sim_response.document:
                    raise Exception("Failed to receive similarity report document.")
                sim_pdf = await sim_response.download_media(bytes)


                # Get the AI report
                ai_response = await conv.get_response(timeout=600)
                if not ai_response.document:
                    raise Exception("Failed to receive AI report document.")
                ai_pdf = await ai_response.download_media(bytes)


                return sim_pdf, ai_pdf
            except asyncio.TimeoutError:
                # Handle timeouts
                print(f"Timeout occurred during conversation with bot for file: {path}")
                raise
            except Exception as e:
                # Handle other exceptions
                print(f"An error occurred: {e}")
                raise

if __name__ == '__main__':
    # Example usage:
    # Make sure to have a file named 'sample.docx' in the same directory
    # and your .env file correctly set up.
    async def main():
        # You need to be logged in for this to work.
        # The first time you run this, you'll be prompted for your phone number,
        # password, and 2FA code.
        await client.start()
        print("Client Created")
        sim, ai = await send_doc_and_get_reports('sample.docx')
        with open("similarity_report.pdf", "wb") as f:
            f.write(sim)
        with open("ai_report.pdf", "wb") as f:
            f.write(ai)
        print("Reports downloaded successfully.")

    # To run this example, you would typically use asyncio.run(main())
    # but since this is a library file, we'll leave it commented out.
    # asyncio.run(main())
    pass