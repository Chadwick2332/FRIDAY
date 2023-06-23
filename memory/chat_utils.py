from typing import Any, List, Dict
import openai
import requests
import os
import json
import logging

with open('.env', 'r') as f:
    for line in f.readlines():
        if line.strip():
            key, value = line.strip().split("=", 1)
            os.environ[key] = value


def query_database(query_prompt: str) -> Dict[str, Any]:
    """
    Query vector database to retrieve chunk with user's input questions.
    """
    url = "http://localhost:8000/query"
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
        "Authorization": "Bearer {}".format(os.getenv("DATABASE_INTERFACE_BEARER_TOKEN")),
    }
    data = {"queries": [{"query": query_prompt, "top_k": 3}]}

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        result = response.json()
        # process the result
        return result
    else:
        raise ValueError(f"Error: {response.status_code} : {response.content}")


def apply_prompt_template(question: str) -> str:
    """
        A helper function that applies additional template on user's question.
        Prompt engineering could be done here to improve the result. Here I will just use a minimal example.
    """
    prompt = f"""
        Use the information from the 'memory' above to answer the question: {question}
    """
    return prompt


def call_chatgpt_api(user_question: str, chunks: List[str]) -> Dict[str, Any]:
    """
    Call chatgpt api with user's question and retrieved chunks.
    """
    # Send a request to the GPT-3 API
    messages = list(
        map(lambda chunk: {
            "role": "user",
            "content": "(memory)" + chunk
        }, chunks))
    question = apply_prompt_template(user_question)
    messages.append({"role": "user", "content": question})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1024,
        temperature=0.7,  # High temperature leads to a more creative response.
    )
    return response


def ask(user_question: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Ask a question and get a response from the GPT-3.5-turbo API.
    """
    
    # Add user question to messages
    question = user_question
    messages.append({"role": "user", "content": question})

    # Call the GPT-3.5-turbo API with the modified messages
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=messages,
        max_tokens=1024,
        temperature=0.7,
    )

    # Extract the GPT-3.5-turbo response
    return response["choices"][0]["message"]["content"]


def ask_with_memory(user_question: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Get chunks from database.
    chunks_response = query_database(user_question)
    chunks = []
    for result in chunks_response["results"]:
        for inner_result in result["results"]:
            chunks.append(inner_result["text"])

    # Add retrieved chunks to messages
    unique_chunks = set(chunks)
    chunks_messages = [{"role": "system", "content": "(MEMORY)" + chunk} for chunk in unique_chunks]
    messages.extend(chunks_messages)

    # Add user question to messages
    question = user_question
    messages.append({"role": "user", "content": question})

    # Call the GPT-3.5-turbo API with the modified messages
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=messages,
        max_tokens=1024,
        temperature=0.7,
    )

    # Extract the GPT-3.5-turbo response
    return response["choices"][0]["message"]["content"]