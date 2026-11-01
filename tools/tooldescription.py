



def tool_description(tool=""):
    if tool == "":
        tool = input("Janet: Please enter a tool name: ").strip()
    from tools.registry import register
    """
    Returns a dictionary of all registered tools with their descriptions and parameters.
    """
    commands = register()
    return commands.get_all_descriptions()