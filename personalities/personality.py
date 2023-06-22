import openai
import json

class Personality:
    def __init__(self):
        self.voice_id = ""
        self.system_name = ""
        self.description = """"""
        
        self.systemPrompt = "You are an actor pretending to be a character named {}." \
            "This is your template for the character that you are playing."
        
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
    def get_answer(self, question, messages):
        """Returns the answer to the question asked by the user."""
        
        messages.append({"role": "user", "content": question})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
            functions=self.functionCalls,
        )

        response_message = response["choices"][0]["message"]

        # Check if AI wants to call a function
        if response_message.get("function_call"):
            function_name = response_message["function_call"]["name"]
            function_args = json.loads(
                response_message["function_call"]["arguments"])

            # only one function in this example, but you can have multiple
            available_functions = {
                "get_weather": self.get_weather,
                "get_local_time": self.get_local_time
            }
            function_to_call = available_functions[function_name]

            # Call the function
            function_response = function_to_call(**function_args)

            # Continue conversation with function response
            messages.append(response_message)
            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            )

            second_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k-0613",
                messages=messages,
            )
            return second_response["choices"][0]["message"]["content"], messages

        return response_message["content"], messages
