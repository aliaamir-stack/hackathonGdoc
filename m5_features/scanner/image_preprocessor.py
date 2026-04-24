"""
Image Preprocessor — OpenCV pipeline for medicine/pill photo optimization.

Prepares raw camera images for OCR by applying:
1. Grayscale conversion
2. Gaussian blur for noise reduction
3. Adaptive thresholding for text clarity
4. Sharpening with unsharp mask
5. Contrast enhancement via CLAHE
"""

import base64
import logging
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """
    OpenCV-based image preprocessing pipeline for medicine scanning.

    Converts raw photos into OCR-optimized images by applying
    a series of computer vision transformations.
    """

    @staticmethod
    def decode_base64_image(image_base64: str) -> Optional[np.ndarray]:
        """
        Decode a base64-encoded image string into an OpenCV numpy array.

        Args:
            image_base64: Base64-encoded image data

        Returns:
            OpenCV image array (BGR format), or None if decoding fails
        """
        try:
            image_bytes = base64.b64decode(image_base64)
            np_array = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
            if image is None:
                logger.error("Failed to decode image — invalid image data")
                return None
            logger.info(f"Image decoded: {image.shape[1]}x{image.shape[0]} pixels")
            return image
        except Exception as e:
            logger.error(f"Base64 image decoding failed: {e}")
            return None

    @staticmethod
    def to_grayscale(image: np.ndarray) -> np.ndarray:
        """Convert BGR image to grayscale."""
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def denoise(image: np.ndarray, strength: int = 10) -> np.ndarray:
        """
        Apply Non-Local Means Denoising to reduce image noise.

        Args:
            image: Grayscale input image
            strength: Denoising filter strength (higher = more denoising)

        Returns:
            Denoised grayscale image
        """
        return cv2.fastNlMeansDenoising(image, None, strength, 7, 21)

    @staticmethod
    def sharpen(image: np.ndarray) -> np.ndarray:
        """
        Apply unsharp mask sharpening to enhance text edges.

        Uses Gaussian blur + weighted addition to create sharp text edges
        that improve OCR recognition accuracy.
        """
        gaussian = cv2.GaussianBlur(image, (0, 0), 3)
        sharpened = cv2.addWeighted(image, 1.5, gaussian, -0.5, 0)
        return sharpened

    @staticmethod
    def adaptive_threshold(image: np.ndarray) -> np.ndarray:
        """
        Apply adaptive Gaussian thresholding for text extraction.

        Adaptive thresholding handles uneven lighting conditions
        that are common in mobile phone photos of medicine packaging.
        """
        return cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11,
            C=2,
        )

    @staticmethod
    def enhance_contrast(image: np.ndarray) -> np.ndarray:
        """
        Apply CLAHE (Contrast Limited Adaptive Histogram Equalization).

        CLAHE improves local contrast which is essential for reading
        embossed or printed text on pill surfaces.
        """
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(image)

    @staticmethod
    def resize_for_ocr(
        image: np.ndarray,
        target_width: int = 1200,
    ) -> np.ndarray:
        """
        Resize image to optimal width for OCR processing.

        Tesseract performs best on images ~300 DPI, which typically
        means scaling up small images or normalizing large ones.

        Args:
            image: Input image
            target_width: Desired width in pixels

        Returns:
            Resized image maintaining aspect ratio
        """
        height, width = image.shape[:2]
        if width == target_width:
            return image

        scale = target_width / width
        new_height = int(height * scale)
        interpolation = (
            cv2.INTER_CUBIC if scale > 1 else cv2.INTER_AREA
        )
        return cv2.resize(
            image, (target_width, new_height), interpolation=interpolation
        )

    def preprocess(
        self,
        image_base64: str,
        for_ocr: bool = True,
    ) -> Optional[np.ndarray]:
        """
        Run the full preprocessing pipeline on a base64-encoded image.

        Pipeline steps:
        1. Decode base64 → OpenCV array
        2. Resize to optimal OCR width
        3. Convert to grayscale
        4. Denoise
        5. Enhance contrast (CLAHE)
        6. Sharpen
        7. Optionally apply adaptive thresholding (for OCR)

        Args:
            image_base64: Base64-encoded image data
            for_ocr: If True, apply thresholding for text extraction

        Returns:
            Preprocessed image array, or None if processing fails
        """
        # Step 1: Decode
        image = self.decode_base64_image(image_base64)
        if image is None:
            return None

        try:
            # Step 2: Resize
            image = self.resize_for_ocr(image)

            # Step 3: Grayscale
            gray = self.to_grayscale(image)

            # Step 4: Denoise
            denoised = self.denoise(gray)

            # Step 5: Contrast enhancement
            enhanced = self.enhance_contrast(denoised)

            # Step 6: Sharpen
            sharpened = self.sharpen(enhanced)

            # Step 7: Optional thresholding
            if for_ocr:
                result = self.adaptive_threshold(sharpened)
            else:
                result = sharpened

            logger.info("Image preprocessing completed successfully")
            return result

        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return None

    @staticmethod
    def encode_to_base64(image: np.ndarray) -> str:
        """
        Encode an OpenCV image back to base64 string.

        Args:
            image: OpenCV image array

        Returns:
            Base64-encoded JPEG string
        """
        _, buffer = cv2.imencode(".jpg", image)
        return base64.b64encode(buffer).decode("utf-8")


# Singleton instance
image_preprocessor = ImagePreprocessor()
