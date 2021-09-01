from typing import Union, Callable

ValidNumbers = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', 'e')
ValidOperators = ('^', '√', '%', '*', '/', '+', '-')
Parenthesis = ('(', ')')
ValidChars = ValidNumbers + ValidOperators + Parenthesis


class Calculator:

    def __init__(self):
        self._expression: list[str] = list()  # List of characters

    @staticmethod
    def _add(first: float, second: float) -> float:
        return first + second

    @staticmethod
    def _subtract(first: float, second: float) -> float:
        return first - second

    @staticmethod
    def _multiply(first: float, second: float) -> float:
        return first * second

    @staticmethod
    def _divide(first: float, second: float) -> float:
        if second == 0:
            raise ZeroDivisionError("Division by zero!")

        return first / second

    @staticmethod
    def _power(num: float, power: float) -> float:
        if num < 0 and not power.is_integer():
            raise ValueError(
                "Negative number to the power of non-integer number!")

        return num ** power

    @staticmethod
    def _sqrt(root: float, num: float) -> float:
        if num < 0 and (not root.is_integer() or int(root) % 2 == 0):
            raise ValueError("Invalid root for negative argument!")

        if root == 0:
            raise ValueError("Root can't be 0!")

        ans = num ** (1 / root)
        if type(ans) is not complex:
            return ans
        ans = -((-num) ** (1 / root))
        if type(ans) is not complex:
            return ans
        raise ValueError("Complex number!")

    @staticmethod
    def _mod(first: float, second: float) -> float:
        return first % second

    def _find_parenthesis(self, location: tuple[int, int]) -> Union[tuple[int, int], None]:
        focused_expression = self._expression[location[0]:location[1] + 1]
        if Parenthesis[0] not in focused_expression:
            return None

        end = start = focused_expression.index(Parenthesis[0])
        parenthesis_equality = 0
        while True:
            if focused_expression[end] == Parenthesis[0]:
                parenthesis_equality += 1
            elif focused_expression[end] == Parenthesis[1]:
                parenthesis_equality -= 1

            if parenthesis_equality == 0:
                break

            end += 1
            if end >= len(focused_expression):
                raise ValueError("No closing parenthesis found!")

        start += location[0]
        end += location[0]
        return start, end

    def _find_previous_number_index(self, index: int, location: tuple[int, int]) -> int:
        for i in range(index - 1, location[0] - 1, -1):
            temp_char = self._expression[i]
            if temp_char in ValidNumbers:
                continue
            elif temp_char in Parenthesis:
                return i + 1
            elif temp_char in ValidOperators:
                if temp_char != '-' and temp_char != '+':
                    return i + 1
                else:
                    if i == location[0]:
                        return i
                    elif self._expression[i - 1] == 'e':
                        continue
                    elif self._expression[i - 1] in ValidOperators or self._expression[i - 1] in Parenthesis:
                        return i
                    elif self._expression[i - 1] in ValidNumbers:
                        return i + 1
                    else:
                        raise ValueError(
                            "Something went wrong in finding operator's previous number!")
            else:
                raise ValueError(
                    "Something went wrong in finding operator's previous number!")

        else:
            return location[0]

    def _find_next_number_index(self, index: int, location: tuple[int, int]) -> int:
        has_met_number = False
        has_met_e = False
        for i in range(index + 1, location[1] + 1):
            temp_char = self._expression[i]
            if temp_char == 'e':
                has_met_e = True
            if temp_char in ValidNumbers:
                has_met_number = True
                continue
            if has_met_e and (temp_char == '+' or temp_char == '-'):
                has_met_e = False
                continue
            elif has_met_number and temp_char in ValidOperators + Parenthesis:
                return i - 1
            elif not has_met_number and temp_char == '-':
                continue
            else:
                raise ValueError(
                    "Something went wrong in finding operator's next number!")

        else:
            return location[1]

    def _replace_calculated(self, location: tuple[int, int], calculated_expression: str) -> None:
        new_expression = self._expression[:location[0]] + list(calculated_expression) + self._expression[
            location[1] + 1:]
        self._expression = new_expression

    @staticmethod
    def _convert_to_float(num: str):
        if num == "":
            return 0.0
        return float(num)

    def _calculate_and_replace(self, index: int, location: tuple[int, int],
                               function: Callable[[float, float], float]) -> None:
        first_index = self._find_previous_number_index(index, location)
        last_index = self._find_next_number_index(index, location)
        first_num = Calculator._convert_to_float(
            "".join(self._expression[first_index:index]))
        second_num = Calculator._convert_to_float(
            "".join(self._expression[index + 1:last_index + 1]))
        self._replace_calculated((first_index, last_index), str(
            function(first_num, second_num)))

    def _solve_first_order_operators(self, location: tuple[int, int]) -> None:
        negative_end = location[1] - len(self._expression)
        while True:
            positive_end = negative_end + len(self._expression)
            i = location[0]
            while i <= positive_end:
                temp_char = self._expression[i]
                if temp_char == '^':
                    self._calculate_and_replace(
                        i, (location[0], positive_end), Calculator._power)
                    break
                elif temp_char == '√':
                    self._calculate_and_replace(
                        i, (location[0], positive_end), Calculator._sqrt)
                    break

                i += 1
            else:
                return

    def _solve_second_order_operators(self, location: tuple[int, int]) -> None:
        negative_end = location[1] - len(self._expression)
        while True:
            positive_end = negative_end + len(self._expression)
            i = location[0]
            while i <= positive_end:
                temp_char = self._expression[i]
                if temp_char == '*':
                    self._calculate_and_replace(
                        i, (location[0], positive_end), Calculator._multiply)
                    break
                elif temp_char == '/':
                    self._calculate_and_replace(
                        i, (location[0], positive_end), Calculator._divide)
                    break
                elif temp_char == '%':
                    self._calculate_and_replace(
                        i, (location[0], positive_end), Calculator._mod)
                    break

                i += 1
            else:
                return

    def _solve_third_order_operators(self, location: tuple[int, int]) -> None:
        negative_end = location[1] - len(self._expression)
        while True:
            positive_end = negative_end + len(self._expression)
            i = location[0]
            while i <= positive_end:
                temp_char = self._expression[i]
                if temp_char == '+' and i != location[0] and self._expression[i - 1] != 'e':
                    self._calculate_and_replace(
                        i, (location[0], positive_end), Calculator._add)
                    break
                elif temp_char == '-' and i != location[0] and self._expression[i - 1] in ValidNumbers and \
                        self._expression[i - 1] != 'e':
                    self._calculate_and_replace(
                        i, (location[0], positive_end), Calculator._subtract)
                    break

                i += 1
            else:
                return

    def _solve(self, location: tuple[int, int]) -> None:
        negative_end = location[1] - len(self._expression)
        while True:
            positive_end = negative_end + len(self._expression)
            new_location = self._find_parenthesis((location[0], positive_end))
            if new_location is None:
                break

            negative_new_end = new_location[1] - len(self._expression)
            self._solve((new_location[0] + 1, new_location[1] - 1))
            del self._expression[new_location[0]
                                 ], self._expression[negative_new_end]

        self._solve_first_order_operators(
            (location[0], negative_end + len(self._expression)))  # ^, √
        self._solve_second_order_operators(
            (location[0], negative_end + len(self._expression)))  # %, *, /
        self._solve_third_order_operators(
            (location[0], negative_end + len(self._expression)))  # +, -

    @staticmethod
    def _check_validation(expression: str) -> str:
        expression = expression.rstrip("".join(ValidOperators + (' ',)))
        if expression.count(Parenthesis[0]) < expression.count(Parenthesis[1]):
            raise ValueError("Closing parenthesis more than opening ones!")
        expression += Parenthesis[1] * (expression.count(
            Parenthesis[0]) - expression.count(Parenthesis[1]))

        return expression

    def calculate(self, expression: str) -> tuple[float, str]:
        valid_expression = Calculator._check_validation(expression)
        self._expression = list(
            filter(lambda char: char != ' ', valid_expression))
        self._solve((0, len(self._expression) - 1))
        answer = Calculator._convert_to_float("".join(self._expression))
        return answer, f"{valid_expression} ="
