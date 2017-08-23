#!/usr/bin/python

# import tkinter as tk


# counter = 0 
# def counter_label(label):
#   counter = 0
#   def count():
#     global counter
#     counter += 1
#     label.config(text=str(counter))
#     label.after(1000, count)
#   count()
 
 
# root = tk.Tk()
# root.title("Counting Seconds")
# label = tk.Label(root, fg="dark green")
# label.pack()
# counter_label(label)
# buttonForward = tk.Button(root, text='Forward', width=25, command=root.destroy)
# buttonForward.pack()
# buttonBackward = tk.Button(root, text='Backward', width=25, command=root.destroy)
# buttonBackward.pack()
# root.mainloop()

from Tkinter import *


count = 0

def counting():
	global count
	count = count+1
	print(count)

r = 0
# for c in colours:
    # Label(text=c, relief=RIDGE,width=15).grid(row=r,column=0)
    # Entry(bg=c, relief=SUNKEN,width=10).grid(row=r,column=1)
    # r = r + 1


Label(text="", width=30, height=4).grid(row=0,column=0)

Label(text="Move", width=15, height=4).grid(row=1,column=1)
Button(text='Forward', width=10, command=counting, height=4).grid(row=2,column=1)
Button(text='Backward', width=10, command=counting, height=4).grid(row=3,column=1)
Button(text='STOP', width=10, command=counting, height=4).grid(row=5,column=1)


Label(text="", width=15, height=4).grid(row=5,column=2)

Label(text="Change Speed", width=15, height=4).grid(row=1,column=3)
Button(text='Fast', width=10, command=counting, height=4).grid(row=2,column=3)
Button(text='Medium', width=10, command=counting, height=4).grid(row=3,column=3)
Button(text='Slow', width=10, command=counting, height=4).grid(row=4,column=3)
Button(text='Crawl', width=10, command=counting, height=4).grid(row=5,column=3)


Label(text="", width=15, height=4).grid(row=6,column=4)

Label(text="Change Colour", width=15, height=4).grid(row=1,column=5)
Button(text='Red', width=10, command=counting, height=4).grid(row=2,column=5)
Button(text='Green', width=10, command=counting, height=4).grid(row=3,column=5)
Button(text='Blue', width=10, command=counting, height=4).grid(row=4,column=5)

Label(text="", width=15, height=4).grid(row=6,column=6)

mainloop()


# root = Tk()
# frame = Frame(root)
# frame.pack()

# bottomframe = Frame(root)
# bottomframe.pack( side = RIGHT )

# redbutton = Button(frame, text="Red", fg="red").grid(row=0,column=0)
# # redbutton.pack( side = LEFT)

# greenbutton = Button(frame, text="Brown", fg="brown").grid(row=0,column=1)
# # greenbutton.pack( side = LEFT )

# bluebutton = Button(frame, text="Blue", fg="blue").grid(row=0,column=2)
# # bluebutton.pack( side = LEFT )

# blackbutton = Button(bottomframe, text="Black", fg="black").grid(row=0,column=3)
# # blackbutton.pack( side = LEFT)

# root.mainloop()