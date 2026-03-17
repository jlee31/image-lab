'''
This file is responsible for:
 
Containing image processing functions using OpenCV.
 
Taking input images (usually as NumPy arrays) and returning processed images.
 
Encapsulating specific image operations like grayscale conversion, edge detection, blurring, etc.
 
Keeping the image processing logic independent from the GUI.
'''
from utils.imports import (
    cv,
    np,
    Image,
    ImageEnhance,
    ImageFilter,
    messagebox,
)
from utils.utils import check_image_loaded
from utils.customMessageBox import ctk_get_value


def _ensure_image_copy(image):
    """Return a mutable copy of the image or None if not loaded."""
    if not check_image_loaded(image):
        return None
    return image.copy()


def adjust_brightness_with_factor(image, brightness_factor: float):
    """Adjust brightness using a provided factor (non-interactive helper)."""
    new_image = _ensure_image_copy(image)
    if new_image is None:
        return image
    image_pil = Image.fromarray(cv.cvtColor(new_image, cv.COLOR_BGR2RGB))
    enhancer = ImageEnhance.Brightness(image_pil)
    enhanced_image = enhancer.enhance(brightness_factor)
    return cv.cvtColor(np.array(enhanced_image), cv.COLOR_RGB2BGR)


def adjust_saturation_with_factor(image, saturation_factor: float):
    """Adjust saturation using a provided factor (non-interactive helper)."""
    new_image = _ensure_image_copy(image)
    if new_image is None:
        return image
    image_pil = Image.fromarray(cv.cvtColor(new_image, cv.COLOR_BGR2RGB))
    enhancer = ImageEnhance.Color(image_pil)
    enhanced_image = enhancer.enhance(saturation_factor)
    return cv.cvtColor(np.array(enhanced_image), cv.COLOR_RGB2BGR)


def adjust_contrast_with_factor(image, contrast_factor: float):
    """Adjust contrast using a provided factor (non-interactive helper)."""
    new_image = _ensure_image_copy(image)
    if new_image is None:
        return image
    image_pil = Image.fromarray(cv.cvtColor(new_image, cv.COLOR_BGR2RGB))
    enhancer = ImageEnhance.Contrast(image_pil)
    enhanced_image = enhancer.enhance(contrast_factor)
    return cv.cvtColor(np.array(enhanced_image), cv.COLOR_RGB2BGR)


# all functions will return an adjusted image
def adjust_brightness(image):
    print("Adjusting Brightness")
    if not check_image_loaded(image):
            return
    newImage = image.copy()
    # brightness_factor = simpledialog.askfloat("Input", "Enter Brightness Factor (0.0 to 2.0)", minvalue=0.0, maxvalue=2.0)
    brightness_factor = ctk_get_value(input="Enter Brightness Factor (0.0 to 2.0)",minvalue=0.0, maxvalue=2.0, type=float)
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
    # saturation_factor = simpledialog.askfloat("Input", "Enter Saturation Factor (0.0 to 2.0)", minvalue=0.0, maxvalue=2.0)
    saturation_factor = ctk_get_value(input="Enter Saturation Factor (0.0 to 2.0)",minvalue=0.0, maxvalue=2.0, type=float)
    if saturation_factor:
        image_pil = Image.fromarray(cv.cvtColor(newImage, cv.COLOR_BGR2RGB))
        enhancer = ImageEnhance.Color(image_pil)
        enhanced_image = enhancer.enhance(saturation_factor)
        newImage = cv.cvtColor(np.array(enhanced_image), cv.COLOR_RGB2BGR)
    return newImage

def adjust_contrast(image):
    print("Adjusting Contrast")
    if not check_image_loaded(image):
            return
    newImage = image.copy()
    # saturation_factor = simpledialog.askfloat("Input", "Enter Contrast Factor (0.0 to 2.0)", minvalue=0.0, maxvalue=2.0)
    contrast_factor = ctk_get_value(input="Enter Contrast Factor (0.0 to 2.0)",minvalue=0.0, maxvalue=2.0, type=float)
    if contrast_factor:
        image_pil = Image.fromarray(cv.cvtColor(newImage, cv.COLOR_BGR2RGB))
        enhancer = ImageEnhance.Contrast(image_pil)
        enhanced_image = enhancer.enhance(contrast_factor)
        newImage = cv.cvtColor(np.array(enhanced_image), cv.COLOR_RGB2BGR)
    return newImage

def apply_glitch(image):
    print("Adding a glitch")
    if not check_image_loaded(image):
            return
    newImage = image.copy()
    # glitch_factor = simpledialog.askinteger("Input", "Enter Glitch Intensity (1 - 50)", minvalue=1, maxvalue=50)
    glitch_factor = ctk_get_value(input="Enter Glitch Intensity (1 - 50)",minvalue=1, maxvalue=50, type=int)
    if not glitch_factor:
        return newImage
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
    blur_factor = ctk_get_value(input="Enter Blur Factor (1 to 10)",minvalue=1, maxvalue=10, type=int)
    if blur_factor:
        newImage = apply_blur_with_radius(newImage, blur_factor)
    return newImage


