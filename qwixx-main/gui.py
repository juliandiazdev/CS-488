import tkinter as tk
from random import randint
from functools import partial

### START CONSTANTS ###
# Create the main window
root = tk.Tk()
root.title("Dice Roller")
root.maxsize(850, 500)

endgame = False

# Score Dict
basis_score = {
    "red" : 0,
    "yellow" : 0,
    "green" : 0,
    "blue" : 0,
    "penalty" : 0
}

score = {
    0 : basis_score,
    1 : basis_score,
    2 : basis_score,
    3 : basis_score,
    4 : basis_score
}

# keyboard shortcut for next
def key(event):
    next_turn()

root.bind("<Key>", key)

# Colors and values for the dice
dice_colors = ['white-1', 'white-2', 'red', 'blue', 'green', 'yellow']

dice_values = {
    "white-1": 0,
    "white-2": 0,
    "red": 0,
    "blue": 0,
    "green":0,
    "yellow": 0
}

# Create and pack the roll button
rollstate = 'normal'

# current_player is the index for players which keeps tracker of roller/watcher
current_player = 0
number_of_players = 5

# True is Roller, False is Watcher
# generates an array dependent on the number of players
is_roller = [False] * number_of_players

def roleUpdate():
    global pass_okay_counter
    is_roller[current_player] = not is_roller[current_player]
    is_roller[(current_player + 1)] = not is_roller[(current_player + 1)]
    #pass_okay_counter = 0

# pass possible
pass_okay = True

# pass okay counter
pass_okay_counter = 0

# logic for counting penalties per player
penalties = [0] * number_of_players

# logic to indicate what to disable (left form picked button)
top_index = [0, 0, 0, 0]
top_indices = [top_index.copy() for _ in range(number_of_players)]

# logic to generate the board
row_array = [False] * 11
boards = [[row_array.copy() for _ in range(4)] for _ in range(number_of_players)]

# dice NOT rolled
dice_rolled = 0

name_frame = tk.Frame(root)
name_frame.pack(side='top', anchor='n')
button_frame = tk.Frame(root)
button_frame.pack(side='top', anchor='n')

### END CONSTANTS ###

# Create a canvas for dice
dice_canvas = tk.Canvas(root, width=400, height=80)

def diceCanvas():
    dice_canvas.pack_forget()
    dice_canvas.pack(pady=10)

diceCanvas()

def draw_dice(canvas, offset_x, offset_y, color, roll):
    # Draw the dice with the top-left corner at (offset_x, offset_y)
    if color == 'white-1' or color == 'white-2':
        color = 'white'
    canvas.create_rectangle(offset_x, offset_y, offset_x + 50, offset_y + 50, fill=color)

    # Coordinates for pips
    pip_coords = {
        1: [(offset_x + 25, offset_y + 25)],
        2: [(offset_x + 15, offset_y + 15), (offset_x + 35, offset_y + 35)],
        3: [(offset_x + 15, offset_y + 15), (offset_x + 25, offset_y + 25), (offset_x + 35, offset_y + 35)],
        4: [(offset_x + 15, offset_y + 15), (offset_x + 35, offset_y + 15),
            (offset_x + 15, offset_y + 35), (offset_x + 35, offset_y + 35)],
        5: [(offset_x + 15, offset_y + 15), (offset_x + 35, offset_y + 15),
            (offset_x + 25, offset_y + 25), (offset_x + 15, offset_y + 35), (offset_x + 35, offset_y + 35)],
        6: [(offset_x + 15, offset_y + 15), (offset_x + 35, offset_y + 15),
            (offset_x + 15, offset_y + 25), (offset_x + 35, offset_y + 25),
            (offset_x + 15, offset_y + 35), (offset_x + 35, offset_y + 35)],
    }
    # Draw the pips
    for pip in pip_coords[roll]:
        canvas.create_oval(pip[0] - 5, pip[1] - 5, pip[0] + 5, pip[1] + 5, fill='black')

def roll_dice():
    global dice_rolled, pass_okay, rollstate, pass_state
    pass_state = 'normal'
    # Roll each die and update the canvas
    for i, color in enumerate(dice_colors):
        roll = randint(1, 6)
        draw_dice(dice_canvas, 10 + i * 60, 10, color, roll)
        dice_values[color] = roll
    is_roller[current_player] = not is_roller[current_player]
    dice_rolled = 1
    pass_okay = True
    paint_penalty_frame()
    paint_name()
    rollstate = 'disabled'
    paint_roll_button()
    rollstate = 'normal'

def paint_name():
    for widget in name_frame.winfo_children():
        widget.destroy()

    if rollstate == 'normal' or pass_okay_counter == number_of_players:
        playerType = "Roller"
    else:
        playerType = "Watcher"

    playerType = 'Player ' + str(current_player + 1) + " (" + playerType + ")"
    if endgame:
        playerType = "ENDGAME"

    name = tk.Label(name_frame, text=playerType)
    name.pack(side='top', anchor='n')

