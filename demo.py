import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import simpledialog
from fpdf import FPDF
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path

def get_image_paths(folder_path):
    image_extensions = {'.jpg', '.jpeg', '.png'}
    image_paths = []
    try:
        for filename in os.listdir(folder_path):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                image_paths.append(os.path.join(folder_path, filename))
        return sorted(image_paths)
    except Exception as e:
        print(f"Error retrieving image paths: {e}")
        return []

def images_to_pdf(image_paths, pdf_path):
    pdf = FPDF()
    for i, image_path in enumerate(image_paths):
        try:
            with Image.open(image_path) as image:
                img_w, img_h = image.size
                pdf.add_page()
                pdf_w = pdf.w
                pdf_h = pdf.h

                img_aspect = img_w / img_h
                pdf_aspect = pdf_w / pdf_h

                if img_aspect > pdf_aspect:
                    scaled_w = pdf_w
                    scaled_h = pdf_w / img_aspect
                else:
                    scaled_h = pdf_h
                    scaled_w = pdf_h * img_aspect

                x = (pdf_w - scaled_w) / 2
                y = (pdf_h - scaled_h) / 2

                if image.mode != 'RGB':
                    image = image.convert('RGB')

                temp_image_path = f'temp_image_{i}.jpg'
                image.save(temp_image_path)
                pdf.image(temp_image_path, x=x, y=y, w=scaled_w, h=scaled_h)
                os.remove(temp_image_path)
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")

    try:
        pdf.output(pdf_path)
    except Exception as e:
        print(f"Error saving PDF: {e}")

def encrypt_pdf(input_pdf_path, output_pdf_path, password):
    try:
        pdf_reader = PdfReader(input_pdf_path)
        pdf_writer = PdfWriter()
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
        pdf_writer.encrypt(password)
        with open(output_pdf_path, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)
    except Exception as e:
        print(f"Error encrypting PDF: {e}")

def decrypt_pdf(input_pdf_path, output_pdf_path, password):
    try:
        pdf_reader = PdfReader(input_pdf_path)
        pdf_writer = PdfWriter()
        if pdf_reader.is_encrypted:
            pdf_reader.decrypt(password)
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
        with open(output_pdf_path, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)
    except Exception as e:
        print(f"Error decrypting PDF: {e}")

def extract_images_from_pdf(pdf_path, output_folder):
    try:
        images = convert_from_path(pdf_path, poppler_path=r'C:\poppler-23.11.0\Library\bin')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        for i, image in enumerate(images):
            image_filename = os.path.join(output_folder, f'image_{i + 1}.jpg')
            image.save(image_filename, 'JPEG')
            print(f"Saved image {image_filename}")
    except Exception as e:
        print(f"Error extracting images from PDF: {e}")

class PDFApp:
    def __init__(self, root):
        self.root = root
        root.title("PDF Management App")

        # Buttons for functionality
        self.select_folder_button = tk.Button(root, text="Select Folder of Images", command=self.select_folder)
        self.select_folder_button.pack(pady=10)

        self.convert_to_pdf_button = tk.Button(root, text="Convert Images to PDF", command=self.convert_to_pdf)
        self.convert_to_pdf_button.pack(pady=10)

        self.encrypt_pdf_button = tk.Button(root, text="Encrypt PDF", command=self.encrypt_pdf)
        self.encrypt_pdf_button.pack(pady=10)

        self.decrypt_pdf_button = tk.Button(root, text="Decrypt PDF", command=self.decrypt_pdf)
        self.decrypt_pdf_button.pack(pady=10)

        self.extract_images_button = tk.Button(root, text="Extract Images from PDF", command=self.extract_images)
        self.extract_images_button.pack(pady=10)

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if not self.folder_path:
            return
        messagebox.showinfo("Selected Folder", f"Selected folder: {self.folder_path}")

    def convert_to_pdf(self):
        if not hasattr(self, 'folder_path'):
            messagebox.showerror("Error", "No folder selected")
            return
        
        pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not pdf_path:
            return

        image_paths = get_image_paths(self.folder_path)
        images_to_pdf(image_paths, pdf_path)
        messagebox.showinfo("Success", "Images have been converted to PDF")

    def encrypt_pdf(self):
        pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not pdf_path:
            return
        
        encrypted_pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not encrypted_pdf_path:
            return
        
        password = simpledialog.askstring("Password", "Enter password:")
        if not password:
            return
        
        encrypt_pdf(pdf_path, encrypted_pdf_path, password)
        messagebox.showinfo("Success", "PDF has been encrypted")

    def decrypt_pdf(self):
        encrypted_pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not encrypted_pdf_path:
            return
        
        decrypted_pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not decrypted_pdf_path:
            return
        
        password = simpledialog.askstring("Password", "Enter password:")
        if not password:
            return
        
        decrypt_pdf(encrypted_pdf_path, decrypted_pdf_path, password)
        messagebox.showinfo("Success", "PDF has been decrypted")

    def extract_images(self):
        pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not pdf_path:
            return
        
        output_folder = filedialog.askdirectory()
        if not output_folder:
            return
        
        extract_images_from_pdf(pdf_path, output_folder)
        messagebox.showinfo("Success", "Images have been extracted from the PDF")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFApp(root)
    root.mainloop()
