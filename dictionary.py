from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


TOKEN: Final = '8164159308:AAG7mV-JfZUKSECJ7lOHC0I7dl3spZuCPqI'
BOT_USERNAME: Final = '@dift_voucherBot'

## COMMANDS
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # await update.message.reply_text("Hello! I am here to help you who much you have spent so you can "
    #                                 f"get or to know the nolege for how to get a voucher.")
    await update.message.reply_text("Hello! I am Voucher Bot and I am at your service.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am a Voucher Bot. Please type what is your problem. So I can help you.")


## RESPONSES
def handle_responses(text: str):
    processed: str = text.lower()

    if 'hello' in processed:
        return "Hello there!"

    if 'i have a problem' in processed:
        return "Hello! Sorry that you have a prble. How can I help you?"

    return "I do not understand what you wrote..."

## HELP RESPONSES
def help_responses(text: str):
    processd: str = text.capitalize()

    help1 = "How much for to win the voucher?"
    help2 = "Can you help me to find how much did I spent?"
    help3 = "How long does voucher last? After winning "

    if help1 in processd:
        return "You need to spent 1000 or more to able to win the voucher"

    if help2 in processd:
        return "No problem.That's a job."

    if help3 in processd:
        return "I don't have an answer to that question."
    
    return "I do not understand what you wrote..."



async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    massage_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {massage_type}: "{text}"')

    if massage_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_responses(new_text)
        else:
            return
    else:
        response: str = handle_responses(text)

    print('Bot:', response)
    await update.message.reply_text(response)

async def errors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    print('Start bot...')
    app = Application.builder().token(TOKEN).build()

    ## COMMANDS
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    ## MESSAGES
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    ## ERRORS
    app.add_error_handler(errors)

    ## CHECK FOR UPDATES FOR MESSAGES
    print('Poling...')
    app.run_polling(poll_interval=5)
