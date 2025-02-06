from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_bytes
from PIL import Image
import io
import os
import sys

def get_poppler_path():
    if sys.platform.startswith('win'):
        return r'R:\\Apps\\poppler-24.08.0\\Library\\bin'
    return None

def swap_halves(pdf_bytes):
    # Convert PDF to images
    images = convert_from_bytes(pdf_bytes, poppler_path=get_poppler_path())
    output = PdfWriter()
    
    # We need all halves first to rearrange them
    all_halves = []
    for page in images:
        width, height = page.size
        half_width = width // 2
        
        # Split into halves and store them
        left_half = page.crop((0, 0, half_width, height))
        right_half = page.crop((half_width, 0, width, height))
        all_halves.extend([left_half, right_half])
    
    # Now we have all_halves = [1, 2, 3, 4]
    # We want to arrange them as [4, 1] then [2, 3]
    
    width, height = images[0].size
    half_width = width // 2
    
    # Create first page [4 1]
    page1 = Image.new('RGB', (width, height))
    page1.paste(all_halves[3], (0, 0))        # 4 on left
    page1.paste(all_halves[0], (half_width, 0))  # 1 on right
    
    # Create second page [2 3]
    page2 = Image.new('RGB', (width, height))
    page2.paste(all_halves[1], (0, 0))        # 2 on left
    page2.paste(all_halves[2], (half_width, 0))  # 3 on right
    
    # Convert both pages to PDF
    for new_page in [page1, page2]:
        img_byte_arr = io.BytesIO()
        new_page.save(img_byte_arr, format='PDF')
        img_byte_arr.seek(0)
        
        temp_reader = PdfReader(img_byte_arr)
        output.add_page(temp_reader.pages[0])
    
    output_stream = io.BytesIO()
    output.write(output_stream)
    output_stream.seek(0)
    return output_stream.getvalue()


def scale_to_portrait(pdf_bytes):
    images = convert_from_bytes(pdf_bytes, poppler_path=get_poppler_path())
    output = PdfWriter()
    
    for page in images:
        width, height = page.size
        half_width = width // 2
        
        # Split into halves
        left_half = page.crop((0, 0, half_width, height))
        right_half = page.crop((half_width, 0, width, height))
        
        # Scale each half to portrait
        for half in [left_half, right_half]:
            # Calculate scaling factor
            scale = min(width / half_width, height / half.size[1])
            new_size = (int(half_width * scale), int(half.size[1] * scale))
            scaled_half = half.resize(new_size, Image.LANCZOS)
            
            # Convert to PDF
            img_byte_arr = io.BytesIO()
            scaled_half.save(img_byte_arr, format='PDF')
            img_byte_arr.seek(0)
            
            temp_reader = PdfReader(img_byte_arr)
            output.add_page(temp_reader.pages[0])
    
    output_stream = io.BytesIO()
    output.write(output_stream)
    output_stream.seek(0)
    return output_stream.getvalue()
