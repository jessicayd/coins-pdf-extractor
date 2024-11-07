import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import camelot as c
import fitz  # PyMuPDF for rendering the PDF
import matplotlib.pyplot as plt
from file_handling import download_csv
from screeninfo import get_monitors

# Global Variables
values = [
    "ID", "Name", "Latitude", "Longitude", "Start_Year", "End_Year",
    "Num_Coins_Found", "Reference", "Comment", "External_Link"
]
mapping = {}
coins = []
grouping = ""
labels = {}
precise_date = False

def is_separator(row):
    index = row[0]
    if (index is None or len(index) == 0 or len(index) >= 5 or not any(char.isdigit() for char in index) or
        sum(1 for col in row if (col == "" or col == " " or col is None)) >= len(row) / 2):
        return True
    return False

def is_header(row):
    return row[0].replace("\n", " ").replace("   ", " ").replace("  ", " ") == labels[0]

def get_separator(row):
    return row.iloc[0]

def append_data(coins, tables, grouping):
    count = 0
    for table in tables:
        table = table.df
        for i, row in table.iterrows():
            if is_separator(row):
                if is_header(row):
                    continue
                grouping = get_separator(row)
                continue

            coin = {}
            count += 1
            for key, label in labels.items():
                try:
                    coin[mapping[label]] = row[key]
                except KeyError:
                    continue
            if mapping.get("grouping_label", ""):
                coin[mapping["grouping_label"]] = grouping
            coins.append(coin)
    return count

def confirm_labels(confirm_window, tables, tool):
    for i in range(9):
        header = confirm_window.children.get(str(i)).get()
        if header:
            mapping[header] = values[i]
    mapping["grouping_label"] = confirm_window.children.get("grouping_label").get()

    global precise_date
    start_date = confirm_window.children.get("4").get()
    end_date = confirm_window.children.get("5").get()

    if start_date == end_date:
        precise_date = True

    confirm_window.destroy()
    coins_added = append_data(coins, tables, grouping)
    update_tool_status(tool, coins_added)

def create_boxes(tables, tool):
    labels_list = list(labels.values())
    confirm_window = tk.Tk()
    confirm_window.title("Confirm Labels")

    for i in range(10):
        label = tk.Label(confirm_window, text=values[i])
        label.grid(row=0, column=i, padx=1)
        map_var = tk.StringVar(confirm_window)
        box = ttk.Combobox(confirm_window, values=labels_list, textvariable=map_var, state="readonly", name=str(i), width=17)
        box.grid(row=1, column=i, padx=1)

    label = tk.Label(confirm_window, text="Grouped by...")
    label.grid(row=0, column=10, padx=1)
    map_var = tk.StringVar(confirm_window)
    box = ttk.Combobox(confirm_window, values=values, textvariable=map_var, state="readonly", name="grouping_label", width=17)
    box.grid(row=1, column=10, padx=1)

    confirm_button = tk.Button(confirm_window, text="Confirm labels", command=lambda: confirm_labels(confirm_window, tables, tool))
    confirm_button.grid(row=3, column=5, sticky="NSEW")

def get_labels(table):
    table = table.df
    if len(table) > 0:
        temp_labels = table.loc[0]
        for i, label in enumerate(temp_labels):
            label = label.replace("\n", " ").replace("   ", " ").replace("  ", " ")
            labels[i] = label
        return labels

def extract(tool, mapping):
    try:
        page = 1  # Fixed page number for now, modify as needed
        if not hasattr(tool, 'file') or not tool.file:
            print("No file selected.")
            return

        file = tool.file
        area = select_area(file)
        tables = c.read_pdf(file, pages=str(page), flavor="lattice", line_scale=40, line_tol=8, table_areas=area)

        if not mapping:
            labels = get_labels(tables[0])
            create_boxes(tables, tool)
        else:
            coins_added = append_data(coins, tables, grouping)
            update_tool_status(tool, coins_added)

        c.plot(tables[0], kind="grid")
        plt.show()
    except Exception as e:
        handle_extraction_error(tool, e)

def handle_extraction_error(tool, error):
    print(f"Extraction error: {error}")
    reminder = tool.children.get("reminder")
    if reminder:
        reminder["text"] = "Remember to fit the PDF to page!"
        reminder["font"] = ('Helvetica', 9, 'bold')
    messagebox.showwarning(
        title="Oops!",
        message="Table not found. Ensure page number is correct, PDF is fit to page, and that your box is fully within the PDF."
    )

def update_tool_status(tool, coins_added):
    capture_button = tool.children.get("capture_button")
    upload_button = tool.children.get("upload_button")

    def change():
        capture_button["text"] = "Capture table"

    capture_button["text"] = f"Success! Grabbed {coins_added} coins."
    capture_button.after(1000, change)
    upload_button["text"] = "Save csv"
    upload_button["command"] = lambda: download_csv(tool)

def clear_widgets(tool):
    for widget_name in ["textbox_label", "page_textbox", "confirm_button", "reminder"]:
        widget = tool.children.get(widget_name)
        if widget:
            widget.after(2000, widget.destroy)


def on_capture_button_click(tool):
    extract(tool, mapping)
