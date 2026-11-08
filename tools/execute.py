from tools.parser import parse_command
from tools.parser import task
from tools.registry import register

ai_register = register()

def execute(task_dict: task):
    if not task_dict:
        print("Janet: No command provided.")
        return
    for command, argument in task_dict.items():
        if not argument:
            argument = None
        run_function = ai_register.call_tool(command)
        if run_function:
            if argument:
                return run_function(argument)
            else:
                return run_function()
        else:
            print(f"Janet: Command '{command}' not recognized.")

if __name__ == "__main__":
    while True:
        execute_task_class = parse_command()     
        execute(execute_task_class)