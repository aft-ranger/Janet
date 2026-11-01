from unicodedata import name

from tools.gettool import get_tool
from tools.hello import hello
from tools.calculator import calculate
from tools.filesystem import list_files
from tools.terminal import order
from tools.goodbye import goodbye
from tools.tooldescription import tool_description
from tools.notifier import manage_notifier
from tools.sticky import manage_sticky
from tools.organizer import manage_organizer

'''def tool_registry():
    return {
        "calculate" : {
            "function": calculate,
            "description": "Perform a calculation",
            "parameters": {
                "type": "object",
                "properties": {
                "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        },
        "hello" : {
            "function": hello,
            "description": "Greet the user",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        "list files" : {
            "function": list_files,
            "description": "List files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path of the directory to list files from"
                    }
                },
                "required": [""]
            }
        },
        "run command" : {
            "function": order,
            "description": "Run a terminal command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The terminal command to execute"
                    }
                },
                "required": ["command"]
            }
        },
        "exit" : {
            "function": goodbye,
            "description": "Exit the program",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        "get tool" : {
            "function": get_tool,
            "description": "Get the description of a specific tool",
            "parameters": {
                "type": "object",
                "properties": {
                    "Tool": {
                        "type": "string",
                        "description": "The name of the tool to get the description for"
                    }
                },
                "required": ["Tool"]
            }
        },
        "get tools description" : {
            "function": tool_description,
            "description": "Get the descriptions of all available tools",
            "parameters": {
                "type": "object",
                "properties": {
                    "Tool": {
                        "type": "string",
                        "description": "The name of the tool to get the description for"
                    }
                },
                "required": ["Tool"]
            }
        }
    }'''

    
class tool_registry:
    def __init__(self):
        self._tools = {}

    def register_tool(self, name, function, description, parameters):
            self._tools[name] = {
                "function": function,
                "description": description,
                "parameters": parameters
            }
    def call_tool(self, function):
        return self._tools.get(function, {}).get("function")

    def check_tool(self, name):
        return name in self._tools
        
    def get_all_descriptions(self):
        return {name: info["description"] for name, info in self._tools.items()}
                    

registry = tool_registry()

registry.register_tool(
    name="calculate",
    function=calculate,
    description="Perform a calculation",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression to evaluate"
            }
        },
        "required": ["expression"]
    }
)

registry.register_tool(
    name="hello",
    function=hello,
    description="Greet the user",
    parameters={
        "type": "object",
        "properties": {},
        "required": []
    }
)

registry.register_tool(
    name="list files",
    function=list_files,
    description="List files in a directory",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The path of the directory to list files from"
            }
        },
        "required": ["path"]
    }
)   

registry.register_tool(
    name="run command",
    function=order,
    description="Run a terminal command",
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The command to run"
            }
        },
        "required": ["command"]
    }
)   

registry.register_tool(
    name="exit",
    function=goodbye,
    description="Exit the program",
    parameters={
        "type": "object",
        "properties": {},
        "required": []
    }
)

registry.register_tool(
    name="get tool",
    function=get_tool,
    description="Get the description of a specific tool",
    parameters={
        "type": "object",
        "properties": {
            "Tool": {
                "type": "string",
                "description": "The name of the tool to get the description for"
            }
        },
        "required": ["Tool"]
    }
)

registry.register_tool(
    name="get tools description",
    function=tool_description,
    description="Get the descriptions of all available tools",
    parameters={
        "type": "object",
        "properties": {
            "Tool": {
                "type": "string",
                "description": "The name of the tool to get the description for"
            }
        },
        "required": []
    }
)

registry.register_tool(
    name="notifier",
    function=manage_notifier,
    description="Control the Auto Notifier background service (start, stop, status, test, list, add <message>, delete <number|message>, clear, interval <hours>)",
    parameters={
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "The action to perform: start, stop, status, test, list, add <message>, delete <number|message>, clear, or interval <hours>"
            }
        },
        "required": ["action"]
    }
)

registry.register_tool(
    name="sticky notes",
    function=manage_sticky,
    description="Open or manage Sticky Notes (open, read, add <text>, clear)",
    parameters={
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Optional action: open, read, add <text>, or clear"
            }
        },
        "required": []
    }
)

registry.register_tool(
    name="auto sort",
    function=manage_organizer,
    description="Sort files in Downloads (default) or a custom directory (start [path], stop, status, once [path], or <path>)",
    parameters={
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "The action or directory path: start [path], stop, status, once [path], or <path>"
            }
        },
        "required": ["action"]
    }
)
def register():
    tool_registry_instance = registry
    return tool_registry_instance
    
    