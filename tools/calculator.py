import ast

ALLOWED_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Constant,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.UAdd,
    ast.USub,
)


def _validate_ast(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED_NODES):
            raise ValueError(f"Unsafe or unsupported syntax: {type(node).__name__}")
        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
            raise ValueError("Only numeric values (int/float) are allowed.")


def calculate(equation=""):
    if equation == "":
        equation = input("Janet: Please enter the equation: ").strip()
    try:
        equation = str(equation)
        equation = equation.strip()

        if not equation:
                    print("Janet: No equation provided.")
                    return
        
        cleanEquation = equation.replace(" ", "")
        #parse = list(cleanEquation)

        tree = ast.parse(cleanEquation, mode='eval')
        _validate_ast(tree)
        result = eval(compile(tree, filename="<ast>", mode="eval"), {"__builtins__": {}})

        '''x = float(num1)
        y = float(num2)

        if operator == "+":
            result = x + y
        elif operator == "-":
            result = x - y
        elif operator == "*":
            result = x * y
        elif operator == "/":
            if y == 0:
                print("Janet: Error! Division by zero.")
                return
            result = x / y
        elif operator == "%":
            result = x%y
        else:
            print(
                f"Janet: Unsupported operator '{operator}'. Please use +, -, *, / or %."
            )
            return'''

    except ZeroDivisionError:
        print("Janet: Error! Division by zero.")
        return
    except (ValueError, SyntaxError):
        print("Janet: Invalid or unsafe expression. Only mathematical calculations are allowed.")
        return

    return result


# multi expression calculator

