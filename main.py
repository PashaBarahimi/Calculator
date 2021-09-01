from tkinter import Tk, Frame, StringVar, Label, Entry, Button, Canvas, PhotoImage, constants, messagebox
from enum import Enum
from calc import Calculator, ValidOperators
import platform

# ==================== DarkMode Variables ===================
IsDark = True
IsChangingMode = False
DisplayState = 14
ColorCodes = ["#F0F0F0", "#E2E2E2", "#D3D3D3", "#C5C5C5", "#B7B7B7", "#A9A9A9", "#9A9A9A", "#8C8C8C", "#7E7E7E",
              "#6F6F6F", "#616161", "#535353", "#454545", "#363636", "#282828"]
SwitchImages = []
Widgets = []

# ========================= Settings =========================
root = Tk()
root.geometry("400x550")
root.minsize(400, 550)
root.title("Calculator")
root.configure(bg=ColorCodes[14])
if platform.system() == "Windows":
    root.iconbitmap("./assets/icon.ico")
Widgets.append(root)

# ========================== Frames ==========================
switch = Frame(root, bg=ColorCodes[14])
switch.place(relwidth=1, relheight=0.08, relx=0, rely=0)
texts = Frame(root, bg=ColorCodes[14])
texts.place(relwidth=1, relheight=0.17, relx=0, rely=0.08)
buttons = Frame(root, bg=ColorCodes[14])
buttons.place(relwidth=1, relheight=0.75, relx=0, rely=0.25)
line = Frame(root, bg=ColorCodes[0])
line.place(relwidth=0.9, relx=0.05, rely=0.25)
Widgets += [switch, texts, buttons]

# ======================= TextVariables =======================
labelStr = StringVar(value="")
textboxStr = StringVar(value="0")

# =========================== Texts ===========================
label = Label(texts, anchor=constants.W, textvariable=labelStr, font=(
    "Cascadia Code", 8), bg=ColorCodes[14], fg=ColorCodes[0])
label.place(relwidth=0.9, relheight=0.25, relx=0.05, rely=0.1)
textbox = Entry(texts, textvariable=textboxStr, font=("Cascadia Mono", 20), state=constants.DISABLED, relief=constants.FLAT,
                disabledbackground=ColorCodes[14], disabledforeground=ColorCodes[0])
textbox.place(relwidth=0.9, relheight=0.35, relx=0.05, rely=0.45)
Widgets.append(label)


# ====================== SystemVariables ======================
class CharPressed(Enum):
    NONE = 0
    OPERATOR = 1
    OPENING_PARENTHESIS = 2
    CLOSING_PARENTHESIS = 3


PointPressed = False
ParenthesisEquality = 0
LastChar = CharPressed.NONE
ShouldClearTextBox = True
ShouldClearLabel = False

calculator = Calculator()


# ========================= Functions =========================
def backspace() -> None:
    global PointPressed, ShouldClearTextBox
    if ShouldClearTextBox:
        return
    string = textboxStr.get()
    string = string[:-1]
    if string == "" or string == "-" or string == "0" or string == "-0":
        textboxStr.set("0")
        ShouldClearTextBox = True
    else:
        textboxStr.set(string)
    PointPressed = '.' in textboxStr.get()


def calculate():
    global ShouldClearTextBox, ShouldClearLabel, ParenthesisEquality, LastChar
    expression = labelStr.get()
    new_value = textboxStr.get()
    if (LastChar == CharPressed.CLOSING_PARENTHESIS and not ShouldClearTextBox) or ShouldClearLabel:
        expression = new_value
    elif LastChar != CharPressed.CLOSING_PARENTHESIS:
        expression += new_value

    expression += ')' * (expression.count('(') - expression.count(')'))
    labelStr.set(expression)

    try:
        answer, valid_expression = calculator.calculate(expression)
    except ValueError as err:
        messagebox.showerror("Value Error!", str(err))
    except Exception as err:
        messagebox.showerror("Something Went Wrong!", str(err))
    else:
        labelStr.set(valid_expression)
        if answer.is_integer() and 'e' not in str(answer):
            answer = int(answer)
        textboxStr.set(str(answer))
    finally:
        ShouldClearLabel = True
        ShouldClearTextBox = True
        ParenthesisEquality = 0
        LastChar = CharPressed.NONE


