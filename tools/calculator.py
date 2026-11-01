

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
        parse = list(cleanEquation)

        if len(parse) < 3:
            print(
                "Janet: Invalid equation format. Please try again"
            )
            return

        i = 0
        while i < len(parse):
            char = parse[i]
            
            if char.isdigit() or char == ".":
                i += 1
                continue
            
            if char == "-" and i == 0:
                i += 1
                continue
            
            break
        else:
            print("No operator found")
            return   

        num1 = "".join(parse[0:i])
        operator = parse[i]
        num2 = "".join(parse[i+1:])

        x = float(num1)
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
                f"Janet: Unsupported operator '{operator}'. Please use +, -, *, or /."
            )
            return

    except ValueError:
        print("Janet: Invalid input. Please enter numerical values.")
        return

    return result


