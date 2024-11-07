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

from tkinter import Toplevel, NW
import fitz 

def select_area(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)  
    pix = page.get_pixmap()
    image_path = "page.png"
    pix.save(image_path)

    root = Toplevel()
    root.title("Select Table Area")

    img = tk.PhotoImage(file=image_path)
    root.img = img  

    canvas = tk.Canvas(root, width=img.width(), height=img.height())
    canvas.pack()
    canvas.img = img  
    canvas.create_image(0, 0, anchor=NW, image=img)  

    coords = []
    rect_id = None

    def on_click(event):
        nonlocal rect_id
        coords.clear()
        coords.append((event.x, event.y))
        if rect_id:
            canvas.delete(rect_id)
        rect_id = canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="red")
        print("Mouse click detected at:", event.x, event.y)

    def on_drag(event):
        if rect_id:
            canvas.coords(rect_id, coords[0][0], coords[0][1], event.x, event.y)

    def on_release(event):
        coords.append((event.x, event.y))
        print(f"Mouse release detected. Selected area: {coords}")
        root.quit()  # End the mainloop
        root.destroy()  # Close the window

    canvas.bind("<ButtonPress-1>", on_click)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)

    root.mainloop()

    # Return the coordinates in Camelot and bbox format
    if len(coords) == 2:
        x1, y1 = coords[0]
        x2, y2 = coords[1]
        camelot_coords = [f"{x1},{y1},{x2},{y2}"]
        bbox = (x1, y1, x2, y2)
        print("Bounding box created successfully.")
        return camelot_coords, bbox
    else:
        print("Failed to capture valid coordinates.")
        return None, None

def extract_table_with_camelot(pdf_path, table_area, output_csv_path='extracted_table.csv'):
    try:
        print(pdf_path)
        print(table_area)
        # tables = c.read_pdf(pdf_path, pages='1', flavor='stream', strip_text='\n', table_areas=table_area)
        tables = c.read_pdf(pdf_path, pages='1', flavor='lattice', line_scale=40, line_tol=8, strip_text='\n', split_text=True)
        if tables.n > 0:
            c.plot(tables[0], kind='grid')
            plt.show()
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
            table_area, bbox = select_area(tool.file)
            print(table_area)
            if table_area:
                extract_table_with_camelot(tool.file, table_area)
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
