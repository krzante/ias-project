import tkinter as tk
from tkinter import *
from tkinter import ttk
from overlay import Window
import numpy
import pyglet
from pynput.keyboard import Key, Listener
from asteval import Interpreter
import json
import sys

aeval = Interpreter()


# End turn calculations
def end_round():
    used = int(canvas1.itemcget(e_used_num, 'text'))
    gained = int(canvas1.itemcget(e_gained_num, 'text'))
    destroyed = int(canvas1.itemcget(e_destroyed_num, 'text'))
    energy = int(canvas1.itemcget(energy_count, 'text'))
    round = int(canvas1.itemcget(round_count, 'text'))

    #saving current round state
    prev_round["round"] = str(round)
    prev_round["energy"] = str(energy)

    energy = numpy.clip((energy - used + gained - destroyed), 0, 8) + 2

    canvas1.itemconfig(round_count, text = str(round+1))
    canvas1.itemconfig(energy_count, text = str(energy))
    canvas1.itemconfig(e_used_num, text = 0)
    canvas1.itemconfig(e_gained_num, text = 0)
    canvas1.itemconfig(e_destroyed_num, text = 0)
    print("End Round")

# Reset fuction
def reset_app():
    canvas1.itemconfig(round_count, text = 1)
    canvas1.itemconfig(energy_count, text = 3)
    canvas1.itemconfig(e_used_num, text = 0)
    canvas1.itemconfig(e_gained_num, text = 0)
    canvas1.itemconfig(e_destroyed_num, text = 0)

    prev_round["round"] = "1"
    prev_round["energy"] = "3"
    print("Reset")


# Return to the previous round state
def undo_round():
    if canvas1.itemcget(round_count, 'text') != prev_round["round"]:
        canvas1.itemconfig(round_count, text = prev_round["round"])
        canvas1.itemconfig(energy_count, text = prev_round["energy"])

        canvas1.itemconfig(e_used_num, text = 0)
        canvas1.itemconfig(e_gained_num, text = 0)
        canvas1.itemconfig(e_destroyed_num, text = 0)
        print("Undo")


# Dictionary of the prev round
prev_round = {
    "round":"1",
    "energy": "3",
}


def btn_add(id,canvas):
    num = str(numpy.clip(int(canvas.itemcget(id, 'text'))+1, 0, 50)) #getter ng item
    canvas.itemconfig(id, text = num) #setter function


def btn_minus(id,canvas):
    num = str(numpy.clip(int(canvas.itemcget(id, 'text'))-1, 0, 50)) #getter ng item
    canvas.itemconfig(id, text = num) #setter function


def create_norm_btn(root, func, img):
    return Button(
        root,
        image = img,
        borderwidth = 0,
        highlightthickness = 0,
        command = func,
        relief = "flat")


def create_lambda_btn(root, func, param, img, param2 = "NULL"):
    if param2 != "NULL":
        return Button(
        root,
        image = img,
        borderwidth = 0,
        highlightthickness = 0,
        command = lambda:func(param,param2),
        relief = "flat")
    else:
        return Button(
            root,
            image = img,
            borderwidth = 0,
            highlightthickness = 0,
            command = lambda:func(param),
            relief = "flat")


# I used if else because pyinstaller does not support match cases
def on_press(key):
    if key.char.upper() == "Q":
        btn_minus(e_used_num)
    elif key.char.upper() == "W":
        btn_add(e_used_num)
    elif key.char.upper() == "A":
        btn_minus(e_gained_num)
    elif key.char.upper() == "S":
        btn_add(e_gained_num)
    elif key.char.upper() == "Z":
        btn_minus(e_destroyed_num)
    elif key.char.upper() == "X":
        btn_add(e_destroyed_num)
    elif key.char.upper() == "E":
        end_round()
    elif key.char.upper() == "R":
        reset_app()
    elif key.char.upper() == "F":
        undo_round()

###################### Tab2 functions ######################

tab2_data = {
    "win":"0",
    "loss": "0",
    "draw": "0",
    "slp": "0"
}

tab2_calculation = ""
def add_to_calc(symbol):
    global tab2_calculation
    tab2_calculation += str(symbol)
    calc_text.delete(1.0, "end")
    calc_text.insert(1.0, tab2_calculation)

def eval_calc():
    global tab2_calculation
    try:
        tab2_calculation = str(aeval(tab2_calculation))
        calc_text.delete(1.0, "end")
        calc_text.insert(1.0, tab2_calculation)
    except:
        clear_calc()
        calc_text.insert(1.0, "Error")

def clear_calc():
    global tab2_calculation
    tab2_calculation = ""
    calc_text.delete(1.0, "end")

