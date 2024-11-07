from tkinter import filedialog
import tkinter as tk

def upload_file(capture_button, tool):
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
    if file_path:
        tool.file = file_path

        # Optionally clear or reset mappings here
        mapping = {}

        tk.Grid.rowconfigure(tool, 1, weight=1)
        capture_button.grid(row=1, column=0, sticky="NSEW", columnspan=2)


def download_csv(tool):
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    try:
        global coins, mapping, grouping, labels, precise_date

        df = pd.DataFrame(coins)
        if precise_date:
            df["Start_Year"] = df["End_Year"]   

            cols = df.columns.tolist()
            start_year_col = cols.pop()
            cols.insert(1, start_year_col)

            df = df[cols]     

        df.to_csv(save_path, index=False, header=True, encoding="utf_8_sig")
        download_button = tool.children.get("upload_button")
        capture_button = tool.children.get("capture_button")
        download_button["text"] = "Upload"
        download_button["command"] = lambda: upload_file(capture_button, tool)

        # Reset global variables
        mapping = {}
        coins = []
        grouping = ""
        labels = {}
        precise_date = False

    except Exception as e:
        tk.messagebox.showerror("Save Error", f"Error: {e}")