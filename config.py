import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.environ.get('SECRET_KEY', 'civicshield-dev-secret-key-change-in-production-2026')
    DATABASE_PATH = os.path.join(BASE_DIR, os.environ.get('DATABASE_PATH', 'civicshield.db'))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, os.environ.get('UPLOAD_FOLDER', 'static/uploads'))
    KEYFRAME_FOLDER = os.path.join(BASE_DIR, 'static/uploads/keyframes')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 64 * 1024 * 1024)) # 64 MB (supports up to 50MB videos)
    MAX_VIDEO_CONTENT_LENGTH = int(os.environ.get('MAX_VIDEO_CONTENT_LENGTH', 50 * 1024 * 1024)) # 50 MB
    MAX_VIDEO_DURATION_SECONDS = int(os.environ.get('MAX_VIDEO_DURATION_SECONDS', 60)) # 60 seconds
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov', 'm4v'}
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'mp4', 'webm', 'mov', 'm4v'}
    
    # Feature Toggles
    ENABLE_AI_CLASSIFICATION = os.environ.get('ENABLE_AI_CLASSIFICATION', 'True').lower() == 'true'
    ENABLE_IMAGE_AUTHENTICITY = os.environ.get('ENABLE_IMAGE_AUTHENTICITY', 'True').lower() == 'true'
    ENABLE_VIDEO_ANALYSIS = os.environ.get('ENABLE_VIDEO_ANALYSIS', 'True').lower() == 'true'
    AUTHENTICITY_MODEL_NAME = "CivicShield Forensic AI Engine v2.4 (EXIF + FFT/Laplacian Quality + Frame-Consistency + ELA + Perceptual Hasher)"
    OTP_DEV_MODE = os.environ.get('OTP_DEV_MODE', 'True').lower() == 'true'
    OTP_DEV_CODE = os.environ.get('OTP_DEV_CODE', '123456')
    
    # Supported Civic Categories
    CATEGORIES = [
        "Potholes and Damaged Roads",
        "Garbage Accumulation",
        "Drainage Blockage",
        "Water Leakage",
        "Broken Streetlights",
        "Exposed Electrical Wires",
        "Damaged Footpaths",
        "Overflowing Public Bins",
        "Waterlogging and Flooding",
        "Public Property Damage",
        "Other Civic Issues"
    ]
    
    # Standard Departments
    DEPARTMENTS = [
        {
            "code": "ROADS",
            "name": "Roads and Engineering",
            "categories": ["Potholes and Damaged Roads", "Damaged Footpaths", "Public Property Damage"]
        },
        {
            "code": "SANITATION",
            "name": "Sanitation and Waste Management",
            "categories": ["Garbage Accumulation", "Overflowing Public Bins"]
        },
        {
            "code": "WATER",
            "name": "Water Supply Department",
            "categories": ["Water Leakage"]
        },
        {
            "code": "DRAINAGE",
            "name": "Drainage and Sewerage",
            "categories": ["Drainage Blockage", "Waterlogging and Flooding"]
        },
        {
            "code": "ELECTRICITY",
            "name": "Electricity and Street Lighting",
            "categories": ["Broken Streetlights", "Exposed Electrical Wires"]
        },
        {
            "code": "PUBLIC_WORKS",
            "name": "Public Works & Urban Infrastructure",
            "categories": ["Public Property Damage", "Other Civic Issues"]
        }
    ]

    # SLA Rules (in hours)
    SLA_RULES = {
        "Critical": {"ack_hours": 2, "resolve_hours": 24},
        "High": {"ack_hours": 6, "resolve_hours": 48},
        "Medium": {"ack_hours": 12, "resolve_hours": 72},
        "Low": {"ack_hours": 24, "resolve_hours": 120}
    }
