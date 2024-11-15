import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import camelot as c
import matplotlib.pyplot as plt

def extract_tables_with_camelot(pdf_path, save_folder, status_label, buttons):
    try:
        # Disable buttons while processing
        for button in buttons:
            button.config(state="disabled")
        
        status_label.config(text="Processing, please wait...")
        status_label.update_idletasks()  # Ensure the label updates immediately

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
        
        print(f"Total tables found: {tables.n}")
        
        if tables.n > 0:
            output_csv_path = os.path.join(save_folder, os.path.basename(pdf_path) + "_output.csv")
            tables.export(output_csv_path, f='csv', compress=False)
            print(f"All tables extracted and saved to {output_csv_path}")
            status_label.config(text=f"Done! Tables saved to {output_csv_path}")
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
        # Re-enable buttons after processing
        for button in buttons:
            button.config(state="normal")

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
            status_label.config(text="")  # Clear status label when file is changed

    def choose_save_folder():
        folder = filedialog.askdirectory(title="Select Save Folder")
        if folder:
            save_folder.set(folder)
            folder_label.config(text=f"Save Folder: {folder}")
            status_label.config(text="")  # Clear status label when folder is changed

    def on_capture_button_click():
        if hasattr(tool, 'file') and tool.file and save_folder.get():
            # Start a new thread for extraction
            thread = threading.Thread(target=extract_tables_with_camelot, args=(tool.file, save_folder.get(), status_label, [upload_button, choose_folder_button, capture_button]))
            thread.start()
        else:
            print("No file or save folder selected.")
            messagebox.showwarning(title="Error", message="No PDF file or save folder selected.")

    upload_button = tk.Button(tool, text="Upload PDF", command=upload_file)
    choose_folder_button = tk.Button(tool, text="Choose Save Folder", command=choose_save_folder)
    capture_button = tk.Button(tool, text="Capture Table", state="disabled", command=on_capture_button_click)

    # Labels with left-aligned text
    file_label = tk.Label(tool, text="No file selected.", wraplength=400, justify="left", anchor="w")
    folder_label = tk.Label(tool, text="No save folder selected.", wraplength=400, justify="left", anchor="w")
    status_label = tk.Label(tool, text="", wraplength=400, justify="left", anchor="w")

    # Configure grid to make the window responsive
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