def check_for_operator_replacement(operator: str) -> None:
    global ShouldClearTextBox, LastChar
    string = labelStr.get()
    if not ShouldClearTextBox:
        new_value = textboxStr.get()
        string += '2' if operator == '√' and new_value == "0" else new_value
        ShouldClearTextBox = True
    else:
        string = string.rstrip("".join(ValidOperators + (' ',)))
    string += f" {operator} " if operator != '√' else operator
    labelStr.set(string)
    LastChar = CharPressed.OPERATOR


def add_first_operator(operator: str) -> None:
    global ShouldClearLabel, ShouldClearTextBox, ParenthesisEquality, LastChar
    if ShouldClearLabel:
        labelStr.set("")
        ParenthesisEquality = 0
        ShouldClearLabel = False
    string = labelStr.get()
    new_value = textboxStr.get()
    string += '2' if operator == '√' and new_value == "0" else new_value
    ShouldClearTextBox = True
    string += f" {operator} " if operator != '√' else operator
    labelStr.set(string)
    LastChar = CharPressed.OPERATOR


def operator_after_closing_parenthesis(operator: str) -> None:
    global LastChar
    string = labelStr.get()
    global ShouldClearTextBox
    if not ShouldClearTextBox:
        new_value = textboxStr.get()
        string = '2' if operator == '√' and new_value == "0" else new_value
        ShouldClearTextBox = True
    string += f" {operator} " if operator != '√' else operator
    labelStr.set(string)
    LastChar = CharPressed.OPERATOR


def operator_pressed(operator: str) -> None:
    global LastChar
    if operator == '=':
        calculate()
    elif LastChar == CharPressed.OPERATOR:
        check_for_operator_replacement(operator)
    elif LastChar == CharPressed.NONE or LastChar == CharPressed.OPENING_PARENTHESIS:
        add_first_operator(operator)
    elif LastChar == CharPressed.CLOSING_PARENTHESIS:
        operator_after_closing_parenthesis(operator)


def number_pressed(number: str) -> None:
    global PointPressed, ShouldClearTextBox
    string = textboxStr.get()
    if ShouldClearTextBox or string == "0":
        string = ""
        PointPressed = False
    if number != '.':
        string += number
    elif not PointPressed:
        if string == "":
            string = "0"
        string += '.'
        PointPressed = True

    textboxStr.set(string)
    ShouldClearTextBox = False


def close_parenthesis() -> None:
    global LastChar, ParenthesisEquality, ShouldClearTextBox
    if ParenthesisEquality <= 0 or LastChar == CharPressed.NONE:
        return
    string = labelStr.get()
    if LastChar == CharPressed.CLOSING_PARENTHESIS:
        string += ')'
    else:
        string += textboxStr.get() + ')'
        ShouldClearTextBox = True
    labelStr.set(string)
    ParenthesisEquality -= 1
    LastChar = CharPressed.CLOSING_PARENTHESIS


def parenthesis_pressed(is_opening: bool) -> None:
    global LastChar, ParenthesisEquality, ShouldClearLabel
    if not is_opening:
        close_parenthesis()
    else:
        if LastChar == CharPressed.CLOSING_PARENTHESIS or ShouldClearLabel:
            labelStr.set("(")
            ParenthesisEquality = 1
            LastChar = CharPressed.OPENING_PARENTHESIS
            ShouldClearLabel = False
            return
        string = labelStr.get()
        string += '('
        labelStr.set(string)
        ParenthesisEquality += 1
        LastChar = CharPressed.OPENING_PARENTHESIS


def clear_pressed(should_clear_all: bool) -> None:
    if not should_clear_all:
        backspace()
    else:
        global PointPressed, ParenthesisEquality, LastChar, ShouldClearTextBox, ShouldClearLabel
        labelStr.set("")
        textboxStr.set("0")
        PointPressed = False
        ParenthesisEquality = 0
        LastChar = CharPressed.NONE
        ShouldClearTextBox = True
        ShouldClearLabel = False


def plus_or_minus_pressed() -> None:
    string = textboxStr.get()
    if string == "0":
        return
    if "-" in string:
        string = string.replace('-', '')
    else:
        string = '-' + string
    textboxStr.set(string)


# ======================= ButtonConfigs =======================
placeCNF = {
    "relwidth": 0.2,
    "relheight": 0.125
}

