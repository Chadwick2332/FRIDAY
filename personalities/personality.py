import openai
import json

class Personality:
    def __init__(self):
        self.voice_id = ""
        self.system_name = ""
        self.description = """"""
        
        self.systemPrompt = "You are an actor pretending to be a character named {}." \
            "Above is your template for the character that you are playing. When you " \
            "see a response that starts with '(MEMORY)', this is information from your " \
            "memory, that may or may not be useful. You can use this information to " \
            "help you respond to the user. Do not repeat the information verbatim, " \
            "but paraphrase it and only include relevant information."
            
        
        self.functionCalls = []
        
        openai.api_key = "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"

    
    def get_voice_id(self):
        """Returns the voice id of the personality."""
        return self.voice_id
    
    def get_system_name(self):
        """Returns the system name of the personality."""
        return self.system_name
    
    def get_description(self):
        """Returns the description of the personality."""
        return self.description
    
    def get_system_full_prompt(self):
        """Returns the full system prompt of the personality."""
        return self.systemPrompt.format(self.system_name) + "\n\n" + self.description
    
    def get_function_calls(self):
        """Returns the function calls of the personality."""
        return self.functionCalls
