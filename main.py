# import tkinter as tk
# from file_handling import upload_file
# from capture import on_capture_button_click
# from tkinter import filedialog

# if __name__ == "__main__":
#     tool = tk.Tk()
#     tool.title("COINS Tool")

#     upload_button = tk.Button(tool, text="Upload PDF", name='upload_button', command=lambda: upload_file(capture_button, tool))
#     capture_button = tk.Button(tool, text="Capture table", name="capture_button", command=lambda: on_capture_button_click(tool))

#     tk.Grid.columnconfigure(tool, 0, weight=1)
#     tk.Grid.columnconfigure(tool, 1, weight=1)
#     tk.Grid.rowconfigure(tool, 0, weight=1)

#     upload_button.grid(row=0, column=0, sticky="NSEW", columnspan=2)

#     tool.mainloop()

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import camelot as c
import matplotlib.pyplot as plt
from pdf2image import convert_from_path
from PIL import Image

from tkinter import Toplevel, NW
import fitz 

def extract_table_with_camelot(pdf_path, output_csv_path='extracted_table.csv'):
    try:
        print(pdf_path)
        tables = c.read_pdf(pdf_path, pages='1', flavor='lattice', line_scale=40, line_tol=8, strip_text='\n', split_text=True)
        print(tables.n)
        if tables.n > 0:
            for i, table in enumerate(tables):
                c.plot(table, kind='grid')
                plt.show()

                c.plot(table, kind="contour")
                plt.show()
                print(table.parsing_report)
            tables.export(output_csv_path, f='csv', compress=False)
            print(f"Table(s) extracted and saved as {output_csv_path}")
        else:
            print("No tables found in the specified area.")
    except Exception as e:
        print(f"Extraction error: {e}")
        messagebox.showwarning(
            title="Oops!",
            message="Table not found. Ensure that your bounding box is correct."
        )


def main():
    tool = tk.Tk()
    tool.title("PDF Table Extractor")

    def upload_file():
        pdf_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF files", "*.pdf")])
        if pdf_path:
            tool.file = pdf_path
            print(f"File selected: {pdf_path}")
            capture_button.config(state="normal")

    def on_capture_button_click():
        if hasattr(tool, 'file') and tool.file:
            extract_table_with_camelot(tool.file)
        else:
            print("No file selected.")
            messagebox.showwarning(title="Error", message="No PDF file selected.")

    upload_button = tk.Button(tool, text="Upload PDF", command=upload_file)
    capture_button = tk.Button(tool, text="Capture Table", state="disabled", command=on_capture_button_click)

    upload_button.grid(row=0, column=0, padx=10, pady=10)
    capture_button.grid(row=0, column=1, padx=10, pady=10)

    tool.mainloop()

if __name__ == "__main__":
    main()
