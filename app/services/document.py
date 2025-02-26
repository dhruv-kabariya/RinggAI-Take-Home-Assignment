import json
from datetime import datetime
from typing import Optional, List, Dict
import weaviate.classes as wvc
import pymupdf
from PIL import Image
import io

from docx import Document as DocxDocument
from fastapi import UploadFile, HTTPException

from config import CHUNK_SIZE, CHUNK_OVERLAP, SUPPORTED_DOCUMENT_TYPES
from models.api import DocumentMetadata
from services.vision_service import process_all_images_async

def check_allowed_file(file_content_type: str) -> bool:
    """
    Checks if the file content type is supported for processing.

    Args:
    - file_content_type (str): The MIME type of the file.

    Returns:
    - bool: True if the file type is supported, False otherwise.
    """
    return file_content_type in SUPPORTED_DOCUMENT_TYPES.values()
   
async def process_document(docId:str ,file: UploadFile) -> tuple:
    """
    Processes an uploaded document and stores its chunks in Weaviate.

    Args:
    - docId (str): The unique identifier for the document.
    - file (UploadFile): The uploaded file to be processed.

    Returns:
    - tuple: A tuple containing the processed chunks and metadata of the document.
    """
    if file.content_type not in SUPPORTED_DOCUMENT_TYPES.values():
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Read and process the document
    content = await read_document(file)
    chunks = convert_to_chunk_and_schema(content,file.content_type,docId)
    
    # Create metadata
    metadata = DocumentMetadata(
        document_id=docId,
        file_name=file.filename,
        file_type=file.content_type,
        upload_timestamp=str(datetime.now()),
        total_chunks=len(chunks),
        additional_info={}
    )

    return (chunks,metadata)

async def read_document( file: UploadFile) -> list:
    """
    Reads content from various document formats and extracts text and images.

    Args:
    - file (UploadFile): The uploaded file to be read and processed.

    Returns:
    - list: A list of dictionaries containing extracted data, including page number, text, and images.
    """
    content = ""
    file_content = await file.read()
    extracted_data = []
    image_processing_tasks=[]
    
    if file.content_type == SUPPORTED_DOCUMENT_TYPES["pdf"]:
        # Read PDF
        doc = pymupdf.Document(stream=file_content)  # Open PDF
        
        for  page_no,page in enumerate(doc, start=1):
            print(page)
            print(page_no)
            # Extract text blocks
            text_blocks = page.get_text("blocks")
            # Each block is (x0, y0, x1, y1, "text", block_no, block_type)
            formatted_blocks = ''
            for block in text_blocks:
                if block[6] == 0:  # Text block (type 0)
                    formatted_blocks =formatted_blocks +'\n' + block[4]  # Get the text
            
            # Add text entry if there are any text blocks
            if formatted_blocks:
                extracted_data.append({
                    "page_no": str(page_no + 1),
                    "is_image": False,
                    "image": None,
                    "text": formatted_blocks
                })
            
            # Extract images
            image_list = page.get_images(full=True)
            
            # Process each image
            for img_index, img in enumerate(image_list):
                xref = img[0]  # Get the XREF of the image
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Create a PIL Image object
                image = Image.open(io.BytesIO(image_bytes))
                if image.size[0] > 250 and image.size[1] > 250:
                    # Add image entry
                    image_processing_tasks.append((image, str(page_no + 1), img_index))
            # return extracted_data
            
    elif file.content_type == SUPPORTED_DOCUMENT_TYPES["docx"]:
        # Read DOCX
        doc = DocxDocument(io.BytesIO(file_content))
        # extracted_data = []

        for i,element  in enumerate(doc.element.body):
            # Extract Text
            if element.tag.endswith('p'):  # Paragraphs
                text = element.text.strip()
                if text:
                    extracted_data.append({"page_no": i, "is_image": False, "text": text, "image": None})

            # Extract Images
            elif element.tag.endswith('graphic'):  
                for rel in doc.part.rels:
                    if "image" in doc.part.rels[rel].target_ref:
                        image_bytes = doc.part.rels[rel].target_part.blob
                        image = Image.open(io.BytesIO(image_bytes))
                        if image.size[0] > 250 and image.size[1] > 250:
                        # Extract text from image using OCR
                            image_processing_tasks.append((image, str(page_no + 1), img_index))

        # return extracted_data
        
    elif file.content_type == SUPPORTED_DOCUMENT_TYPES["json"]:
        
        # Read JSON
        try:
            json_content = json.loads(file_content)
            if isinstance(json_content,list):
                for i,d in enumerate(json_content):
                    extracted_data.append({
                        "page_no":i, 
                        "is_image": False, 
                        "text": json.dumps(d), 
                        "image": None,
                        })
            else:
                extracted_data.append({
                    "page_no": 0, 
                    "is_image": False, 
                    "text": json.dumps(json_content), 
                    "image": None
                    })
            
            # return extracted_data
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON file")
            
    elif file.content_type == SUPPORTED_DOCUMENT_TYPES["txt"]:
        # Read TXT
        content = file_content.decode("utf-8")
        extracted_data.append({
            "page_no": 0,
            "is_image": False,
            "text": content,
            "image": None
        })
    
    processed_images = []
    processed_images =await process_all_images_async(image_processing_tasks)
    
    for proc_img in processed_images:
        extracted_data.append({
            "page_no": proc_img["page_no"],
            "is_image": True,
            "image": None,
            "text": proc_img["text"],
        })
        
    extracted_data.sort(key=lambda x: (int(x["page_no"]), x["is_image"]))
    
    return extracted_data

def convert_to_chunk_and_schema(extracted_data: list,file_type:str,docId:str) -> List[Dict]:
    """
    Splits text into overlapping chunks and returns as a list of dictionaries.

    Args:
    - extracted_data (list): A list of dictionaries containing extracted data.
    - file_type (str): The type of the file.
    - docId (str): The unique identifier for the document.

    Returns:
    - List[Dict]: A list of dictionaries representing the chunks of the document.
    """
    chunks = []
    chunk_id = 0  
    
    for item in extracted_data:
        text = item["text"]
        is_image = item["is_image"]

        if text:
           
            start = 0
            while start < len(text):
                end = min(start + CHUNK_SIZE, len(text))
                chunk_text = text[start:end]
                temp_chunk = {
                    "docId":docId,
                    "pageNo": str(item["page_no"]),
                    "chunkId": str(chunk_id),
                    "chunkDataType": "image" if is_image else "text",
                    "chunkData": chunk_text,
                    "fileType": file_type
                }
                
                chunks.append(wvc.data.DataObject(properties=temp_chunk))

                chunk_id += 1
                start += CHUNK_SIZE - CHUNK_OVERLAP  # Move forward with overlap

    return chunks