def paint_roll_button():
    global rollstate
    for widget in button_frame.winfo_children():
        widget.destroy()
    roll_button = tk.Button(button_frame, text="Roll the Dice", command=roll_dice, state=rollstate)
    roll_button.pack()

paint_roll_button()

# COLORED ROWS
# Define the colors for each row
colors = ["#FF6666", "#FFFF66", "#66FF66", "#6666FF"]

color_numbers = ["red", "yellow", "green", "blue"]

# Define the number sequence for the rows
row_numbers = [
    list(range(2, 13)),
    list(range(2, 13)),
    list(range(12, 1, -1)),
    list(range(12, 1, -1))
]

def calcScore():
    global score

    for row_index, color in enumerate(color_numbers):
        current_row = boards[current_player][row_index]
        totalChecks = 0

        for i in current_row:
            if i:
                totalChecks += 1
        print(totalChecks)
        newRowScore = 0

        # counting logic
        if totalChecks == 2: newRowScore = 3
        if totalChecks == 3: newRowScore = 6
        if totalChecks == 4: newRowScore = 10
        if totalChecks == 5: newRowScore = 15
        if totalChecks == 6: newRowScore = 21
        if totalChecks == 7: newRowScore = 28
        if totalChecks == 8: newRowScore = 36
        if totalChecks == 9: newRowScore = 45
        if totalChecks == 10: newRowScore = 55
        if totalChecks == 11: newRowScore = 66
        if totalChecks == 12: newRowScore = 78

        score[current_player][color] = newRowScore

        print(newRowScore)
    print(score)

def hasFiveChecks(row_index):
    current_row = boards[current_player][row_index]
    totalChecks = 0

    for i in current_row:
        if i:
            totalChecks += 1

    return totalChecks >= 5

def check_valid_move(row_index, column_index, column_value):
    global destroy_container, current_player
    if pass_okay_counter == number_of_players:
        # sum white die with a color die
        current_color = color_numbers[row_index]
        value1 = dice_values[current_color] + dice_values["white-1"]
        value2 = dice_values[current_color] + dice_values["white-2"]

        if column_value == value1 or column_value == value2:
            boards[current_player][row_index][column_index] = True
            top_indices[current_player][row_index] = column_index
            destroy_container = True
            paint_rows()
    else:
        sum_of_whites = dice_values['white-1'] + dice_values['white-2']
        if column_value == sum_of_whites:
            boards[current_player][row_index][column_index] = True
            top_indices[current_player][row_index] = column_index
            destroy_container = True
            paint_rows()

    # if number clicked in row
    #   disable other possible clicks



    #if not hasFiveChecks(row_index):


destroy_container = False
row_container = tk.Frame(root)
row_container.pack(anchor='center', pady=4, padx=20)

# Create the rows of buttons
def paint_rows():
    # if not hasFiveChecks(row_index):
    #     lastButtonState = 'disabled'
    # else:
    #     lastButtonState = 'enabled'
    # add a changeable state to buttons 12, 12, 2, 2

    if destroy_container:
        for widget in row_container.winfo_children():
            widget.destroy()

    for i, numbers in enumerate(row_numbers):
        row_frame = tk.Frame(row_container, bg=colors[i])
        row_frame.pack(fill='x', pady=5)

        for j, number in enumerate(numbers):
            red_state = number == 12 and i == 0
            yellow_state = number == 12 and i == 1
            green_state = number == 2 and i == 2
            blue_state = number == 2 and i == 3

            if top_indices[current_player][i] > j or red_state or yellow_state or blue_state or green_state:
                state = 'disabled'
            else:
                state = 'normal'

            if ((number == 12 and (i == 0 or i == 1)) or (number == 2 and (i == 2 or i == 3))) and hasFiveChecks(i):
                state = 'normal'

            if not boards[current_player][i][j]:
                button = tk.Button(row_frame, text=str(number), bg=colors[i], width=3, height=1, state=state, command= partial(check_valid_move, i, j, number))
                button.pack(side='left', padx=1, pady=1)
            else:
                label = tk.Label(row_frame, text='x', bg=colors[i], height=1, width=3)
                label.pack(side='left', padx=1, pady=1)

        # Add the lock button at the end
        lock_button = tk.Button(row_frame, text="🔒", bg=colors[i], width=3, height=1, command=partial(check_lock, i))
        lock_button.pack(side='left', padx=1, pady=1)

def check_lock(row_index):
    print('check lock ', row_index)
    crosses = 0

    print(boards[current_player][row_index])
    # for i in range(boards[current_player][row_index]):
    #     print(i)


paint_name()
paint_rows()