def del_calc():
    global tab2_calculation
    if tab2_calculation == "NONE":
        clear_calc()
    elif tab2_calculation != "":
        tab2_calculation = tab2_calculation.rstrip(tab2_calculation[-1])
        # Str = str(calc_text)
        # Str = Str.rstrip(Str[-1])
        calc_text.delete(1.0, "end")
        calc_text.insert(1.0, tab2_calculation)

def reset_winrate():
    canvas2.itemconfig(win_label, text = 0)
    canvas2.itemconfig(loss_label, text = 0)
    canvas2.itemconfig(draw_label, text = 0)

def tab2_save():
    global tab2_calculation
    tab2_data["win"] = canvas2.itemcget(win_label, 'text')
    tab2_data["loss"] = canvas2.itemcget(loss_label, 'text')
    tab2_data["draw"] = canvas2.itemcget(draw_label, 'text')
    if tab2_calculation == "":
        tab2_data["slp"] = "0"
    else:
        tab2_data["slp"] = tab2_calculation
    with open('./saves/tab2.json', 'w') as fjson:
        json.dump(tab2_data, fjson)

def tab2_load():
    global tab2_calculation
    data = {}
    with open('./saves/tab2.json', 'r') as fjson:
        data = json.load(fjson)

    canvas2.itemconfig(win_label, text = data["win"])
    canvas2.itemconfig(loss_label, text = data["loss"])
    canvas2.itemconfig(draw_label, text = data["draw"])
    tab2_calculation = str(data["slp"])
    calc_text.delete(1.0, "end")
    calc_text.insert(1.0, tab2_calculation)


pyglet.font.add_file('./fonts/AldotheApache.ttf')
dflt_fnt = "Aldo the Apache"
clr_white = "#ffffff"
clr_black = "#000000"

# Setting up the window and tabs
window = tk.Tk()
nb = ttk.Notebook(window)
window.iconbitmap("./images/icon.ico")

window.geometry("300x475")
# window.configure(bg = "red")
window.title("zakyr's Axie Calculator")
window.attributes('-alpha', 0.6)
window.attributes('-topmost', 1)

tab1 = Frame(nb, width=300, height=450)
tab2 = Frame(nb, width=300, height=450)

nb.add(tab1, text="ENERGY")
nb.add(tab2, text="WINRATE")
nb.pack()


