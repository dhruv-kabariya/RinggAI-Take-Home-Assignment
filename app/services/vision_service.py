import io
import aiohttp

import asyncio

from config import AZURE_VISION_ENDPOINT,AZURE_VISION_KEY


AZURE_HEADERS = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': AZURE_VISION_KEY
}

async def azure_ocr(session,image):
    """Extract text from an image using Azure Computer Vision OCR"""
    try:
        # Convert PIL image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # API endpoint for OCR
        vision_url = f"{AZURE_VISION_ENDPOINT}vision/v3.2/ocr"
        
        # Parameters for the API request
        params = {
            'language': 'en',
            'detectOrientation': 'true'
        }
        
        # Send POST request to Azure
        async with session.post(
            vision_url,
            headers=AZURE_HEADERS,
            params=params,
            data=img_byte_arr
        ) as response:
            if response.status == 200:
                result = await response.json()
                
                # Extract and combine text from the response
                text = ""
                for region in result.get("regions", []):
                    for line in region.get("lines", []):
                        line_text = " ".join([word.get("text", "") for word in line.get("words", [])])
                        text += line_text + "\n"
                
                return text.strip()
            else:
                print(f"Azure OCR Error: {response.status}, {await response.text()}")
                return f"OCR Error: {response.status}"
    
    except Exception as e:
        print(f"Azure OCR processing error: {e}")
        return "OCR processing error"

async def azure_image_caption(session,image):
    """Generate a caption for an image using Azure Computer Vision"""
    try:
        # Convert PIL image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # API endpoint for image analysis
        vision_url = f"{AZURE_VISION_ENDPOINT}vision/v3.2/analyze"
        
        # Parameters for the API request - include description feature
        params = {
            'visualFeatures': 'Description',
            'language': 'en'
        }
        
        # Send POST request to Azure
        async with session.post(
            vision_url,
            headers=AZURE_HEADERS,
            params=params,
            data=img_byte_arr
        ) as response:
            if response.status == 200:
                result = await response.json()
                
                # Extract caption
                captions = result.get("description", {}).get("captions", [])
                if captions:
                    # Get the highest confidence caption
                    caption = max(captions, key=lambda x: x.get("confidence", 0))
                    return caption.get("text", "No caption generated")
                else:
                    return "No caption generated"
            else:
                print(f"Azure Caption Error: {response.status}, {await response.text()}")
                return f"Caption Error: {response.status}"
    
    except Exception as e:
        print(f"Azure caption generation error: {e}")
        return "Caption generation error"

async def process_image(session,image_data):
    """Process a single image with both OCR and captioning in parallel"""
    image, page_no, img_index = image_data
    
    # Create a copy of the image for processing
    img_copy = image.copy()
    
    ocr_task = azure_ocr(session,img_copy)
    caption_task = azure_image_caption(session, img_copy)
    
    ocr_text, caption = await asyncio.gather(ocr_task, caption_task)
    return {
        "page_no": page_no,
        "image_index": img_index,
        "text": f"The Image Contain Text : {ocr_text}\nDescription of Image : {caption}",
        "image": None
    }

async def process_all_images_async(image_processing_tasks):
    """Process all images using async"""
    processed_images = []
    
    # Create a ClientSession that will be used for all requests
    async with aiohttp.ClientSession() as session:
        # Create a task for each image
        tasks = [process_image(session, task) for task in image_processing_tasks]
        
        # Process images concurrently and gather results
        processed_images = await asyncio.gather(*tasks)
    
    return processed_images