# Define the multiplication values and results
multiplications = [
    (2, 3), (3, 6), (4, 10), (5, 15),
    (6, 21), (7, 28), (8, 36), (9, 45), (10, 55),
    (11, 66), (12, 78)
]

counters_frame = tk.Frame(root)
counters_frame.pack(anchor='s', pady=15, padx=35)

# Create the counter labels
for factor, result in multiplications:
    counter_text = f"{factor}x\n{result}"
    label = tk.Label(counters_frame, text=counter_text, bg="white", width=4, height=4, relief="ridge", bd=1)
    label.pack(side='left', padx=1, pady=1)

# PENALTY COUNTER LABELS
penalty_frame = tk.Frame(counters_frame)
penalty_frame.pack(side='bottom', padx=7)

pass_state = 'normal'

def paint_penalty_frame():
    # if dice_rolled == 0:
    #     pass_state = 'disabled'
    # else:
    #     pass_state = 'normal'
    for widget in penalty_frame.winfo_children():
        widget.destroy()
    for i in range(4):
        if penalties[current_player] > i:
            text = 'x'
        else:
            text = ''
        label = tk.Label(penalty_frame, text=text, bg="white", width=5, height=2, relief="ridge", bd=1)
        label.pack(side='left', padx=2, pady=2)
    if is_roller[current_player] and not pass_okay:
        bg = "red"
    else:
        bg = "white"
    #print(bg)
    pass_button = tk.Button(penalty_frame, text="Pass", command=pass_turn, state=pass_state, bg=bg)
    pass_button.pack(side="top", anchor='ne')


def pass_turn():
    global current_player, pass_okay, destroy_container, pass_okay_counter, pass_state, endgame
    # # if pass_okay:
    # #     pass_okay = False
    #
    # if pass_okay_counter <= number_of_players:
    #     pass_okay = not pass_okay

    if is_roller[current_player] and pass_okay_counter == number_of_players:
        penalties[current_player] += 1
        if penalties[current_player] >= 4:
            endgame = True
        #pass_state = 'disabled'
        print("Penalty, ", current_player + 1)

    paint_penalty_frame()
    # current_player = (current_player + 1) % number_of_players
    # paint_name()
    # paint_penalty_frame()
    # print('rows:')
    # destroy_container = True
    # paint_rows()

paint_penalty_frame()

# this will run when you hit a button in a row, the pass button or hit 'enter' (to move to the next step)
def next_turn():
    global current_player, destroy_container, pass_okay_counter, rollstate
    print("pre update: ", pass_okay_counter)
    pass_okay_counter += 1

    if pass_okay_counter == number_of_players + 1:
        pass_okay_counter = 0

    if pass_okay_counter == 0:
        rollstate = 'normal'
    else:
        rollstate = 'disabled'

    paint_roll_button()

    print("pass_okay_counter", pass_okay_counter)

    if pass_okay_counter > number_of_players:
        roleUpdate()

    current_player = (current_player + 1) % number_of_players
    calcScore()
    paint_scoresheet()
    paint_name()
    paint_penalty_frame()
    destroy_container = True
    paint_rows()


# FINAL SCORE SHEET

# Create a frame for the total boxes and operators
totals_frame = tk.Frame(root, pady=10, padx=26)
totals_frame.pack(side='bottom')

# roll_button = tk.Label(totals_frame, text="=", font=('Arial', 14))

# Create the total boxes and operators
def paint_scoresheet():
    for widget in totals_frame.winfo_children():
        widget.destroy()
    for color in color_numbers:
        total_box = tk.Label(totals_frame, text=score[current_player][color], bg=color, width=10)
        total_box.pack(side='left', padx=10)

        # Add a plus label after each total box except the last one
        if color != color_numbers[-1]:
            plus_label = tk.Label(totals_frame, text="+", font=('Arial', 14))
            plus_label.pack(side='left', padx=2)

    # The subtraction operator before the last white box (to subtract from the result)
    minus_label = tk.Label(totals_frame, text="-", font=('Arial', 14))
    minus_label.pack(side='left', padx=2)

    # The final white total box (to subtract from the result)
    final_total_box = tk.Label(totals_frame, text=score[current_player]['penalty'], bg="#FFFFFF", width=10)
    final_total_box.pack(side='left', padx=2)

    # The equals label
    equals_label = tk.Label(totals_frame, text="=", font=('Arial', 14))
    equals_label.pack(side='left', padx=2)

    # totals
    total = score[current_player]["red"] + score[current_player]["yellow"] + score[current_player]["green"] + score[current_player]["blue"] - score[current_player]["penalty"]

    # The result box, which is larger than the total boxes
    result_box = tk.Label(totals_frame, text=total, bg="#FFFFFF", width=20)
    result_box.pack(side='left', padx=4)

paint_scoresheet()

# RUN THE APPLICATION
root.mainloop()
