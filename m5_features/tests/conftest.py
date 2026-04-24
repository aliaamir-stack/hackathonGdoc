"""
Pytest conftest — Shared fixtures for M5 feature tests.

Provides reusable test fixtures for scanner, emergency,
and Telegram alert test suites.
"""

import pytest
import numpy as np
import base64


@pytest.fixture
def sample_image_base64():
    """Generate a sample base64-encoded test image."""
    # Create a simple 100x100 white image with some text-like features
    image = np.ones((100, 100, 3), dtype=np.uint8) * 255
    # Add some dark pixels to simulate text
    image[20:30, 10:90] = 0  # Horizontal line
    image[40:50, 20:80] = 50  # Another line

    import cv2
    _, buffer = cv2.imencode(".jpg", image)
    return base64.b64encode(buffer).decode("utf-8")


@pytest.fixture
def sample_medications():
    """Common medication list for interaction testing."""
    return ["aspirin", "metformin", "lisinopril"]


@pytest.fixture
def emergency_texts():
    """Sample emergency descriptions for protocol matching."""
    return {
        "cpr": "someone is not breathing and has no pulse",
        "choking": "a person is choking on a piece of food",
        "stroke": "sudden face drooping and slurred speech",
        "heart_attack": "severe crushing chest pain",
        "seizure": "person having a seizure on the floor",
        "burns": "child burned by hot water",
        "bleeding": "deep cut with severe bleeding",
        "poisoning": "child swallowed cleaning chemicals",
        "allergic": "severe allergic reaction with throat swelling",
        "electric": "person touched a live wire",
    }


@pytest.fixture
def karachi_coords():
    """Karachi city center GPS coordinates."""
    return {"latitude": 24.8607, "longitude": 67.0011}


@pytest.fixture
def lahore_coords():
    """Lahore city center GPS coordinates."""
    return {"latitude": 31.5204, "longitude": 74.3587}
