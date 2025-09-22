
import telegram
import json
import os
import time

def send_question(bot, chat_id, question_data):
    """Sends a single question as a poll and its explanation."""
    try:
        topic = question_data.get("topic", "General Knowledge")
        question_id = question_data.get("id", "N/A")
        question_text = f"{question_id}. {question_data['question']}"
        options = list(question_data["options"].values())
        answer = question_data["answer"].lower()
        explanation = question_data["explanation"]
        
        # Telegram polls need at least 2 and at most 10 options.
        if not (2 <= len(options) <= 10):
            print(f"Skipping question ID {question_data.get('id')} due to invalid number of options.")
            return

        # The correct option index is 0-based (a=0, b=1, c=2, ...).
        correct_option_id = ord(answer) - ord('a')

        bot.send_message(chat_id=chat_id, text=f"*Topic: {topic}*", parse_mode='Markdown')
        
        poll_message = bot.send_poll(
            chat_id=chat_id,
            question=question_text,
            options=options,
            is_anonymous=False,
            type='quiz',
            correct_option_id=correct_option_id
        )
        
        # Pause briefly before sending the explanation
        time.sleep(20) 

        bot.send_message(
            chat_id=chat_id,
            text=f"""*Explanation:*
{explanation}""",
            parse_mode='Markdown'
        )
        print(f"Successfully sent question ID {question_data.get('id')} to chat ID {chat_id}.")

    except Exception as e:
        print(f"Error sending question ID {question_data.get('id')} to chat ID {chat_id}: {e}")

def main():
    """Main function to run the bot."""
    try:
        token = os.environ['TELEGRAM_TOKEN']
        chat_ids_str = os.environ['TELEGRAM_CHAT_IDS']
        chat_ids = [int(chat_id.strip()) for chat_id in chat_ids_str.split(',')]
    except KeyError:
        print("Error: Please set the TELEGRAM_TOKEN and TELEGRAM_CHAT_IDS environment variables.")
        return

    bot = telegram.Bot(token=token)
    
    # Send a welcome message
    for chat_id in chat_ids:
        bot.send_message(chat_id=chat_id, text="Hello! I am a geography quiz bot. I will send you 10 questions every day. I hope you enjoy it!")

    
    # Load questions from JSON file
    try:
        with open('questions.json', 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading questions.json: {e}")
        return

    # Manage progress
    progress_file = 'progress.txt'
    try:
        with open(progress_file, 'r') as f:
            start_index = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        start_index = 0

    if start_index >= len(questions):
        message = "All questions have been sent. We are done!"
        for chat_id in chat_ids:
            bot.send_message(chat_id=chat_id, text=message)
        print(message)
        return

    end_index = min(start_index + 10, len(questions))
    questions_to_send = questions[start_index:end_index]

    for chat_id in chat_ids:
        for question_data in questions_to_send:
            send_question(bot, chat_id, question_data)
            time.sleep(10)  # Delay between questions

    # Update progress for the next run
    with open(progress_file, 'w') as f:
        f.write(str(end_index))
    
    print(f"Sent questions from index {start_index} to {end_index - 1}.")

if __name__ == "__main__":
    main()
