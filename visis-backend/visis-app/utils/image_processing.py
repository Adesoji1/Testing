
import cv2
import numpy as np

def denoise_image(image, h=10, hForColor=10, templateWindowSize=7, searchWindowSize=21):
    """Denoise the image using Non-local Means Denoising algorithm with customizable parameters."""
    return cv2.fastNlMeansDenoisingColored(image, None, h, hForColor, templateWindowSize, searchWindowSize)

def enhance_contrast(image, clip_limit=3.0, grid_size=(8, 8)):
    """Enhance the contrast of the image using CLAHE with customizable parameters."""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=grid_size)
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

def correct_skew(image):
    """Correct the skew of the image using Hough Line Transform for more complex layouts."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
    angle = 0.0
    if lines is not None:
        for rho, theta in lines[:, 0]:
            angle += theta
        angle /= len(lines) if len(lines) else 1
        angle = np.degrees(angle) - 90
    else:
        coords = np.column_stack(np.where(gray > 0))
        angle = cv2.minAreaRect(coords)[-1]
        angle = -(90 + angle) if angle < -45 else -angle
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def remove_shadows(image, kernel_size=(7, 7), blur_strength=21):
    """Remove shadows from the image with adjustable parameters for kernel and blur size."""
    rgb_planes = cv2.split(image)
    result_planes = []
    for plane in rgb_planes:
        dilated_img = cv2.dilate(plane, np.ones(kernel_size, np.uint8))
        bg_img = cv2.medianBlur(dilated_img, blur_strength)
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        result_planes.append(norm_img)
    return cv2.merge(result_planes)

def adaptive_threshold(image, max_value=255, block_size=11, C=2):
    """Apply adaptive thresholding to improve OCR accuracy on complex backgrounds."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.adaptiveThreshold(gray, max_value, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, block_size, C)
