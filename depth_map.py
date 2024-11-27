from PIL import Image
import numpy as np
import cv2 as cv
import open3d as o3d
import zlib


def colour_image(val, minval, maxval, startcolour, stopcolour):
    f = float(val - minval) / (maxval - minval)
    return tuple(f*(b-a)+a for (a,b) in zip(startcolour, stopcolour))


def create_depth_map(png_path):

    # read depth chunk and get image size
    depth_data = extract_depth_chunk(png_path)
    width,height = get_png_dimensions(png_path)
    if not depth_data:
        raise ValueError("Unable to parse depth_data from PNG input.")

    # set up colouring vars
    minval, maxval = 0, 255
    RED, BLUE = (255,0,0), (0,0,255)

    # initialize depth colour
    depthColor = np.zeros((height, width, 3), dtype=np.uint8)

    for i in range(height):
        for j in range(width):
            depthColor[i][j] = colour_image(depth_data[i][j], minval, maxval, BLUE, RED)


    return depthColor


def extract_depth_chunk(file_path, chunk_type=b"dEPh"):
    """
    Extracts the custom depth data chunk from a PNG file.
    
    Args:
        file_path (str): Path to the PNG file.
        chunk_type (bytes): Type of the chunk to extract (default is b"dEPh").
    
    Returns:
        bytes: The decompressed depth data if the chunk is found.
    """
    with open(file_path, "rb") as f:
        # Validate PNG signature
        signature = f.read(8)
        if signature != b'\x89PNG\r\n\x1a\n':
            raise ValueError("Not a valid PNG file")
        
        while True:
            # Read the chunk length (4 bytes, big-endian)
            length_bytes = f.read(4)
            if len(length_bytes) < 4:
                break  # End of file
            length = int.from_bytes(length_bytes, "big")
            
            # Read the chunk type (4 bytes)
            chunk = f.read(4)
            
            # Read the chunk data and CRC (length + 4 bytes CRC)
            chunk_data = f.read(length)
            crc = f.read(4)
            
            # Check if this is the desired chunk type
            if chunk == chunk_type:
                # Decompress the depth data
                decompressed_data = zlib.decompress(chunk_data)
                depth_array_flat = list(decompressed_data)
                width, height = get_png_dimensions(file_path)
                depth_array = [depth_array_flat[i * width : (i+1) * width] for i in range(height)]
                return depth_array

    raise ValueError(f"Chunk type {chunk_type.decode('utf-8')} not found in the PNG file.")


def get_png_dimensions(file_path):
    with Image.open(file_path) as img:
        width, height = img.size
    return width, height

if __name__ == "__main__":
    png_path = "example_with_depth.png"

    output_path = "depth_map.png"

    depth_map = create_depth_map(png_path)

    cv.imshow("depth map",depth_map)
    cv.waitKey()
    cv.destroyAllWindows()


    # with open(output_path, "wb") as f:
    #     print(depth_map)

        # f.write(depth_map)
