def tool_description():
    from tools.registry import register
    """
    Returns a dictionary of all registered tools with their descriptions and parameters.
    """
    commands = register()
    return commands.get_all_descriptions()