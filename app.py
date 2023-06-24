import openai
import json
import os
import datetime

from personalities.eliza import Eliza
from personalities.arcane import Arcane

from memory.chat_utils import ask_with_memory, preprend_time_to_str
from memory.database_utils import upsert_file
from log import log_conversation
from voice import Voice

with open('.env', 'r') as f:
    for line in f.readlines():
        if line.strip():
            key, value = line.strip().split("=", 1)
            os.environ[key] = value

DEFAULT_LOCATION = "Warrenton, VA"


def prompt():
    """For now we will just directly take the user's input using the input() function. This will eventually be replaced with a transcription
    module that will take the user's speech as input and convert it to text."""

    question = input("User: ")
    return question

def print_with_color(text, color):
    """This function will print the given text in the given color. This will be used to print the system's response in a different color."""
    # ANSI escape sequences for different colors
    color_codes = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
    }

    # Reset ANSI escape sequence
    reset_code = '\033[0m'

    print(color_codes[color] + text + reset_code)

def main():
    """This will display the chat between the user and the system. The user will be prompted to ask a question and the system will respond.
    It will also read answer using the text to speech module."""
    
    # Select personality (for now we will just use Eliza)
    eliza = Eliza()
    
    # try:
    #     location = eliza.get_location()
    # except:
    #     print("Failed to get location. Please check your internet.")
    #     print("Setting default location to {}".format(DEFAULT_LOCATION))
    #     location = DEFAULT_LOCATION
    
    # location = DEFAULT_LOCATION
    
    # eliza.description += "Time: {}, Location: {}".format(eliza.get_local_time(), location)

    # Check if the OPENAI_API_KEY environment variable is set
    if os.getenv("OPENAI_API_KEY") is None:
        print("OPENAI_API_KEY environment variable not found. Please set it to your OpenAI API key.")
        exit(1)

    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Setup voice
    voice = Voice(eliza.get_voice_id())
    
    voice.start()
    
    # Load the systems personality and get 
    system_role = eliza.get_system_full_prompt()
    
    print_with_color("\nPERSONALITY: " + eliza.get_system_name() + '\n', 'green')
    print_with_color(system_role + '\n', 'green')

    # Initialize the chat conversation
    messages = [{"role": "system", "content": system_role}]
    message_logs = []
            
    # MAIN LOOP
    try:
        while True:
            question = prompt()
            question = preprend_time_to_str(question)
            
            #Store the question in the message logs
            message_logs.append({"role": "user", "content": question})
            
            answer = ask_with_memory(question, messages)

            message_logs.append({"role": "assistant", "content": answer})
            messages.append({"role": "assistant", "content": answer})

            print_with_color("\nAssistant: " + answer + '\n', 'cyan')

            # Add the answer to the Voice queue
            voice.add_text(answer)

    except KeyboardInterrupt:
        # On Keyboard Interrupt exit, save the messages to a text file
        filename = log_conversation(message_logs, 'logs/', 'txt')
        
        # Prompt the user to save the conversation to the database
        if input("Would you like to save this conversation to the database? (y/n): ").lower() == 'y':
            try:
                upsert_file('logs/' + filename)
            except:
                print("Failed to save conversation to database.")
            
            print("\nConversation saved to {} folder.".format('logs/'))


if __name__ == "__main__":
    main()
