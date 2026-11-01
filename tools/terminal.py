import subprocess

def order(order=""):
    if order == "":
        order = input("Janet: Please enter the command you want to execute: ")
    try:       
        result = subprocess.run(
            order.split(),
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout

    except FileNotFoundError:
        print("Janet: Command not found. Please check the command name.")

    except subprocess.CalledProcessError as e:
        print("Janet: An error occurred while executing the command:")
        print("Exit Code:", e.returncode)
        print("Error Output:", e.stderr)

    except Exception as e:
        print("Janet: An unexpected error occurred:", e)