def apply_blur_with_radius(image, blur_radius: float):
    """Apply Gaussian blur with a provided radius (non-interactive helper)."""
    new_image = _ensure_image_copy(image)
    if new_image is None:
        return image
    image_pil = Image.fromarray(cv.cvtColor(new_image, cv.COLOR_BGR2RGB))
    blurred_image = image_pil.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    return cv.cvtColor(np.array(blurred_image), cv.COLOR_RGB2BGR)

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
    # pixel_factor = simpledialog.askfloat("Input", "Enter Pixel Factor (From 2 to 50)", minvalue=2, maxvalue=50)
    pixel_factor = ctk_get_value(input="Enter Pixel Factor (From 2 to 50)", minvalue=2, maxvalue=50, type=int)
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
    noise_factor = ctk_get_value(input="Enter Noise Factor (From 0 to 1)", minvalue=0.0, maxvalue=1.0, type=float)
    if noise_factor is not None:
        newImage = apply_noise_with_intensity(newImage, noise_factor)
        messagebox.showinfo("Success", "Noise Applied")
    return newImage


def apply_noise_with_intensity(image, noise_factor: float):
    """Apply noise using a provided intensity factor (non-interactive helper)."""
    new_image = _ensure_image_copy(image)
    if new_image is None:
        return image
    clamped = max(0.0, min(noise_factor, 1.0))
    max_noise = int(max(1, clamped * 50))
    noise = np.random.randint(0, max_noise + 1, new_image.shape, dtype=np.uint8)
    return cv.add(new_image, noise)

def apply_vignette(image):
    if not check_image_loaded(image):
            return
    newImage = image.copy()
    # vignette_intensity = simpledialog.askfloat("Input", "Enter Vignette Intensity (0.0 to 1.0)", minvalue=0.0, maxvalue=1.0)
    vignette_intensity = ctk_get_value(input="Enter Vignette Intensity (0.0 to 1.0)", minvalue=0.0, maxvalue=1.0, type=float)
    if vignette_intensity:
          rows, cols = newImage.shape[:2]
          kernel_x = cv.getGaussianKernel(cols, cols / 2)
          kernel_y = cv.getGaussianKernel(rows, rows / 2)
          kernel = kernel_y * kernel_x.T
          mask = 255 * kernel / ( 1 - vignette_intensity)
          mask = mask * vignette_intensity + (1 - vignette_intensity)
          newImage = newImage * mask[:,:,np.newaxis]
          newImage = np.clip(newImage, 0, 255).astype(np.uint8)
    return newImage

def apply_retro_filter(image):
    if not check_image_loaded(image):
            return
    newImage = image.copy()
    image_pil = Image.fromarray(cv.cvtColor(newImage, cv.COLOR_BGR2RGB))
    r,g,b = image_pil.split()
    r = r.point(lambda i: i * 1.3)
    b = b.point(lambda i: i * 0.8)
    image_pil = Image.merge('RGB', (r,g,b))
    enhancer = ImageEnhance.Contrast(image_pil)
    image_pil = enhancer.enhance(1.2)
    newImage = cv.cvtColor(np.array(image_pil), cv.COLOR_RGB2BGR)
    return newImage


def apply_smart_enhance(image):
    """
    Human-tuned enhancement preset:
    gentle contrast & saturation boost, light sharpening.
    """
    if not check_image_loaded(image):
            return
    enhanced = image.copy()
    # Slight contrast lift
    enhanced = adjust_contrast_with_factor(enhanced, 1.1)
    # Slight saturation lift
    enhanced = adjust_saturation_with_factor(enhanced, 1.05)
    # Light sharpen
    enhanced_pil = Image.fromarray(cv.cvtColor(enhanced, cv.COLOR_BGR2RGB))
    enhanced_pil = enhanced_pil.filter(ImageFilter.SHARPEN)
    enhanced = cv.cvtColor(np.array(enhanced_pil), cv.COLOR_RGB2BGR)
    return enhanced

def apply_pencil(image):
    if not check_image_loaded(image):
            return
    newImage = image.copy()
    gray = cv.cvtColor(newImage, cv.COLOR_BGR2GRAY)
    inverted = cv.bitwise_not(gray)
    blurred = cv.GaussianBlur(inverted, (21,21), sigmaX=0, sigmaY=0)
    inverted_blur = cv.bitwise_not(blurred)
    sketch = cv.divide(gray, inverted_blur, scale = 256)
    return cv.cvtColor(sketch, cv.COLOR_GRAY2BGR)


