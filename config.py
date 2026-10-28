"""Configuration for the Product Pricing Analysis project."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
RAW_DATA_FILE = RAW_DATA_DIR / "synthetic_products.csv"

# Dataset generation settings. Adjust these values to change dataset size.
RANDOM_SEED = 42
NUMBER_OF_PRODUCTS = 120
COMPETITORS = ["MarketOne", "ShopSphere", "ValueCart", "PrimeRetail"]
OBSERVATION_MONTHS = [
    "2026-04-01",
    "2026-05-01",
    "2026-06-01",
    "2026-07-01",
    "2026-08-01",
    "2026-09-01",
]

# Price ranges (INR) by category; all generated records are synthetic.
CATEGORY_PRICE_RANGES = {
    "Electronics": (800, 45000),
    "Home Appliances": (700, 30000),
    "Fashion": (250, 7000),
    "Beauty & Personal Care": (100, 5000),
    "Home & Kitchen": (150, 12000),
    "Sports & Fitness": (300, 18000),
}

CATEGORY_PRODUCT_TYPES = {
    "Electronics": ["Wireless Earbuds", "Bluetooth Speaker", "Smartwatch", "Keyboard", "Power Bank", "Headphones", "Webcam", "Router"],
    "Home Appliances": ["Mixer Grinder", "Electric Kettle", "Air Cooler", "Table Fan", "Induction Cooktop", "Vacuum Cleaner", "Rice Cooker"],
    "Fashion": ["Casual Shirt", "Running Shoes", "Backpack", "Denim Jeans", "Hoodie", "Wallet", "Sports T-Shirt"],
    "Beauty & Personal Care": ["Face Moisturizer", "Shampoo", "Hair Dryer", "Sunscreen", "Beard Trimmer", "Face Wash", "Hair Serum"],
    "Home & Kitchen": ["Water Bottle", "Cookware Set", "Bedsheet Set", "Storage Rack", "Desk Lamp", "Lunch Box", "Kitchen Scale"],
    "Sports & Fitness": ["Yoga Mat", "Dumbbell Set", "Resistance Bands", "Skipping Rope", "Fitness Gloves", "Cycling Helmet", "Exercise Bench"],
}

SYNTHETIC_BRANDS = [
    "NovaNest", "UrbanPeak", "BrightForge", "AeroVale", "CoreMint", "EverTrail",
    "LumaWorks", "Oakline", "PulseCraft", "Zenora", "NorthBend", "VividRoot",
]
