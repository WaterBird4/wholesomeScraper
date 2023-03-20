import tkinter as tk

# create tkinter window
window = tk.Tk()

def handle_keypress(event):
	"""Print the character associated with keypress"""
	print(event.char)

# Bind keypress event to handle_keypress()
window.bind("<Key>", handle_keypress)

window.mainloop()

