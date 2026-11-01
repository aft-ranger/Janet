





def get_tool(Tool=""): 
    if Tool == "":
        Tool = input("Janet: Please enter a tool name: ").strip()
    from tools.registry import register
    """
    Returns the description of a specific tool.
    """
    registry = register()
    tool_descriptions = {}

    if registry.check_tool(Tool) is True:
        tool_info = registry._tools.get(Tool)
        tool_descriptions[Tool] = {
            "description": tool_info.get("description", ""),
            "parameters": tool_info.get("parameters", {}).get("properties", {})
        }
    else:
        print(f"Tool '{Tool}' not found in the registry.")
    
    return tool_descriptions