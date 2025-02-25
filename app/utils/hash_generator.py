import hashlib

def generate_document_id(file_name):
    """
    Generate a consistent hash (document ID) for a given file name.
    
    Args:
        file_name (str): The file name to be hashed.
    
    Returns:
        str: A unique hash ID (first 10 characters of SHA-256).
    """
    hash_object = hashlib.sha256(file_name.encode())  # Create hash from file name
    document_id = hash_object.hexdigest()[:10]  # Use first 10 characters for brevity
    return document_id
