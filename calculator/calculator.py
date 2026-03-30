import tkinter as tk

# ---------------- STATE ---------------- #
a = None
operator = None

# ---------------- FUNCTIONS ---------------- #

def update_display(value):
    display_var.set(value)


def get_display():
    return display_var.get()


def clear_all():
    global a, operator
    a = None
    operator = None
    update_display("0")


def format_result(num):
    if num % 1 == 0:
        return str(int(num))
    return str(round(num, 6))


def button_clicked(value):
    global a, operator

    current = get_display()

    # DIGITS
    if value.isdigit():
        if current == "0":
            update_display(value)
        else:
            update_display(current + value)

    # DECIMAL
    elif value == ".":
        if "." not in current:
            update_display(current + ".")

    # OPERATORS
    elif value in ["+", "-", "*", "/"]:
        a = current
        operator = value
        update_display("0")

    # EQUALS
    elif value == "=":
        if a is None or operator is None:
            return

        b = current

        try:
            num_a = float(a)
            num_b = float(b)

            if operator == "+":
                result = num_a + num_b
            elif operator == "-":
                result = num_a - num_b
            elif operator == "*":
                result = num_a * num_b
            elif operator == "/":
                if num_b == 0:
                    update_display("Error")
                    return
                result = num_a / num_b

            update_display(format_result(result))

        except:
            update_display("Error")

        # Reset after calculation
        a = None
        operator = None

    # CLEAR
    elif value == "C":
        clear_all()


# ---------------- GUI ---------------- #

root = tk.Tk()
root.title("Calculator")
root.resizable(False, False)

# Center window
window_width = 300
window_height = 400

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)

root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Display
display_var = tk.StringVar(value="0")

display = tk.Label(
    root,
    textvariable=display_var,
    font=("Arial", 24),
    bg="white",
    anchor="e",
    relief="sunken",
    height=2
)
display.grid(row=0, column=0, columnspan=4, sticky="nsew")

# Buttons layout
buttons = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"],
    ["C"]
]

# Create buttons
for r, row in enumerate(buttons, start=1):
    for c, value in enumerate(row):
        btn = tk.Button(
            root,
            text=value,
            font=("Arial", 16),
            command=lambda v=value: button_clicked(v)
        )

        if value == "C":
            btn.grid(row=r, column=0, columnspan=4, sticky="nsew")
        else:
            btn.grid(row=r, column=c, sticky="nsew")

# Make grid expand nicely
for i in range(5):
    root.grid_rowconfigure(i, weight=1)

for i in range(4):
    root.grid_columnconfigure(i, weight=1)

# Start app
root.mainloop()