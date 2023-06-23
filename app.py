import openai
import json
import os
import datetime

from personalities.eliza import Eliza
from personalities.arcane import Arcane

from memory.chat_utils import ask_with_memory
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


    # Initialize the chat conversation
    messages = [{"role": "system", "content": system_role}]
            
    # MAIN LOOP
    try:
        while True:
            question = prompt()
            answer = ask_with_memory(question, messages)

            messages.append({"role": "assistant", "content": answer})

            print("\nSystem: " + answer + "\n")

            # Add the answer to the Voice queue
            voice.add_text(answer)

    except KeyboardInterrupt:
        # On Keyboard Interrupt exit, save the messages to a text file
        log_conversation(messages, 'logs/', 'txt')
        
        print("\nConversation saved to {} folder.".format('logs/'))


if __name__ == "__main__":
    main()
