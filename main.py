import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox, simpledialog
# from matplotlib.font_manager import json_dump
from overlay import Window
import numpy
import pyglet
from pynput.keyboard import Key, Listener
from asteval import Interpreter
import json
import sys
import random

import hashlib

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import createTransactionController
from decimal import Decimal

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import *



class CreditCard:
    number = None
    expiration_date = None
    code = None


class TransactionResponse:
    is_success = False
    messages = []

class CustomerInfo:
    first_name = None
    last_name = None
    company = None
    address = None
    city = None
    state = None
    zip = None
    country = None
    
customer = CustomerInfo()
card = CreditCard()


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
window.title("Suñga, Yumang & Zante")
# window.attributes('-alpha', 0.8)
window.attributes('-topmost', 1)

tab1 = Frame(nb, width=300, height=450)
tab2 = Frame(nb, width=300, height=450)
tab3 = Frame(nb, width=300, height=450)

nb.add(tab1, text="ENERGY")
nb.add(tab2, text="WINRATE")
nb.add(tab3, text="DONATE")
nb.pack()

### CREDIT CARD PAYMENT ###################################
def charge_credit_card(user, invoiceNumber_arg, customerID_arg): #amount, card, customer
    """
    Charge a credit card
    """

    # Create a merchantAuthenticationType object with authentication details
    # retrieved from the constants file
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = get_api_login_id()
    merchantAuth.transactionKey = get_transaction_id()

    # Create the payment data for a credit card
    creditCard = apicontractsv1.creditCardType()
    creditCard.cardNumber = user['Card Number']#card.number 
    creditCard.expirationDate = user['Exp Date']#card.expiration_date 
    creditCard.cardCode = user['CVV']#card.code

    # Add the payment data to a paymentType object
    payment = apicontractsv1.paymentType()
    payment.creditCard = creditCard

    # Create order information
    order = apicontractsv1.orderType()
    order.invoiceNumber = invoiceNumber_arg #str(random.randint(1, 99999999999))
    order.description = "Donation"

    # Set the customer's Bill To address
    customerAddress = apicontractsv1.customerAddressType()
    customerAddress.firstName = user['First Name']#customer.first_name 
    customerAddress.lastName = user['Last Name']#customer.last_name 
    customerAddress.company = user['Company']#customer.company
    customerAddress.address = user['Address']#customer.address
    customerAddress.city = user['City']#customer.city
    customerAddress.state = user['State']#customer.state
    customerAddress.zip = user['Zip']#customer.zip
    customerAddress.country = user['Country']#customer.country

    # Set the customer's identifying information
    customerData = apicontractsv1.customerDataType()
    customerData.type = "individual"
    customerData.id = customerID_arg #str(random.randint(1, 99999)) #"18467382746"
    customerData.email = "kyleramon.zante@tup.edu.ph"

    # Add values for transaction settings
    duplicateWindowSetting = apicontractsv1.settingType()
    duplicateWindowSetting.settingName = "duplicateWindow"
    duplicateWindowSetting.settingValue = "600"
    settings = apicontractsv1.ArrayOfSetting()
    settings.setting.append(duplicateWindowSetting)

    # setup individual line items
    line_item_1 = apicontractsv1.lineItemType()
    line_item_1.itemId = "420m4-RK-p091"
    line_item_1.name = "Donation: IAS-Project"
    line_item_1.description = "Monetary Donation Test for IAS Project"
    line_item_1.quantity = "1"
    line_item_1.unitPrice = user['Amount']

    # build the array of line items
    line_items = apicontractsv1.ArrayOfLineItem()
    line_items.lineItem.append(line_item_1)

    # Create a transactionRequestType object and add the previous objects to it.
    transactionrequest = apicontractsv1.transactionRequestType()
    transactionrequest.transactionType = "authCaptureTransaction"
    transactionrequest.amount = user['Amount']
    transactionrequest.payment = payment
    transactionrequest.order = order
    transactionrequest.billTo = customerAddress
    transactionrequest.customer = customerData
    transactionrequest.transactionSettings = settings
    transactionrequest.lineItems = line_items

    # Assemble the complete transaction request
    createtransactionrequest = apicontractsv1.createTransactionRequest()
    createtransactionrequest.merchantAuthentication = merchantAuth
    createtransactionrequest.refId = "MerchantID-0001"
    createtransactionrequest.transactionRequest = transactionrequest
    # Create the controller
    createtransactioncontroller = createTransactionController(
        createtransactionrequest)
    createtransactioncontroller.execute()

    response = createtransactioncontroller.getresponse()
    result = dict()
    if response is not None:
        # Check to see if the API request was successfully received and acted upon
        if response.messages.resultCode == "Ok":
            # Since the API request was successful, look for a transaction response
            # and parse it to display the results of authorizing the card
            if hasattr(response.transactionResponse, 'messages') is True:
                result['status'] = True
                result['message'] = response.transactionResponse.messages.message[0].description
            else:
                result['status'] = False
                result['message'] = "Failed Transaction."
        else:
            result['status'] = False
            result['message'] = "Failed Transaction."
    else:
        result['status'] = False
        result['message'] = "Null Response."
    
    return result

