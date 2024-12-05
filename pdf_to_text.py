import pytesseract
from pdf2image import convert_from_path
import fitz  # PyMuPDF
import os
import pdfplumber

def image_to_text_pdf(input_pdf_path, output_pdf_path):
    """
    Converts an image-based PDF to a searchable text-based PDF using OCR.

    Args:
        input_pdf_path (str): Path to the input image-based PDF.
        output_pdf_path (str): Path to save the text-based PDF.

    Returns:
        None
    """
    try:
        # Convert PDF to high-quality images
        print("Converting PDF to images...")
        images = convert_from_path(input_pdf_path, dpi=600)  # High DPI for better quality

        # Temporary directory for storing intermediate PDFs
        temp_dir = "temp_pages"
        os.makedirs(temp_dir, exist_ok=True)

        # Store individual text-based PDF pages
        pdf_pages = []

        for i, image in enumerate(images):
            print(f"Processing page {i + 1}/{len(images)}...")

            # Save image as PNG to preserve quality
            temp_image_path = os.path.join(temp_dir, f"page_{i + 1}.png")
            image.save(temp_image_path, format="PNG")

            # Perform OCR and generate a PDF
            temp_pdf_path = os.path.join(temp_dir, f"text_page_{i + 1}.pdf")
            with open(temp_pdf_path, "wb") as f:
                pdf_bytes = pytesseract.image_to_pdf_or_hocr(
                    temp_image_path, extension="pdf", lang="eng"
                )
                f.write(pdf_bytes)

            # Add the page to the list
            pdf_pages.append(temp_pdf_path)

        # Merge all text-based PDF pages into a single PDF
        merge_pdfs(pdf_pages, output_pdf_path)
        print(f"Text-based PDF created at: {output_pdf_path}")

        # Cleanup temporary files
        for file in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, file))
        os.rmdir(temp_dir)

    except Exception as e:
        print(f"An error occurred: {e}")


def merge_pdfs(pdf_paths, output_pdf_path):
    """
    Merges multiple PDF files into a single PDF.

    Args:
        pdf_paths (list): List of paths to individual PDF files.
        output_pdf_path (str): Path to save the merged PDF.

    Returns:
        None
    """
    pdf_writer = fitz.open()

    for pdf_path in pdf_paths:
        pdf_reader = fitz.open(pdf_path)
        for page in pdf_reader:
            pdf_writer.insert_pdf(pdf_reader)

    pdf_writer.save(output_pdf_path)
    pdf_writer.close()


def verify_pdf_with_pdfplumber(output_pdf_path):
    """
    Verifies the OCR output PDF with pdfplumber.

    Args:
        output_pdf_path (str): Path to the OCR-generated PDF.

    Returns:
        None
    """

    with pdfplumber.open(output_pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            print(f"Page {i + 1} text:\n{text}")
            if not text.strip():
                print(f"Warning: Page {i + 1} contains no readable text.")

        print("Verification complete.")


if __name__ == "__main__":
    # Input PDF path
    input_pdf = "input2.pdf"  # Replace with your image-based PDF
    # Output PDF path
    output_pdf = "output2.pdf"

    # Ensure input file exists
    if not os.path.exists(input_pdf):
        print(f"Error: File {input_pdf} does not exist.")
    else:
        image_to_text_pdf(input_pdf, output_pdf)
        verify_pdf_with_pdfplumber(output_pdf)