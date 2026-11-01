from tools.registry import register
from dataclasses import dataclass

@dataclass
class task:
    command : str
    argument : str = None

    def standardize(self) -> dict:
        self_command = self.command.lower().strip() 
        self_argument = (
        self.argument.lower().strip() if self.argument else None)
        return {self_command:self_argument}
def parse_command(command =""):
    try:
        if command == "":
            command = input("You: ").strip()
    except KeyboardInterrupt:
        print("\nJanet: Program interrupted by user. Exiting gracefully...")
        exit(0)

    commands = register()
    
    i=0
    while i < len(command.split()):
        if commands.check_tool(" ".join(command.split()[0:i])) is True:
            break
        i += 1

    split = command.split(maxsplit=i)
    
    if len(split) == 1:
        task_instance = task(command=split[0])
        return task_instance
    
    else:
        if len(" ".join(split[0:i]).split()) == len(command.split()):
            task_instance = task(command = " ".join(split[0:i]))
            return task_instance
        else:
            task_instance = task(command = " ".join(split[0:i]), argument = split[i])
            return task_instance
     