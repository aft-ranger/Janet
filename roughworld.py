import ollama
from tools.registry import register
from tools.execute import execute
import json
ai_tools = register().get_ollama_tools()

message = [
    {"role": "system",
     "content": '''"You are a helpful female assistant. You talk with a friendly and supportive tone. Your name is Janet and you refer to me as Sir."'''},
]



while True:
    prompt = input("Enter your prompt: ")
    message.append({"role": "user", "content": prompt})
    response = ollama.chat(model="huihui_ai/qwen2.5-abliterate:7b", messages=message, tools=ai_tools)

    while response.message.tool_calls:
        message.append(response.message)
        
        for call in response.message.tool_calls:
            name = call.function.name
            arguments = call.function.arguments

            argument_list = []
            if arguments:
                key = list(arguments.keys())[0]
                argument_list = arguments[key]
            
            result = execute({name: argument_list})
            
            message.append({
                "role": "tool",
                "name": name,
                "content": str(result),
            })
        response = ollama.chat(model="huihui_ai/qwen2.5-abliterate:7b", messages=message, tools=ai_tools)

    print("Janet:", response.message.content)
    message.append({"role": "assistant", "content": response.message.content})