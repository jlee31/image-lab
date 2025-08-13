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
    print("Adjusting Saturation")
    if not check_image_loaded(image):
            return
    newImage = image.copy()
    saturation_factor = simpledialog.askfloat("Input", "Enter Saturation Factor (0.0 to 2.0)", minvalue=0.0, maxvalue=2.0)
    if saturation_factor:
        image_pil = Image.fromarray(cv.cvtColor(newImage, cv.COLOR_BGR2RGB))
        enhancer = ImageEnhance.Color(image_pil)
        enhanced_image = enhancer.enhance(saturation_factor)
        new_image = cv.cvtColor(np.array(enhanced_image), cv.COLOR_RGB2BGR)
    return new_image

def adjust_contrast(image):
    print("Adjusting Contrast")
    if not check_image_loaded(image):
            return
    newImage = image.copy()
    saturation_factor = simpledialog.askfloat("Input", "Enter Contrast Factor (0.0 to 2.0)", minvalue=0.0, maxvalue=2.0)
    if saturation_factor:
        image_pil = Image.fromarray(cv.cvtColor(newImage, cv.COLOR_BGR2RGB))
        enhancer = ImageEnhance.Contrast(image_pil)
        enhanced_image = enhancer.enhance(saturation_factor)
        new_image = cv.cvtColor(np.array(enhanced_image), cv.COLOR_RGB2BGR)
    return new_image

def apply_glitch(image):
    print("Adding a glitch")
    if not check_image_loaded(image):
            return
    newImage = image.copy()
    glitch_factor = simpledialog.askinteger("Input", "Enter Glitch Intensity (1 - 50)", minvalue=1, maxvalue=50)
    height, width, _ = newImage.shape
    for i in range(glitch_factor):
         offset = np.random.randint(-10, 11, size=3)
         slice_height = np.random.randint(height // 20, height // 5)
         start_row = np.random.randint(0, height - slice_height)
         newImage[start_row:start_row+slice_height] = np.roll(newImage[start_row:start_row+slice_height], offset, axis = 1)
    return newImage

def apply_blur(image):
    print("Apply Blur")
    if not check_image_loaded(image):
            return
    newImage = image.copy()
    blur_factor = simpledialog.askfloat("Input", "Enter Blur Factor (1 to 10)", minvalue=1, maxvalue=10)
    if blur_factor:
        image_pil = Image.fromarray(cv.cvtColor(newImage, cv.COLOR_BGR2RGB))
        blurred_image = image_pil.filter(ImageFilter.GaussianBlur(radius=blur_factor))
        newImage = cv.cvtColor(np.array(blurred_image), cv.COLOR_RGB2BGR)
    return newImage

def apply_sharpen(image):
    print("Apply sharpen")
    if not check_image_loaded(image):
            return
    newImage = image.copy()
    image_pil = Image.fromarray(cv.cvtColor(newImage, cv.COLOR_BGR2RGB))
    sharpened_image = image_pil.filter(ImageFilter.SHARPEN)
    newImage = cv.cvtColor(np.array(sharpened_image), cv.COLOR_RGB2BGR)
    messagebox.showinfo("Success", "Sharpened Applied")
    return newImage

def apply_pixels(image):
    print("Applying Invert")
    if not check_image_loaded(image):
            return
    newImage = image.copy()
    pixel_factor = simpledialog.askfloat("Input", "Enter Pixel Factor (From 2 to 50)", minvalue=2, maxvalue=50)
    if pixel_factor:
        height, width = newImage.shape[:2]
        small = cv.resize(newImage, (width // pixel_factor, height // pixel_factor), interpolation=cv.INTER_LINEAR)
        newImage = cv.resize(small, (width, height), interpolation=cv.INTER_NEAREST)
    return newImage    


def apply_invert(image):
    print("Applying Invert")
    if not check_image_loaded(image):
            return
    newImage = image.copy()
    return cv.bitwise_not(newImage)

def apply_noise(image):
    print("Applying Noise")
    if not check_image_loaded(image):
            return
    newImage = image.copy()
    noise_factor = simpledialog.askfloat("Input", "Enter Noise Factor (From 0 to 1)", minvalue=0.0, maxvalue=1.0)
    if noise_factor is not None:
        noise = np.random.randint(0,noise_factor, newImage.shape, dtype=np.uint8)
        newImage = cv.add(newImage, noise)
    messagebox.showinfo("Success", "Noise Applied")
    return newImage

def apply_vignette(image):
    if not check_image_loaded(image):
            return
    newImage = image.copy()

def apply_retro_filter(image):
    if not check_image_loaded(image):
            return
    newImage = image.copy()

