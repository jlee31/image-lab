"""
processing/filters/
~~~~~~~~~~~~~~~~~~~
One file per filter.  To add a new filter:
  1. Create processing/filters/my_filter.py
  2. Add its pure function to the imports below.
"""

from .brightness    import adjust_brightness_with_factor
from .contrast      import adjust_contrast_with_factor
from .saturation    import adjust_saturation_with_factor
from .blur          import apply_blur_with_radius
from .noise         import apply_noise_with_intensity
from .vignette      import apply_vignette
from .glitch        import apply_glitch
from .sharpen       import apply_sharpen
from .pixelate      import apply_pixels
from .invert        import apply_invert
from .retro         import apply_retro_filter
from .pencil        import apply_pencil
from .smart_enhance import apply_smart_enhance

__all__ = [
    "adjust_brightness_with_factor",
    "adjust_contrast_with_factor",
    "adjust_saturation_with_factor",
    "apply_blur_with_radius",
    "apply_noise_with_intensity",
    "apply_vignette",
    "apply_glitch",
    "apply_sharpen",
    "apply_pixels",
    "apply_invert",
    "apply_retro_filter",
    "apply_pencil",
    "apply_smart_enhance",
]
