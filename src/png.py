import struct
import zlib
from typing import Tuple, Optional
from PIL import Image
import numpy as np

def add_text_chunk_to_file(key: str, value: str, output_filename: str) -> None:
    """Add a text chunk to a PNG file and save to a new file."""
    # Verify the PNG is valid by trying to open it
    Image.open(self.filename).verify()

    # Read original file
    with open(self.filename, 'rb') as f:
        data = f.read()

    # Create buffer for new file
    buffer = bytearray()

    # Write original content up to IEND chunk
    buffer.extend(data[:-12])  # Skip IEND chunk

    # Create tEXt chunk
    key_value = f"{key}\0{value}".encode('latin-1')
    length = len(key_value)
    
    # Write length (4 bytes, big-endian)
    buffer.extend(struct.pack('>I', length))
    
    # Write chunk type
    buffer.extend(b'tEXt')
    
    # Write the key-value data
    buffer.extend(key_value)
    
    # Calculate and write CRC
    crc = zlib.crc32(b'tEXt' + key_value) & 0xFFFFFFFF
    buffer.extend(struct.pack('>I', crc))

    # Write original IEND chunk
    buffer.extend(data[-12:])

    # Write to output file
    with open(output_filename, 'wb') as f:
        f.write(buffer)

    print(f"Metadata added and image saved as {output_filename}")

def add_text_chunk_to_data(key: str, value: str, output_filename: str) -> None:
    """Add a text chunk to image data and save to a new file."""
    buffer = bytearray()

    # Write original content up to IEND chunk
    buffer.extend(self.image_bytes[:-12])

    # Create tEXt chunk
    key_value = f"{key}\0{value}".encode('latin-1')
    length = len(key_value)
    
    # Write length
    buffer.extend(struct.pack('>I', length))
    
    # Write chunk type
    buffer.extend(b'tEXt')
    
    # Write the key-value data
    buffer.extend(key_value)
    
    # Calculate and write CRC
    crc = zlib.crc32(b'tEXt' + key_value) & 0xFFFFFFFF
    buffer.extend(struct.pack('>I', crc))

    # Write original IEND chunk
    buffer.extend(self.image_bytes[-12:])

    # Write to output file
    with open(output_filename, 'wb') as f:
        f.write(buffer)

    print(f"Metadata added and image saved as {output_filename}")

def read_all_metadata(image:bytearray) -> None:
    """Read and print all metadata chunks from the PNG file."""
    i = 0

    png_header = image[i:i+8]
    i += 8

    if png_header != b'\x89PNG\r\n\x1a\n':
        raise ValueError("File passed is not a PNG")
    
    while True:
        try:
            length_bytes = image[i:i+4]
            if not length_bytes:
                break
            length = struct.unpack(">I", length_bytes)[0]
            i += 4
            chunk_type = image[i:i+4]
            i += 4
            chunk_data = image[i:i+length]
            i += length
            crc = image[i:i+4]
            i += 4
            # Process metadata chunks
            if chunk_type in [b'tEXt', b'zTXt', b'iTXt']:
                print(f"{chunk_type.decode()} chunk: Metadata: {chunk_data}")

            if chunk_type == b'IEND':
                break
        except Exception as e:
            print(f"Error {e}")

    # with open(self.filename, 'rb') as f:
    #     # Verify PNG signature
    #     png_header = f.read(8)
    #     if png_header != b'\x89PNG\r\n\x1a\n':
    #         raise ValueError("File is not a valid PNG")

    #     # Read chunks
    #     while True:
    #         try:
    #             # Read chunk length
    #             length_bytes = f.read(4)
    #             if not length_bytes:
    #                 break
    #             length = struct.unpack('>I', length_bytes)[0]

    #             # Read chunk type
    #             chunk_type = f.read(4)
                
    #             # Read chunk data
    #             chunk_data = f.read(length)
                
    #             # Read CRC
    #             crc = f.read(4)

    #             # Process metadata chunks
    #             if chunk_type in [b'tEXt', b'zTXt', b'iTXt']:
    #                 print(f"{chunk_type.decode()} chunk: Metadata: {chunk_data}")

    #             if chunk_type == b'IEND':
    #                 break

    #         except struct.error:
    #             break

def find_signature_metadata(image:bytearray) -> Optional[str]:
    """Find and return signature metadata if present."""
    i = 0

    png_header = image[i:i+8]
    i += 8

    if png_header != b'\x89PNG\r\n\x1a\n':
        raise ValueError("File passed is not a PNG")
    
    while True:
        try:
            length_bytes = image[i:i+4]
            if not length_bytes:
                break
            length = struct.unpack(">I", length_bytes)[0]
            i += 4
            chunk_type = image[i:i+4]
            i += 4
            chunk_data = image[i:i+length]
            i += length
            crc = image[i:i+4]
            i += 4
            # Process metadata chunks
            if chunk_type == b'tEXt':
                try:
                    metadata = chunk_data.decode('latin-1')
                    if metadata.startswith('Signature\0'):
                        return metadata[len('Signature\0'):]
                except UnicodeDecodeError:
                    continue

            if chunk_type == b'IEND':
                break
        except Exception as e:
            print(f"Error {e}")

    # with open(self.filename, 'rb') as f:
    #     # Verify PNG signature
    #     png_header = f.read(8)
    #     if png_header != b'\x89PNG\r\n\x1a\n':
    #         raise ValueError("File is not a valid PNG")

    #     while True:
    #         try:
    #             length_bytes = f.read(4)
    #             if not length_bytes:
    #                 break
    #             length = struct.unpack('>I', length_bytes)[0]

    #             chunk_type = f.read(4)
    #             chunk_data = f.read(length)
    #             crc = f.read(4)

    #             if chunk_type == b'tEXt':
    #                 try:
    #                     metadata = chunk_data.decode('latin-1')
    #                     if metadata.startswith('Signature\0'):
    #                         return metadata[len('Signature\0'):]
    #                 except UnicodeDecodeError:
    #                     continue

    #             if chunk_type == b'IEND':
    #                 break

    #         except struct.error:
    #             break

    return None

def flatten_image(self) -> Tuple[bytes, Tuple[int, int]]:
    """Flatten image to raw RGBA bytes."""
    # Open and convert image to RGBA
    with Image.open(self.filename) as img:
        rgba_img = img.convert('RGBA')
        
        # Convert to numpy array for faster processing
        pixel_data = np.array(rgba_img)
        
        # Flatten the array and ensure it's in RGBA order
        flattened = pixel_data.tobytes()
        
        return flattened, rgba_img.size