btnCNF = {
    "font": ("Cascadia Code", 15),
    "activebackground": "#a6a6a6",
    "relief": constants.FLAT,
    "overrelief": constants.RIDGE,
    "bg": ColorCodes[14],
    "fg": ColorCodes[0]
}

ColumnNum = (0.04, 0.28, 0.52, 0.76)
RowNum = (0.1025, 0.25, 0.3975, 0.545, 0.6925, 0.84)

# ========================== Buttons ==========================
clearBtn = Button(buttons, btnCNF, text='C',
                  command=lambda: clear_pressed(True))
clearBtn.place(placeCNF, relx=ColumnNum[0], rely=RowNum[0])
openParenthesisBtn = Button(
    buttons, btnCNF, text='(', command=lambda: parenthesis_pressed(True))
openParenthesisBtn.place(placeCNF, relx=ColumnNum[1], rely=RowNum[0])
closeParenthesisBtn = Button(buttons, btnCNF, text=')',
                             command=lambda: parenthesis_pressed(False))
closeParenthesisBtn.place(placeCNF, relx=ColumnNum[2], rely=RowNum[0])
backspaceBtn = Button(buttons, btnCNF, text='⌫',
                      command=lambda: clear_pressed(False))
backspaceBtn.place(placeCNF, relx=ColumnNum[3], rely=RowNum[0])
rootBtn = Button(buttons, btnCNF, text='(r)√x',
                 command=lambda: operator_pressed('√'))
rootBtn.place(placeCNF, relx=ColumnNum[0], rely=RowNum[1])
powerBtn = Button(buttons, btnCNF, text='xⁿ',
                  command=lambda: operator_pressed('^'))
powerBtn.place(placeCNF, relx=ColumnNum[1], rely=RowNum[1])
modBtn = Button(buttons, btnCNF, text='mod',
                command=lambda: operator_pressed('%'))
modBtn.place(placeCNF, relx=ColumnNum[2], rely=RowNum[1])
divideBtn = Button(buttons, btnCNF, text='÷',
                   command=lambda: operator_pressed('/'))
divideBtn.place(placeCNF, relx=ColumnNum[3], rely=RowNum[1])
multiplyBtn = Button(buttons, btnCNF, text='×',
                     command=lambda: operator_pressed('*'))
multiplyBtn.place(placeCNF, relx=ColumnNum[3], rely=RowNum[2])
minusBtn = Button(buttons, btnCNF, text='-',
                  command=lambda: operator_pressed('-'))
minusBtn.place(placeCNF, relx=ColumnNum[3], rely=RowNum[3])
sumBtn = Button(buttons, btnCNF, text='+',
                command=lambda: operator_pressed('+'))
sumBtn.place(placeCNF, relx=ColumnNum[3], rely=RowNum[4])
resultBtn = Button(buttons, btnCNF, text='=',
                   command=lambda: operator_pressed('='))
resultBtn.place(placeCNF, relx=ColumnNum[3], rely=RowNum[5])

num9Btn = Button(buttons, btnCNF, text='9',
                 command=lambda: number_pressed('9'))
num9Btn.place(placeCNF, relx=ColumnNum[2], rely=RowNum[2])
num8Btn = Button(buttons, btnCNF, text='8',
                 command=lambda: number_pressed('8'))
num8Btn.place(placeCNF, relx=ColumnNum[1], rely=RowNum[2])
num7Btn = Button(buttons, btnCNF, text='7',
                 command=lambda: number_pressed('7'))
num7Btn.place(placeCNF, relx=ColumnNum[0], rely=RowNum[2])
num6Btn = Button(buttons, btnCNF, text='6',
                 command=lambda: number_pressed('6'))
num6Btn.place(placeCNF, relx=ColumnNum[2], rely=RowNum[3])
num5Btn = Button(buttons, btnCNF, text='5',
                 command=lambda: number_pressed('5'))
num5Btn.place(placeCNF, relx=ColumnNum[1], rely=RowNum[3])
num4Btn = Button(buttons, btnCNF, text='4',
                 command=lambda: number_pressed('4'))
num4Btn.place(placeCNF, relx=ColumnNum[0], rely=RowNum[3])
num3Btn = Button(buttons, btnCNF, text='3',
                 command=lambda: number_pressed('3'))
num3Btn.place(placeCNF, relx=ColumnNum[2], rely=RowNum[4])
num2Btn = Button(buttons, btnCNF, text='2',
                 command=lambda: number_pressed('2'))
