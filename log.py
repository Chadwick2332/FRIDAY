import os
import json
import time
import datetime

def log_conversation(messages, pathToLogs, type="json"):
    """This function logs the conversation to a JSON file under the logs folder or
    a text file under the given path."""
    title = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    
    if type == "json":
        with open(pathToLogs + title + '.json', 'w') as f:
            json.dump(messages, f, indent=4)
            
    elif type == "txt":
        with open(pathToLogs + title + '.txt', 'w') as f:
            for message in messages:
                # Ignore the system messages
                if message['role'] != 'system':
                    f.write(message['role'].upper()
                            + ": " + message['content'] + "\n")
            return title + '.txt'
    else:
        print("Invalid type. Please choose 'json' or 'txt'.")
        return