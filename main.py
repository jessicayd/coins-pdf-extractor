import camelot as c
import pytesseract as tes
import tkinter as tk
from tkinter import filedialog
import fitz  # PyMuPDF
from screeninfo import get_monitors
import regex as re

# Set up Tesseract OCR path (adjust as needed)
tes.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

# Initialize global variables
values = [
    "ID",
    "Name",
    "Latitude",
    "Longitude",
    "Start_Year",
    "End_Year",
    "Num_Coins_Found",
    "Reference",
    "Comment",
    "External_Link"
    ]

mapping = {}
coins = []
grouping = ""
labels = {}
precise_date = False

def draw(event, canvas):
    global tlx, tly
    tlx = event.x
    tly = event.y
    canvas.create_oval(tlx-2, tly-2, tlx+2, tly+2, fill="Black")

def extract(tool, mapping):
    pass

def end_draw(event, transparent, canvas, tool, mapping):
    global brx, bry
    brx = event.x
    bry = event.y

    capture_button = tool.children.get("capture_button")
    
    confirm_button = tk.Button(tool, text="Confirm", name="confirm_button", command=lambda: extract(tool, mapping))
    
    page_textbox = tk.Text(tool, name="page_textbox", width=3, height=1)
    textbox_label = tk.Label(tool, text="Page #", name="textbox_label")

    canvas.create_rectangle(tlx, tly, brx, bry, outline="black", width=5)

    # page = get_page_number()

    tk.Grid.rowconfigure(tool, 2, weight=1)
    textbox_label.grid(row=2, column=0, sticky="SNEW")
    page_textbox.grid(row=2, column=1, sticky="SNEW")

    if not re.search(r'\d+', page_textbox.get("1.0", tk.END)): # if empty
        page_textbox.insert("1.0", str(page))

    capture_button.config(text="Redraw?")
    transparent.after(1000, transparent.destroy)

    tk.Grid.rowconfigure(tool, 3, weight=1)
    confirm_button.grid(row=3, column=0, sticky="SNEW", columnspan=2)

    reminder = tk.Label(tool, text="Remember to fit the PDF to page!", name="reminder", font=('Helvetica', 9, 'bold'))
    reminder.grid(row=4, column=0)

def upload_file(capture_button, tool):
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
    if file_path:
        global file
        file = file_path

        mapping = {}

        tk.Grid.rowconfigure(tool, 1, weight=1)
        capture_button.grid(row=1, column=0, sticky="NSEW", columnspan=2)

def on_capture_button_click(tool, mapping):
    transparent = tk.Tk()
    transparent.overrideredirect(True)

    screen_width = transparent.winfo_screenwidth()
    screen_height = transparent.winfo_screenheight()
    transparent.geometry(f"{screen_width}x{screen_height}+0+0")
    
    canvas = tk.Canvas(transparent)
    canvas.pack(fill=tk.BOTH, expand=True)

    capture_button = tool.children.get("capture_button")
    capture_button.config(text="...")

    transparent.attributes("-alpha", 0.5)

    canvas.bind("<ButtonPress-1>", lambda event: draw(event, canvas))
    canvas.bind("<ButtonRelease-1>", lambda event: end_draw(event, transparent, canvas, tool, mapping))

def main_loop():
    tool = tk.Tk()
    tool.title("COINS Tool")

    upload_button = tk.Button(tool, text="Upload PDF", name='upload_button', command=lambda: upload_file(capture_button, tool))
    capture_button = tk.Button(tool, text="Capture table", name="capture_button", command=lambda: on_capture_button_click(tool, mapping))

    tk.Grid.columnconfigure(tool, 0, weight=1)
    tk.Grid.columnconfigure(tool, 1, weight=1)
    tk.Grid.rowconfigure(tool, 0, weight=1)

    upload_button.grid(row=0, column=0, sticky="NSEW", columnspan=2)

    tool.mainloop()


# Run the function to open PDF and select bounding box
if __name__ == "__main__":
    print("hi")
    main_loop()