num2Btn.place(placeCNF, relx=ColumnNum[1], rely=RowNum[4])
num1Btn = Button(buttons, btnCNF, text='1',
                 command=lambda: number_pressed('1'))
num1Btn.place(placeCNF, relx=ColumnNum[0], rely=RowNum[4])
num0Btn = Button(buttons, btnCNF, text='0',
                 command=lambda: number_pressed('0'))
num0Btn.place(placeCNF, relx=ColumnNum[1], rely=RowNum[5])
pointBtn = Button(buttons, btnCNF, text='.',
                  command=lambda: number_pressed('.'))
pointBtn.place(placeCNF, relx=ColumnNum[2], rely=RowNum[5])
plusOrMinusBtn = Button(buttons, btnCNF, text='+/-',
                        command=lambda: plus_or_minus_pressed())
plusOrMinusBtn.place(placeCNF, relx=ColumnNum[0], rely=RowNum[5])

Widgets += [clearBtn, openParenthesisBtn, closeParenthesisBtn, backspaceBtn, rootBtn, powerBtn, modBtn, divideBtn,
            multiplyBtn, minusBtn, sumBtn, resultBtn, num9Btn, num8Btn, num7Btn, num6Btn, num5Btn, num4Btn, num3Btn,
            num2Btn, num1Btn, num0Btn, pointBtn, plusOrMinusBtn]

# ======================= Key Dictionary =======================
button_map: dict[str: Button] = {
    "BackSpace": backspaceBtn,
    "c": clearBtn,
    "C": clearBtn,
    "(": openParenthesisBtn,
    ")": closeParenthesisBtn,
    "√": rootBtn,
    "r": rootBtn,
    "^": powerBtn,
    "%": modBtn,
    "m": modBtn,
    "/": divideBtn,
    "÷": divideBtn,
    "*": multiplyBtn,
    "x": multiplyBtn,
    "-": minusBtn,
    "+": sumBtn,
    "=": resultBtn,
    "Return": resultBtn,
    "9": num9Btn,
    "8": num8Btn,
    "7": num7Btn,
    "6": num6Btn,
    "5": num5Btn,
    "4": num4Btn,
    "3": num3Btn,
    "2": num2Btn,
    "1": num1Btn,
    "0": num0Btn,
    ".": pointBtn
}


# ====================== Keyboard Events ======================
def key_pressed(event) -> None:
    valid_sym = ["BackSpace", "Return"]
    key = event.keysym if event.keysym in valid_sym else event.char
    if key in button_map:
        btn = button_map[key]
        btn.invoke()


root.bind("<KeyPress>", key_pressed)
# ========================= DarkMode =========================
canvas = Canvas(switch, bg=ColorCodes[14], highlightthickness=0)
for i in range(15):
    SwitchImages.append(PhotoImage(file=f"./assets/frames/{i:02}.png"))

switch_image = canvas.create_image(26, 14, image=SwitchImages[14])
canvas.place(width=53, height=30, relx=0.8, rely=0.2)


def switch_mode() -> None:
    global DisplayState, IsChangingMode, IsDark
    if not IsChangingMode:
        return
    change_state = -1 if IsDark else +1

    line.configure(bg=ColorCodes[14 - DisplayState])
    canvas.configure(bg=ColorCodes[DisplayState])
    textbox.configure(
        disabledbackground=ColorCodes[DisplayState], disabledforeground=ColorCodes[14 - DisplayState])
    canvas.itemconfigure(switch_image, image=SwitchImages[DisplayState])
    for wid in Widgets:
        wid.configure(bg=ColorCodes[DisplayState])
    for wid in Widgets[4:]:
        wid.configure(fg=ColorCodes[14 - DisplayState])

    if IsDark and DisplayState == 0:
        IsDark = False
        IsChangingMode = False
    elif not IsDark and DisplayState == 14:
        IsDark = True
        IsChangingMode = False
    else:
        DisplayState += change_state
        root.after(12, switch_mode)


# ============================================================
def button_pressed(event) -> None:
    if type(event.widget) is Button:
        event.widget.config(relief=constants.FLAT)
    elif type(event.widget) is Canvas:
        global IsChangingMode
        IsChangingMode = True
        switch_mode()


root.bind("<Button>", button_pressed, add="+")

root.mainloop()
