import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import os
import threading

class PDFToTextConverter:
    def __init__(self, master):
        self.master = master
        master.title("PDF to Text Converter")
        master.geometry("800x700")

        # --- Configuration ---
        # IMPORTANT: Set the path to your Tesseract executable here!
        # Example: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.tesseract_cmd_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

        self.pdf_path = ""
        self.extracted_text = ""

        # --- GUI Elements ---
        self.create_widgets()

    def create_widgets(self):
        # Frame for buttons
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=10)

        self.select_pdf_button = tk.Button(button_frame, text="Select PDF", command=self.select_pdf)
        self.select_pdf_button.pack(side=tk.LEFT, padx=5)

        self.save_text_button = tk.Button(button_frame, text="Save Text to File", command=self.save_text_to_file, state=tk.DISABLED)
        self.save_text_button.pack(side=tk.LEFT, padx=5)

        # PDF Path Display
        self.pdf_path_label = tk.Label(self.master, text="No PDF selected", wraplength=700)
        self.pdf_path_label.pack(pady=5)

        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.master, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

        # Text Output Area
        self.text_output = tk.Text(self.master, wrap=tk.WORD, state=tk.DISABLED)
        self.text_output.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Scrollbar for Text Output
        scrollbar = tk.Scrollbar(self.text_output)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_output.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text_output.yview)

    def select_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select a PDF file",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
        )
        if file_path:
            self.pdf_path = file_path
            self.pdf_path_label.config(text=f"Selected PDF: {os.path.basename(file_path)}")
            self.save_text_button.config(state=tk.DISABLED)
            self.text_output.config(state=tk.NORMAL)
            self.text_output.delete(1.0, tk.END)
            self.text_output.insert(tk.END, "Processing PDF... Please wait.\n")
            self.text_output.config(state=tk.DISABLED)
            self.progress_var.set(0)
            
            # Run conversion in a separate thread to keep GUI responsive
            threading.Thread(target=self._perform_conversion).start()

    def _perform_conversion(self):
        try:
            if not self.tesseract_cmd_path or not os.path.exists(self.tesseract_cmd_path):
                messagebox.showerror("Tesseract Error", "Tesseract executable path is not set or invalid.\nPlease set it in the script or ensure Tesseract is in your system PATH.")
                self._reset_gui_after_error()
                return

            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd_path
            self.extracted_text = self.extract_text_from_pdf(self.pdf_path)
            self.master.after(0, self._update_gui_after_conversion) # Update GUI on main thread
        except Exception as e:
            messagebox.showerror("Conversion Error", f"An error occurred during conversion: {e}")
            self.master.after(0, self._reset_gui_after_error)

    def _update_gui_after_conversion(self):
        self.text_output.config(state=tk.NORMAL)
        self.text_output.delete(1.0, tk.END)
        self.text_output.insert(tk.END, self.extracted_text)
        self.text_output.config(state=tk.DISABLED)
        self.save_text_button.config(state=tk.NORMAL)
        self.progress_var.set(100) # Ensure progress bar is full

    def _reset_gui_after_error(self):
        self.pdf_path_label.config(text="No PDF selected")
        self.text_output.config(state=tk.NORMAL)
        self.text_output.delete(1.0, tk.END)
        self.text_output.config(state=tk.DISABLED)
        self.save_text_button.config(state=tk.DISABLED)
        self.progress_var.set(0)

    def extract_text_from_pdf(self, pdf_path):
        text_content = []
        try:
            doc = fitz.open(pdf_path)
            total_pages = doc.page_count
            
            for i, page in enumerate(doc):
                self.master.after(0, self.progress_var.set, (i + 1) / total_pages * 100) # Update progress bar
                
                # Try direct text extraction first
                page_text = page.get_text()
                
                # If little or no text is extracted, assume it's scanned and use OCR
                if len(page_text.strip()) < 50: # Arbitrary threshold, can be adjusted
                    try:
                        # Render page to image
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # 2x zoom for higher resolution
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        ocr_text = pytesseract.image_to_string(img, lang='eng') # 'eng' for English, add other langs if needed
                        text_content.append(ocr_text)
                    except Exception as ocr_e:
                        text_content.append(f"\n[OCR Error on Page {i+1}: {ocr_e}]\n")
                else:
                    text_content.append(page_text)
                
            doc.close()
        except Exception as e:
            raise Exception(f"Failed to process PDF: {e}")
        
        return "\n".join(text_content)

    def save_text_to_file(self):
        if self.extracted_text:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
                title="Save extracted text as"
            )
            if file_path:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(self.extracted_text)
                    messagebox.showinfo("Success", "Text saved successfully!")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Failed to save text: {e}")
        else:
            messagebox.showwarning("No Text", "No text has been extracted yet.")

def main():
    root = tk.Tk()
    app = PDFToTextConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
