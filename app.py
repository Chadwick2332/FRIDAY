import openai
import json
import os
import datetime

from personalities.friday import Friday
from personalities.arcane import Arcane
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
    
    # Select personality (for now we will just use Friday)
    friday = Friday()
    
    # try:
    #     location = friday.get_location()
    # except:
    #     print("Failed to get location. Please check your internet.")
    #     print("Setting default location to {}".format(DEFAULT_LOCATION))
    #     location = DEFAULT_LOCATION
    
    # location = DEFAULT_LOCATION
    
    # friday.description += "Time: {}, Location: {}".format(friday.get_local_time(), location)

    # Check if the OPENAI_API_KEY environment variable is set
    if os.getenv("OPENAI_API_KEY") is None:
        print("OPENAI_API_KEY environment variable not found. Please set it to your OpenAI API key.")
        exit(1)

    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Setup voice
    voice = Voice(friday.get_voice_id())
    
    voice.start()
    
    system_role = friday.get_system_full_prompt()


    # Initialize the chat conversation
    messages = [{"role": "system", "content": system_role}]

    # HANDLE LOGS
    # chats will be saved to a JSON file under logs folder with the format: logs/<date>-<time>.json
    # the logs folder will be created if it doesn't exist
    
    # Check if the logs folder exists
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    logs = os.listdir('logs')
    
    if len(logs) > 0:
        last_log = logs[-1]
        last_log_time = datetime.datetime.strptime(last_log.split('.')[0], '%Y-%m-%d-%H-%M-%S')
        time_difference = datetime.datetime.now() - last_log_time
        
        if time_difference.seconds < 300:
            print("Do you want to continue the conversation from the last chat log?")
            print("Type 'yes' to continue or 'no' to start a new conversation.")
            user_input = input("User: ")
            
            if user_input == 'yes' or user_input == 'y':
                with open('logs/' + last_log, 'r') as f:
                    messages = json.load(f)
            
    # MAIN LOOP
    try:
        while True:
            question = prompt()
            answer, messages = friday.get_answer(question, messages)

            messages.append({"role": "assistant", "content": answer})

            print("\nSystem: " + answer + "\n")

            # Add the answer to the Voice queue
            voice.add_text(answer)

    except KeyboardInterrupt:
        # On Keyboard Interrupt exit, save the messages to a JSON file
        with open('logs/' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.json', 'w') as f:
            json.dump(messages, f, indent=4)
        
        print("\nConversation saved to logs/" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + ".json")
        exit(0)


if __name__ == "__main__":
    main()