##################### Tab1 #########################################################################
canvas1 = Canvas(
    tab1,
    bg = clr_white,
    height = 450,
    width = 300,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge")
canvas1.place(x = 0, y = 0)


#Loading Background Image
background_img = PhotoImage(master=tab1, file = f"./images/background_tab1.png")
background = canvas1.create_image(151.0, 225.5, image=background_img)


#End Turn Button
img0 = PhotoImage(master=tab1, file = f"./images/btn-end.png") # End turn button
b0 = create_norm_btn(tab1, end_round, img0)
b0.place(x = 104, y = 393, width = 97, height = 52)

#Reset Button
img1 = PhotoImage(master=tab1, file = f"./images/btn-reset.png")  # Reset Button
b1 = create_norm_btn(tab1, reset_app, img1)
b1.place(x = 17, y = 389, width = 51, height = 53)

# Undo Button
img2 = PhotoImage(master=tab1, file = f"./images/btn-undo.png")  # Undo Button
b2 = create_norm_btn(tab1, undo_round, img2)
b2.place(x = 236, y = 389, width = 51, height = 53)


# Loading Plus and Minus buttons for tab1
btn_minus_img = PhotoImage(master=tab1, file = f"./images/btn_minus.png")
btn_plus_img = PhotoImage(master=tab1, file = f"./images/btn_plus.png")


# Energy Destroyed Field
e_destroyed_num = canvas1.create_text(150.5, 342.5, text = "0", fill = clr_white, font = (dflt_fnt, int(30.0)))
canvas1.create_text(151.0, 302.5, text = "ENERGY DESTROYED", fill = clr_black, font = (dflt_fnt, int(16.0)))
# Minus Energy Destroyed 
b3 = create_lambda_btn(tab1, btn_minus, e_destroyed_num, btn_minus_img, canvas1)
b3.place(x = 66, y = 316, width = 51, height = 53)
# Energy Destroyed PLUS
b4 = create_lambda_btn(tab1, btn_add, e_destroyed_num, btn_plus_img, canvas1)
b4.place(x = 188, y = 318, width = 51, height = 53)


# Energy Gained Number
canvas1.create_text(151.0, 219.5, text = "ENERGY GAINED", fill = clr_black, font = (dflt_fnt, int(16.0)))
e_gained_num = canvas1.create_text(150.0, 259.5, text = "0", fill = clr_white, font = (dflt_fnt, int(30.0)))
# Energy Gained MINUS
b5 = create_lambda_btn(tab1, btn_minus, e_gained_num, btn_minus_img, canvas1)
b5.place(x = 66, y = 233, width = 51, height = 53)
# Energy Gained PLUS
b6 = create_lambda_btn(tab1, btn_add, e_gained_num, btn_plus_img, canvas1)
b6.place(x = 188, y = 232, width = 51, height = 53)


# Energy Used Field 
canvas1.create_text(150.0, 136.5, text = "ENERGY USED", fill = clr_black, font = (dflt_fnt, int(16.0)))
e_used_num = canvas1.create_text(149.5, 176.5, text = "0", fill = clr_white, font = (dflt_fnt, int(30.0)))
# USED MINUS
b7 = create_lambda_btn(tab1, btn_minus, e_used_num, btn_minus_img, canvas1)
b7.place(x = 65, y = 150, width = 51, height = 53)
# USED PLUS
b8 = create_lambda_btn(tab1, btn_add, e_used_num, btn_plus_img, canvas1)
b8.place(x = 186, y = 150, width = 51, height = 53)


# Energy count
energy_count = canvas1.create_text(149.0, 86.0,text = "3",  fill = clr_white, font = (dflt_fnt, int(48.0)))


# Round countg
round_count = canvas1.create_text( 90.5, 28.0, text = "1", fill = clr_white, font = (dflt_fnt, int(24.0)))

####################################################################################################
##################### Tab2 #########################################################################
canvas2 = Canvas(
    tab2,
    bg = "#ffffff",
    height = 500,
    width = 300,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge")
canvas2.place(x = 0, y = 0)

background_tab2_img = PhotoImage(master=tab2, file = f"./images/background_tab2.png")
background = canvas2.create_image(
    151.0, 225.5,
    image=background_tab2_img)


btn_small_plus_img = PhotoImage(master=tab2, file=f"./images/btn_small_plus.png")
btn_small_minus_img = PhotoImage(master=tab2, file=f"./images/btn_small_minus.png")
btn_small_reset_img = PhotoImage(master=tab2, file=f"./images/btn_small_reset.png")
btn_save_img = PhotoImage(master=tab2, file=f"./images/btn_save.png")

# 7
btn_7_img = PhotoImage(master=tab2, file=f"./images/btn_calc_7.png")
calc_7 = create_lambda_btn(tab2, add_to_calc, "7", btn_7_img)
calc_7.place(x = 70, y = 263, width = 39, height = 39)

#8
btn_8_img = PhotoImage(master=tab2, file=f"./images/btn_calc_8.png")
calc_8 = create_lambda_btn(tab2, add_to_calc, "8", btn_8_img)
calc_8.place(x = 112, y = 263, width = 39, height = 39)

#9
btn_9_img = PhotoImage(master=tab2, file=f"./images/btn_calc_9.png")
calc_9 = create_lambda_btn(tab2, add_to_calc, "9", btn_9_img)
calc_9.place(x = 154, y = 263, width = 39, height = 39)

#DEL
btn_del_img = PhotoImage(master=tab2, file=f"./images/btn_calc_del.png")
calc_del = create_norm_btn(tab2, del_calc, btn_del_img)
calc_del.place(x = 196, y = 263, width = 39, height = 39)

#4
btn_4_img = PhotoImage(master=tab2, file=f"./images/btn_calc_4.png")
calc_4 = create_lambda_btn(tab2, add_to_calc, "4", btn_4_img)
calc_4.place(x = 70, y = 305, width = 39, height = 39)

#5
btn_5_img = PhotoImage(master=tab2, file=f"./images/btn_calc_5.png")
calc_5 = create_lambda_btn(tab2, add_to_calc, "5", btn_5_img)
calc_5.place(x = 112, y = 305, width = 39, height = 39)

#6
btn_6_img = PhotoImage(master=tab2, file=f"./images/btn_calc_6.png")
calc_6 = create_lambda_btn(tab2, add_to_calc, "6", btn_6_img)
calc_6.place(x = 154, y = 305, width = 39, height = 39)

#-
btn_calc_minus_img = PhotoImage(master=tab2, file=f"./images/btn_calc_minus.png")
calc_minus = create_lambda_btn(tab2, add_to_calc, "-", btn_calc_minus_img)
calc_minus.place(x = 196, y = 305, width = 39, height = 39)

#1
btn_1_img = PhotoImage(master=tab2, file=f"./images/btn_calc_1.png")
calc_8 = create_lambda_btn(tab2, add_to_calc, "1", btn_1_img)
calc_8.place(x = 70, y = 347, width = 39, height = 39)

#2
btn_2_img = PhotoImage(master=tab2, file=f"./images/btn_calc_2.png")
calc_2 = create_lambda_btn(tab2, add_to_calc, "2", btn_2_img)
calc_2.place(x = 112, y = 347, width = 39, height = 39)

#3
btn_3_img = PhotoImage(master=tab2, file=f"./images/btn_calc_3.png")
calc_3 = create_lambda_btn(tab2, add_to_calc, "3", btn_3_img)
calc_3.place(x = 154, y = 347, width = 39, height = 39)

#Clear
btn_c_img = PhotoImage(master=tab2, file=f"./images/btn_calc_c.png")
calc_clear = create_norm_btn(tab2, clear_calc, btn_c_img)
calc_clear.place(x = 70, y = 389, width = 39, height = 39)

#0
btn_0_img = PhotoImage(master=tab2, file=f"./images/btn_calc_0.png")
calc_0 = create_lambda_btn(tab2, add_to_calc, "0", btn_0_img)
calc_0.place(x = 112, y = 389, width = 39, height = 39)

# =
btn_equals_img = PhotoImage(master=tab2, file=f"./images/btn_calc_equals.png")
calc_equals = create_norm_btn(tab2, eval_calc, btn_equals_img)
calc_equals.place(x = 154, y = 389, width = 39, height = 39)

# +
btn_calc_plus_img = PhotoImage(master=tab2, file=f"./images/btn_calc_plus.png")
calc_plus = create_lambda_btn(tab2, add_to_calc, "+", btn_calc_plus_img)
calc_plus.place(x = 196, y = 347, width = 39, height = 81)

#winrate label
win_label = canvas2.create_text(64.0, 97.0, text = "0", fill = "#ffffff", font = (dflt_fnt, int(40.0)))

#loss label
loss_label = canvas2.create_text(151.0, 97.0, text = "0", fill = "#ffffff", font = (dflt_fnt, int(40.0)))

#draw label
draw_label = canvas2.create_text(236.0, 97.0, text = "0", fill = "#ffffff", font = (dflt_fnt, int(40.0)))

# small - ng Loss
loss_minus = create_lambda_btn(tab2, btn_minus, loss_label, btn_small_minus_img, canvas2)
loss_minus.place(x = 119, y = 136, width = 29, height = 30)

# small + Loss
loss_plus = create_lambda_btn(tab2, btn_add, loss_label, btn_small_plus_img, canvas2)
loss_plus.place(x = 157, y = 136, width = 30, height = 30)

#small - WIN
win_minus = create_lambda_btn(tab2, btn_minus, win_label, btn_small_minus_img, canvas2)
win_minus.place(x = 33, y = 134, width = 29, height = 30)

# small + WIN
win_plus = create_lambda_btn(tab2, btn_add, win_label, btn_small_plus_img, canvas2)
win_plus.place(x = 71, y = 134, width = 29, height = 30)

#small - DRAW
draw_minus = create_lambda_btn(tab2, btn_minus, draw_label, btn_small_minus_img, canvas2)
draw_minus.place(x = 205, y = 136, width = 29, height = 30)

# small + DRAW
draw_plus = create_lambda_btn(tab2, btn_add, draw_label, btn_small_plus_img, canvas2)
draw_plus.place(x = 243, y = 136, width = 29, height = 30)

#save button
b19 = create_norm_btn(tab2, tab2_save, btn_save_img)
b19.place(x = 254, y = 407, width = 35, height = 36)

#small reset
b20 = create_norm_btn(tab2, reset_winrate, btn_small_reset_img)
b20.place(x = 6, y = 6, width = 35, height = 35)

#text Box
# tab2_textbox_img = PhotoImage(master=tab2, file = f"./images/tab2_textbox.png")
# entry0_bg = canvas2.create_image(128.5, 226.0, image = tab2_textbox_img)
calc_text = Text(
    tab2,
    # height=36,
    # width=90,
    # insertwidth=0,
    bd = 0,
    bg = "#d0b285",
    # yscrollcommand=S.set,
    highlightthickness = 0,
    font = (dflt_fnt, int(25.0)))
calc_text.place(
    x = 45, y = 203,
    width = 167,
    height = 36)
####################################################################################################

# # Hotkeys not working when exported as exe
# window.bind("<w>", on_press)
# window.bind("<q>", on_press)
# window.bind("<s>", on_press)
# window.bind("<a>", on_press)
# window.bind("<x>", on_press)
# window.bind("<z>", on_press)
# window.bind("<f>", on_press)
# window.bind("<r>", on_press)
# window.bind("<e>", on_press)

# window.bind("<W>", on_press)
# window.bind("<Q>", on_press)
# window.bind("<S>", on_press)
# window.bind("<A>", on_press)
# window.bind("<X>", on_press)
# window.bind("<Z>", on_press)
# window.bind("<F>", on_press)
# window.bind("<R>", on_press)
# window.bind("<E>", on_press)


tab2_load()
window.resizable(False, False)
window.mainloop()
sys.exit()
