import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import camelot as c
import pandas as pd

# Define the custom columns
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
def extract_tables_with_camelot(pdf_path, save_folder, status_label, buttons, tool):
    try:
        for button in buttons:
            button.config(state="disabled")
        
        status_label.config(text="Processing, please wait...")
        status_label.update_idletasks()

        print(f"Processing PDF: {pdf_path}")
        
        tables = c.read_pdf(
            pdf_path, 
            pages='all',
            flavor='lattice',
            line_scale=40,
            line_tol=8,
            strip_text='\n',
            split_text=True
        )
        
        if tables.n > 0:
            for i, table in enumerate(tables):
                print(f"Processing Table {i+1}")
                df = table.df
                df.columns = df.iloc[0]
                df = df[1:].reset_index(drop=True)
                df = handle_category_rows(df)

                complete = threading.Event()

                def close_mapping():
                    complete.set()

                create_mapping_window(df, tool, save_folder, pdf_path, table_num=i+1, close_callback=close_mapping)
                complete.wait()
                
            status_label.config(text="Mapping complete for all tables.")
        else:
            print("No tables found in the PDF.")
            status_label.config(text="No tables found in the PDF.")
    except Exception as e:
        print(f"Extraction error: {e}")
        status_label.config(text="Failed to extract tables.")
        messagebox.showwarning(
            title="Oops!",
            message="Failed to extract tables. Check the PDF or input parameters."
        )
    finally:
        for button in buttons:
            button.config(state="normal")

def handle_category_rows(df):
    """
    Detects rows that span all columns and treats them as category rows.
    Adds a 'Category' column to the DataFrame, assigning each row the last detected category.
    """
    df.replace(r'^\s*$', None, regex=True, inplace=True)

    category = None
    category_col = []
    rows_to_drop = [] 

    for index, row in df.iterrows():
        non_null_cells = row.dropna()
        if non_null_cells.shape[0] == 1:
            category = non_null_cells.values[0]
            category_col.append(None)
            print(f"Detected category row at index {index}: '{category}'")
            rows_to_drop.append(index)
        else:
            category_col.append(category)

    df["Category"] = category_col
    df.drop(index=rows_to_drop, inplace=True)
    return df

def create_mapping_window(df, tool, save_folder, pdf_path, table_num, close_callback):
    confirm_window = tk.Toplevel(tool)
    confirm_window.title(f"Column Mapping for Table {table_num}")

    labels_list = list(df.columns)
    mappings = {}

    for i, custom_col in enumerate(values):
        label = tk.Label(confirm_window, text=custom_col)
        label.grid(row=i, column=0, padx=5, pady=5, sticky="w")

        map_var = tk.StringVar(confirm_window)
        box = ttk.Combobox(confirm_window, values=labels_list, textvariable=map_var, state="readonly", width=30)
        box.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        mappings[custom_col] = map_var

    def confirm_mappings():
        new_data = {}
        for custom_col, map_var in mappings.items():
            selected_col = map_var.get()
            if selected_col:
                new_data[custom_col] = df[selected_col]
            else:
                new_data[custom_col] = None

        mapped_df = pd.DataFrame(new_data)
        print(f"New Mapped DataFrame:\n{mapped_df}")

        save_mapped_df(mapped_df, save_folder, pdf_path, table_num)
        confirm_window.destroy()

        if close_callback:
            close_callback()

    confirm_button = tk.Button(confirm_window, text="Confirm Mappings", command=confirm_mappings)
    confirm_button.grid(row=len(values), column=0, columnspan=2, pady=10)

def save_mapped_df(df, save_folder, pdf_path, table_index):
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_csv_path = os.path.join(save_folder, f"{pdf_name}_table{table_index}.csv")

    df.to_csv(output_csv_path, index=False)
    print(f"Mapped DataFrame saved to {output_csv_path}")
    messagebox.showinfo("Success", f"Mapped DataFrame saved to {output_csv_path}")


def main():
    tool = tk.Tk()
    tool.title("PDF Table Extractor")

    save_folder = tk.StringVar()

    def upload_file():
        pdf_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF files", "*.pdf")])
        if pdf_path:
            tool.file = pdf_path
            file_label.config(text=pdf_path)
            capture_button.config(state="normal")
            status_label.config(text="")

    def choose_save_folder():
        folder = filedialog.askdirectory(title="Select Save Folder")
        if folder:
            save_folder.set(folder)
            folder_label.config(text=f"Save Folder: {folder}")
            status_label.config(text="")

    def on_capture_button_click():
        if hasattr(tool, 'file') and tool.file and save_folder.get():
            thread = threading.Thread(target=extract_tables_with_camelot, args=(tool.file, save_folder.get(), status_label, [upload_button, choose_folder_button, capture_button], tool))
            thread.start()
        else:
            print("No file or save folder selected.")
            messagebox.showwarning(title="Error", message="No PDF file or save folder selected.")

    upload_button = tk.Button(tool, text="Upload PDF", command=upload_file)
    choose_folder_button = tk.Button(tool, text="Choose Save Folder", command=choose_save_folder)
    capture_button = tk.Button(tool, text="Capture Table", state="disabled", command=on_capture_button_click)

    file_label = tk.Label(tool, text="No file selected.", justify="left", anchor="w")
    folder_label = tk.Label(tool, text="No save folder selected.", justify="left", anchor="w")
    status_label = tk.Label(tool, text="", justify="left", anchor="w")

    tool.grid_columnconfigure(0, weight=1)
    tool.grid_columnconfigure(1, weight=1)
    tool.grid_columnconfigure(2, weight=1)
    tool.grid_rowconfigure(1, weight=1)
    tool.grid_rowconfigure(2, weight=1)
    tool.grid_rowconfigure(3, weight=1)

    upload_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    choose_folder_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
    capture_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
    file_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
    folder_label.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
    status_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

    tool.mainloop()

if __name__ == "__main__":
    main()