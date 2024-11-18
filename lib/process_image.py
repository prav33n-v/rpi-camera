"""
This file contains AI generated code to process image for getting output with specific effects similar to a filter.
The functions were generated using ChatGPT and minor changes have been made to make it work with this program.
"""
import numpy as np
from PIL import Image,ImageEnhance

def sepia(image):
    # Convert to grayscale if it's not already in grayscale (this handles black-and-white images)
    img = image.convert('L')  # Convert to grayscale (if not already)
    # Convert image to numpy array (shape will be (height, width, 3) in RGB mode)
    img_np = np.array(img.convert('RGB'))
    # Apply the sepia filter (multiply matrix)
    # The sepia filter matrix for RGB
    sepia_filter = np.array([[0.393, 0.769, 0.189],
                             [0.349, 0.686, 0.168],
                             [0.272, 0.534, 0.131]])
    # Apply the sepia effect: Dot product of image RGB channels with the sepia filter matrix
    sepia_img = img_np @ sepia_filter.T
    # Clip the values to be in the range [0, 255] since RGB values are bounded in this range
    sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
    # Convert back to Image object from numpy array
    sepia_img_pil = Image.fromarray(sepia_img)
    # Return the resulting image
    return sepia_img_pil

def infrared_to_bnw_vintage(image):
    # Ensure the image is in RGB mode
    img = image.convert('RGB')
    # Convert the image to a NumPy array (height, width, 3) - RGB format
    img_np = np.array(img)
    # Convert the image to grayscale using the standard luminosity method
    # We can use a weighted sum to convert to grayscale:
    # Luminosity formula: 0.299*R + 0.587*G + 0.114*B
    grayscale_np = np.dot(img_np[...,:3], [0.299, 0.587, 0.114])
    # Normalize the grayscale image (optional step to improve contrast)
    # In the vintage look, we want the contrast to be more pronounced.
    grayscale_np = np.clip(grayscale_np * 1.2, 0, 255)
    # Simulate the Fujifilm Croma vintage film look by manipulating channels
    # Let's simulate a slight increase in red to give the warm, reddish tones
    img_np = img_np.astype(np.float32)  # Convert to float32 for precision
    # Increase red and reduce blue for the "vintage" feel
    img_np[..., 0] = img_np[..., 0] * 1.05  # Boost red channel slightly
    img_np[..., 1] = img_np[..., 1] * 1.0   # Keep green channel as is
    img_np[..., 2] = img_np[..., 2] * 0.95  # Slightly reduce blue channel
    # Clip the values to ensure they are within valid range [0, 255]
    img_np = np.clip(img_np, 0, 255)
    # Convert the image back to uint8 type and create the final image
    vintage_img = Image.fromarray(img_np.astype(np.uint8))
    # Convert to grayscale using the adjusted luminance
    final_bnw = Image.fromarray(grayscale_np.astype(np.uint8))
    # Return the grayscale vintage image
    return final_bnw

def technicolor(image):
    # Convert the image to RGB if it's not already
    img = image.convert('RGB')
    # Convert the image to a NumPy array for processing
    image_array = np.array(img)
    # Apply Technicolor-style color grading:
    # 1. Enhance the red channel (Technicolor films often have a prominent red)
    image_array[..., 0] = np.clip(image_array[..., 0] * 1.25, 0, 255)  # Boost red channel
    # 2. Enhance the green channel to make the overall image pop
    image_array[..., 1] = np.clip(image_array[..., 1] * 1.15, 0, 255)  # Slight boost to green
    # 3. Enhance the blue channel to create rich color depth
    image_array[..., 2] = np.clip(image_array[..., 2] * 1.10, 0, 255)  # Boost blue channel
    # Increase overall contrast (Technicolor films are known for high contrast)
    image_array = np.clip(image_array * 1.25, 0, 255)
    # Convert back to a PIL image from NumPy array
    technicolor_image = Image.fromarray(image_array.astype(np.uint8))
    # Enhance color saturation for more vibrancy (Technicolor films have intense colors)
    enhancer = ImageEnhance.Color(technicolor_image)
    technicolor_image = enhancer.enhance(1.8)  # Boost color saturation significantly
    # Return the final Technicolor-style image
    return technicolor_image