### HASHING FUNCTIONS #################################
def tojs(userInputs):
    with open("sample.json", "w") as outfile:
        json.dump(userInputs,outfile)

def hashInput(userInputs):
    for userInput in userInputs:
        hashvar = hashlib.md5(str(userInputs[userInput]).encode('utf-8'))
        userInputs[userInput]= str(hashvar.hexdigest()) #hash(userInputs[userInput])
    tojs(userInputs)
    return userInputs

### NEW WINDOW USER INPUT #############################
def user_input():
    #  New window for input
    window = tk.Tk()
    window.title('DONATION')
    window.geometry("300x450")
    window.iconbitmap("./images/icon.ico") #Added the window icon
    window.attributes('-topmost', 1)
    btn_donate["state"] = "disabled"

    invoiceNumbervar = str(random.randint(1, 99999))
    customerIDvar = str(random.randint(1, 99999))
    def close_window():
        btn_donate["state"] = "normal"
        window.destroy()
    
    userInputs = dict()

    def new_entry():
        i = 0
        for fields in textFields:
            userInputs[labels[i]] = fields.get()
            i = i+1

        # Email Setup
        code = str(random.randint(100000, 999999))
        port = 587  # For starttls
        smtp_server = "smtp.gmail.com"
        receiver_email = "kyleramon.zante@tup.edu.ph"
        sender_email = "thinklikblog@gmail.com"
        password = ""

        date_format_str = '%d/%m/%Y %H:%M:%S.%f'
        try: # Load card number start time
            with open('time.json', 'r') as fjson:
                data = json.load(fjson)

            cardNumber = textFields[1].get()
            jsonTime = data[cardNumber]

        except: # Initialize start time for new card number
            with open('time.json', 'r') as fjson:
                data = json.load(fjson)
         
            jsonTime  = '01/1/0001 00:00:00.000000' # Initial time
            cardNumber = textFields[1].get()
            data[cardNumber] = jsonTime

            with open('time.json', 'w') as fjson:
                json.dump(data, fjson)

        # Convert string from json to time object
        startTime = datetime.strptime(jsonTime, date_format_str)

        # Get current time
        currentTime = datetime.now()
        timeLeft = currentTime - startTime

        
        if timeLeft <= timedelta(minutes=10):
            seconds = timeLeft.seconds
            minutes = (seconds//60)%60 
            messagebox.showinfo(title='STATUS', message="Please try again in {} minutes".format(10-minutes))
           
        else: # Email Setup
            code = str(random.randint(100000, 999999))
            port = 587  # For starttls
            smtp_server = "smtp.gmail.com"
            receiver_email = "richardandrei.sunga@tup.edu.ph"
            sender_email = "thinklikblog@gmail.com"
            password = "09123456think!"

            message = """\
            IAS PROJECT: VERIFICATION

            INPUT THE FOLLOWING 6 DIGIT CODE TO CONFIRM THE TRABSACTION
            {}""".format(code)
        
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, port) as server:
                server.ehlo()  # Can be omitted
                server.starttls(context=context)
                server.ehlo()  # Can be omitted
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
            aeval = Interpreter()

            # Input box
            ROOT = tk.Tk()
            ROOT.withdraw()
            ROOT.attributes('-topmost', 1)
            
            valid = False
            tries = 0
            while(not valid):
                
                # If the user inputs the code 3 times in a row
                if (tries == 3):

                    # ADD START TIME OF THE TIMEOUT
                    with open('time.json', 'r') as fjson:
                        data = json.load(fjson)
                
                    # Get current time and convert it from time object to string
                    currentTime = datetime.now()
                    currentTime = currentTime.strftime('%d/%m/%Y %H:%M:%S.%f')

                    cardNumber = textFields[1].get()
                    data[cardNumber] = currentTime

                    with open('time.json', 'w') as fjson:
                        json.dump(data, fjson)

                    # EMAIL NOTIFICATION FOR TIMEOUT
                    message = """\
                    IAS PROJECT: SECURITY ALERT

                    SOMEONE IS TRYING TO MAKE TRANSACTIONS WITH YOUR CREDIT CARD 
                    """
                
                    context = ssl.create_default_context()
                    with smtplib.SMTP(smtp_server, port) as server:
                        server.ehlo()  # Can be omitted
                        server.starttls(context=context)
                        server.ehlo()  # Can be omitted
                        server.login(sender_email, password)
                        server.sendmail(sender_email, receiver_email, message)
                    aeval = Interpreter()
                    
                    valid = True
                    continue
                
                # the input dialog
                USER_INP = simpledialog.askstring(parent = ROOT, title="Verification",
                                        prompt="Input the 6 digit code:")
                
                if (USER_INP == code):
                    # Transaction 
                    i = 0
                    for fields in textFields:
                        userInputs[labels[i]] = fields.get()
                        i = i+1
                    response = charge_credit_card(userInputs, invoiceNumbervar, customerIDvar)
                    hashInput(userInputs)
                    messagebox.showinfo(title='STATUS', message=response['message'])

                    if (response['status']): # Pag True lang sya magcloclose
                        close_window()

                    valid = True
                
                # If the user clicks the cancel and exit button
                elif(USER_INP == None):
                    valid = True
                
                # If the user inputted the wrong code
                else: 
                    tries = tries+1
            
    #  New window for input
    window = tk.Tk()
    window.title('DONATION')
    window.geometry("300x450")
    window.iconbitmap("./images/icon.ico") #Added the window icon
    window.attributes('-topmost', 1)

    # This is need for setting up the background image
    canvas = Canvas(
        window,
        bg = "#ffffff",
        height = 450,
        width = 300,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge")
    canvas.place(x = 0, y = 0)

    # Setting up lang ito ng background image
    background_img = PhotoImage(master=window, file = f"./images/background_user_input.png")
    background = canvas.create_image(
        150.0, 225.0,
        image=background_img)
    
    textFields = []
    labels = ["Amount", "Card Number", "Exp Date","CVV", "First Name", "Last Name",
    'Company', 'Address', 'City', 'State', 'Zip', 'Country']
    for i in range(len(labels)):
            lbl_1 = tk.Label(window, text=labels[i],
                            fg='black', font=("Helvetica", 8))
            lbl_1.place(x = 30, y = 75 + i * 25)

            txtfld_1 = tk.Entry(window, bg='white', fg='black', bd=5)
            txtfld_1.place(x=115, y= 75 + i * 25)
            textFields.append(txtfld_1)

    # Confirm Button
    btn_confirm = PhotoImage(master=window, file = f"./images/btn_confirm.png")  # Undo Button
    b2 = create_norm_btn(window, new_entry, btn_confirm)
    b2.place(x = 107, y = 392, width = 92, height = 48)

    window.resizable(False, False)
    window.protocol("WM_DELETE_WINDOW", close_window)
    window.mainloop()
####################################################################################################
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
##################### Tab3 #########################################################################

canvas3 = Canvas(
    tab3,
    bg = "#ffffff",
    height = 450,
    width = 300,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge")
canvas3.place(x = 0, y = 0)

background_tab3_img = PhotoImage(master=tab3, file = f"./images/background_tab3.png")
background = canvas3.create_image(
    150.0, 225.0,
    image=background_tab3_img)

donate_img = PhotoImage(master=tab3, file = f"./images/btn_donate.png")  # Undo Button
btn_donate = create_norm_btn(tab3, user_input, donate_img)
btn_donate.place(x = 82, y = 192, width = 143, height = 81)

####################################################################################################

def get_transaction_id():
    return ''


def get_api_login_id():
    return ''


def doSomething():
    window.quit()
window.protocol('WM_DELETE_WINDOW', doSomething)


tab2_load()
window.resizable(False, False)
window.mainloop()
sys.exit()
