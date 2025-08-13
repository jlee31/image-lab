'''
This file is responsible for:

Containing image processing functions using OpenCV.

Taking input images (usually as NumPy arrays) and returning processed images.

Encapsulating specific image operations like grayscale conversion, edge detection, blurring, etc.

Keeping the image processing logic independent from the GUI.
'''
from utils.imports import * 
from utils.utils import * 
from PIL import ImageEnhance

# all functions will return an adjusted image
def adjust_brightness(image):
    print("Adjusting Brightness")
    if not check_image_loaded(image):
            return
    newImage = image.copy()
    brightness_factor = simpledialog.askfloat("Input", "Enter Brightness Factor (0.0 to 2.0)", minvalue=0.0, maxvalue=2.0)
    if brightness_factor:
        image_pil = Image.fromarray(cv.cvtColor(newImage, cv.COLOR_BGR2RGB))
        enhancer = ImageEnhance.Brightness(image_pil)
        enhanced_image = enhancer.enhance(brightness_factor)
        newImage = cv.cvtColor(np.array(enhanced_image), cv.COLOR_RGB2BGR)
    return newImage

def adjust_saturation(image):
    pass

def adjust_contrast(image):
    pass

def glitch_image(image):
    pass

def apply_glitch(image, intensity):
    pass

def apply_blur(image):
    pass

def apply_sharpen(image):
    pass

def apply_pixels(image):
    pass

def apply_invert(image):
    pass

def apply_noise(image):
    pass

def apply_vignette(image):
    pass

def apply_retro_filter(image):
    pass
