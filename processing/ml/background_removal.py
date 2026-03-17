"""
processing/ml/background_removal.py
------------------------------------
Background removal using U2-Net via the rembg library.

Paper: Qin et al., "U2-Net: Going Deeper with Nested U-Structure for
       Salient Object Detection", Pattern Recognition, 2020.
       https://arxiv.org/abs/2005.09007

Install: pip install rembg onnxruntime

Returns a BGRA numpy array (4 channels). The alpha channel encodes
the foreground mask: 255 = foreground, 0 = removed background.
"""

import numpy as np
from PIL import Image


def remove_background(image):
    """
    Remove the background from a BGR numpy image.
    Returns a BGRA numpy array with the background set to transparent.
    """
    try:
        from rembg import remove
    except ImportError:
        raise ImportError(
            "rembg is not installed.\n"
            "Run: pip install rembg onnxruntime"
        )

    # BGR numpy -> RGB PIL
    pil_rgb = Image.fromarray(image[:, :, ::-1])

    # rembg returns an RGBA PIL image
    pil_rgba = remove(pil_rgb)

    # RGBA numpy -> BGRA numpy
    rgba = np.array(pil_rgba)
    bgra = rgba[:, :, [2, 1, 0, 3]]
    return bgra
