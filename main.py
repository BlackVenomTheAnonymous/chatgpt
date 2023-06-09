import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai

# Set up OpenAI API credentials
openai.api_key = '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'

# Define your Telegram bot token
TELEGRAM_TOKEN = '5931752370:AAG3Kc4MORSTDZp90sLYvFhbHfG-PoP7dyQ'

# Create a dictionary to store conversation history
conversation_history = {}

# Create the ChatGPT completion function
def generate_completion(prompt):
    response = openai.Completion.create(
        engine='text-davinci-002',
        prompt=prompt,
        max_tokens=200,
        temperature=0.7,
        n=1,
        stop=None,
    )
    return response.choices[0].text.strip()

# Define the message handler
def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_input = update.message.text

    # Get the conversation history for the user
    history = conversation_history.get(user_id, [])

    if len(history) > 0:
        # Append the user's message and the bot's response to the history
        history[-1] += " " + user_input
    else:
        # Start a new conversation with the user's message
        history.append(user_input)

    # Generate a response using ChatGPT
    prompt = "\n".join(history)
    bot_response = generate_completion(prompt)

    # Store the updated conversation history
    history.append(bot_response)
    conversation_history[user_id] = history

    # Split long responses into multiple messages with numbering
    response_chunks = []
    chunk_size = 4096

    while len(bot_response) > chunk_size:
        response_chunks.append(bot_response[:chunk_size])
        bot_response = bot_response[chunk_size:]

    # Add the remaining portion of the response
    response_chunks.append(bot_response)

    # Send the response chunks as separate messages with numbering
    for i, chunk in enumerate(response_chunks):
        message_number = f"{i + 1}/{len(response_chunks)}"
        message = f"{message_number}:\n{chunk}"
        update.message.reply_text(message)

# Define the start command handler
def start_command(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to the ChatGPT bot! Send me a message, and I'll respond.")

# Set up the Telegram bot
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Register the start command handler
    start_handler = CommandHandler("start", start_command)
    dispatcher.add_handler(start_handler)

    # Register the message handler
    message_handler = MessageHandler(Filters.text & ~Filters.command, handle_message)
    dispatcher.add_handler(message_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
