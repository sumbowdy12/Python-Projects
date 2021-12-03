# Tkinter Party Guest App
# Author: Boris Le
# Date: 12/2/2021
import tkinter
from tkinter import messagebox
import random
main_window = tkinter.Tk()
guestCount = 0

#Function to count one guest
def count_one_guest():
    global guestCount
    global output_field
    
    guestCount += 1
    output_field.config(text=guestCount)
    
#Function to count five guest
def count_five_guest():
    global guestCount
    global output_field
    
    guestCount += 5
    output_field.config(text=guestCount)

#Function to decrease by one guest
def decrement_one_guest():
    global guestCount
    global output_field
    
    guestCount -= 1
    output_field.config(text=guestCount)
  
#Function to clear Guests  
def clearGuests():
    global guestCount
    global output_field
    
    if tkinter.messagebox.askyesno(title="Guest Counter", message="Are you sure you want to clear?"):
        guestCount = 0
        output_field.config(text=guestCount)

#Generate random number and display messagebox if winner        
def wonPrize():
    N = int(spin_box.get())
    rand_int = random.randrange(1,N+1)
    
    if rand_int == N:
        tkinter.messagebox.showinfo("Prize Winner", "You won a prize!")
        

#Tkinter GUI design

main_window.title("Party Guest Counter")
main_window.geometry('400x300')

frame = tkinter.Frame(main_window)
frame.grid()

spin_box = tkinter.Spinbox(
    from_=1,
    to=100,
    wrap=True)
spin_box.grid(row=5, column=0, columnspan=2)

output_label = tkinter.Label(frame, text="Guest count: ", font=('sans-serif', 18, 'bold'))
output_label.grid(row=0, column=1)

output_field = tkinter.Label(frame, text=guestCount, font=('sans-serif', 18, 'bold'))
output_field.grid(row=0, column=2)

plus_one = tkinter.Button(frame, text="+1", command=count_one_guest)
plus_one.grid(row=1, column=0, columnspan=2)

plus_five = tkinter.Button(frame, text="+5", command=count_five_guest)
plus_five.grid(row=2, column=0, columnspan=2)

minus_one = tkinter.Button(frame, text="-1", command=decrement_one_guest)
minus_one.grid(row=3, column=0, columnspan=2)

clear_guests = tkinter.Button(frame, text="Clear Guests", command=clearGuests)
clear_guests.grid(row=4, column=0, columnspan=2)

rollPrize = tkinter.Button(frame, text="Roll For Prize", command=wonPrize)
rollPrize.grid(row=5, column=0, columnspan=2)


#Associated functions with keys
def keyPressed(event):
    event_desc = event.char
    if event.keysym == "Return": #Decrease by one when return button is pressed
        decrement_one_guest()
    elif event.keysym == "space": #Clear guests if space button is pressed
        clearGuests()
    elif event.keysym == "a": #Increase by one if a is pressed
        count_one_guest()
    elif event.keysym == "b": #Increase by five if b is pressed
        count_five_guest()

#Bind keys

frame.bind_all("a", keyPressed)
frame.bind_all("b", keyPressed)
frame.bind_all("<Return>", keyPressed)
frame.bind_all("<space>", keyPressed)

frame.mainloop()