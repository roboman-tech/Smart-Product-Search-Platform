"""
Seed the catalog with realistic tech products and matched product images.

Usage:
    python manage.py seed_catalog            # upsert / add missing items
    python manage.py seed_catalog --clear    # wipe existing data first
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.products.models import (
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductImage,
    ProductTag,
)


# ─── Image helper ────────────────────────────────────────────────────────────
# loremflickr returns real Flickr photos filtered by keyword.
# `lock` keeps the image stable across requests (same keyword+lock → same photo).
# Multiple `lock` values per product give gallery variety.

def _img(keyword: str, lock: int) -> str:
    """Return a keyword-matched placeholder image URL (800×800)."""
    safe = keyword.replace(" ", ",")
    return f"https://loremflickr.com/800/800/{safe}?lock={lock}"


# ─── Catalog structure ───────────────────────────────────────────────────────

CATEGORIES = [
    # (name, slug, parent_slug)
    ("Electronics",       "electronics",      None),
    ("Audio",             "audio",            "electronics"),
    ("Computers",         "computers",        "electronics"),
    ("Gaming",            "gaming",           "electronics"),
    ("Smartphones",       "smartphones",      "electronics"),
    ("Cameras",           "cameras",          "electronics"),
    ("Monitors",          "monitors",         "electronics"),
    ("Storage",           "storage",          "electronics"),
    ("Networking",        "networking",       "electronics"),
    ("Accessories",       "accessories",      None),
    ("Keyboards & Mice",  "keyboards-mice",   "accessories"),
    ("Cables & Adapters", "cables-adapters",  "accessories"),
    ("Wearables",         "wearables",        "electronics"),
]

BRANDS = [
    # (name, slug)
    ("Apple",           "apple"),
    ("Samsung",         "samsung"),
    ("Sony",            "sony"),
    ("Bose",            "bose"),
    ("Logitech",        "logitech"),
    ("Razer",           "razer"),
    ("SteelSeries",     "steelseries"),
    ("HyperX",          "hyperx"),
    ("Corsair",         "corsair"),
    ("Dell",            "dell"),
    ("LG",              "lg"),
    ("ASUS",            "asus"),
    ("Anker",           "anker"),
    ("JBL",             "jbl"),
    ("Sennheiser",      "sennheiser"),
    ("Microsoft",       "microsoft"),
    ("Western Digital", "western-digital"),
    ("Seagate",         "seagate"),
    ("Kingston",        "kingston"),
    ("GoPro",           "gopro"),
    ("TP-Link",         "tp-link"),
]

# ─── Products ────────────────────────────────────────────────────────────────
# img_kw  → loremflickr keyword (what the image should depict)
# img_lk  → base lock number (unique per product; +1 / +2 give gallery shots)

PRODUCTS = [

    # ── Over-ear Headphones ─────────────────────────────────────────────────
    {
        "name": "Sony WH-1000XM5 Wireless Headphones",
        "short": "Industry-leading noise cancellation with crystal-clear audio.",
        "desc": "The WH-1000XM5 sets the bar for premium noise-cancelling headphones. Eight microphones and two processors deliver unparalleled quiet. Multipoint connection lets you stay linked to two Bluetooth devices simultaneously.",
        "cat": "audio", "brand": "sony",
        "price": "349.99", "discount": "279.99",
        "rating": "4.8", "reviews": 5842, "stock": 45, "pop": 970,
        "tags": ["wireless", "noise-cancelling", "bluetooth", "premium"],
        "attrs": [("Connectivity", "Bluetooth 5.2"), ("Battery Life", "30 hours"), ("Noise Cancellation", "Yes"), ("Weight", "250 g"), ("Driver Size", "30 mm")],
        "img_kw": "headphones", "img_lk": 10,
    },
    {
        "name": "Bose QuietComfort 45 Headphones",
        "short": "Comfortable all-day noise cancellation with lifelike audio.",
        "desc": "QuietComfort 45 delivers balanced audio that's rich, detailed and non-fatiguing. The TriPort acoustic architecture creates a deep, immersive soundstage with a transparency Aware mode for ambient sound.",
        "cat": "audio", "brand": "bose",
        "price": "329.00", "discount": "249.00",
        "rating": "4.7", "reviews": 4210, "stock": 30, "pop": 940,
        "tags": ["wireless", "noise-cancelling", "comfortable", "bluetooth"],
        "attrs": [("Connectivity", "Bluetooth 5.1"), ("Battery Life", "24 hours"), ("Noise Cancellation", "Yes"), ("Weight", "238 g")],
        "img_kw": "headphones", "img_lk": 20,
    },
    {
        "name": "Sennheiser Momentum 4 Wireless",
        "short": "60-hour battery with audiophile-grade sound quality.",
        "desc": "The Momentum 4 Wireless features adaptive noise cancellation and is tuned by Sennheiser's acoustic engineers. 60-hour battery life keeps music playing all week.",
        "cat": "audio", "brand": "sennheiser",
        "price": "349.95", "discount": "299.95",
        "rating": "4.6", "reviews": 2130, "stock": 28, "pop": 870,
        "tags": ["wireless", "noise-cancelling", "audiophile", "bluetooth"],
        "attrs": [("Connectivity", "Bluetooth 5.2"), ("Battery Life", "60 hours"), ("Noise Cancellation", "Adaptive"), ("Weight", "293 g")],
        "img_kw": "headphones", "img_lk": 30,
    },
    {
        "name": "Sony WH-CH520 Wireless Headphones",
        "short": "Lightweight everyday headphones with 50-hour battery.",
        "desc": "Lightweight and comfortable with 50-hour battery life and multipoint connection for two devices. Perfect for daily commuting and work calls.",
        "cat": "audio", "brand": "sony",
        "price": "59.99", "discount": None,
        "rating": "4.4", "reviews": 3710, "stock": 120, "pop": 850,
        "tags": ["wireless", "bluetooth", "lightweight", "budget"],
        "attrs": [("Connectivity", "Bluetooth 5.2"), ("Battery Life", "50 hours"), ("Foldable", "Yes"), ("Weight", "147 g")],
        "img_kw": "headphones", "img_lk": 40,
    },
    {
        "name": "Sennheiser HD 660S2 Open-Back Headphones",
        "short": "Reference-grade open-back headphones for audiophiles.",
        "desc": "The HD 660S2 delivers neutral, natural sound reproduction with an improved bass response. The open-back design creates a wide soundstage perfect for critical listening and studio monitoring.",
        "cat": "audio", "brand": "sennheiser",
        "price": "599.95", "discount": None,
        "rating": "4.8", "reviews": 890, "stock": 15, "pop": 720,
        "tags": ["wired", "audiophile", "studio", "open-back"],
        "attrs": [("Impedance", "300 Ω"), ("Frequency Response", "8–41,500 Hz"), ("Type", "Open-back"), ("Cable Length", "3 m")],
        "img_kw": "headphones", "img_lk": 50,
    },
    {
        "name": "Anker Soundcore Q45 Wireless",
        "short": "Multi-mode noise cancellation at an unbeatable price.",
        "desc": "Soundcore Q45 offers four dedicated listening modes and Hi-Res Audio certification. BassUp technology dynamically boosts bass in real time.",
        "cat": "audio", "brand": "anker",
        "price": "79.99", "discount": "59.99",
        "rating": "4.3", "reviews": 6500, "stock": 200, "pop": 800,
        "tags": ["wireless", "noise-cancelling", "budget", "bluetooth"],
        "attrs": [("Battery Life", "50 hours"), ("Noise Cancellation", "4 modes"), ("Hi-Res Audio", "Yes"), ("Weight", "260 g")],
        "img_kw": "headphones", "img_lk": 60,
    },

    # ── Earbuds ─────────────────────────────────────────────────────────────
    {
        "name": "Apple AirPods Pro 2nd Generation",
        "short": "Active Noise Cancellation and Transparency mode with H2 chip.",
        "desc": "AirPods Pro feature the Apple H2 chip for up to 2× more noise cancellation and personalized Spatial Audio with dynamic head tracking. Adaptive Transparency lets you hear the world while reducing loud noise.",
        "cat": "audio", "brand": "apple",
        "price": "249.00", "discount": "199.00",
        "rating": "4.8", "reviews": 12400, "stock": 85, "pop": 990,
        "tags": ["wireless", "earbuds", "noise-cancelling", "apple"],
        "attrs": [("Chip", "Apple H2"), ("Battery (ANC on)", "6 hours"), ("Case Charging", "Lightning / MagSafe"), ("Water Resistance", "IPX4")],
        "img_kw": "earphones", "img_lk": 70,
    },
    {
        "name": "Sony WF-1000XM5 True Wireless Earbuds",
        "short": "Sony's flagship earbuds with best-in-class noise cancellation.",
        "desc": "The WF-1000XM5 features Sony's smallest noise-cancelling earbuds yet. Integrated V2 Processor and QN2e chip deliver HD noise cancelling with Dynamic Driver X for natural sound.",
        "cat": "audio", "brand": "sony",
        "price": "299.99", "discount": "249.99",
        "rating": "4.7", "reviews": 3850, "stock": 50, "pop": 960,
        "tags": ["wireless", "earbuds", "noise-cancelling", "bluetooth"],
        "attrs": [("Connectivity", "Bluetooth 5.3"), ("Battery (ANC on)", "8 hours"), ("Case Battery", "16 hours"), ("Water Resistance", "IPX4")],
        "img_kw": "earphones", "img_lk": 80,
    },
    {
        "name": "Samsung Galaxy Buds2 Pro",
        "short": "Hi-Fi 24-bit audio with intelligent ANC and 360 Audio.",
        "desc": "Galaxy Buds2 Pro delivers Hi-Fi 24-bit audio with an improved two-way speaker and bone conduction sensor for clear calls. Intelligent Active Noise Cancellation adapts in real time.",
        "cat": "audio", "brand": "samsung",
        "price": "229.99", "discount": "149.99",
        "rating": "4.5", "reviews": 4200, "stock": 65, "pop": 900,
        "tags": ["wireless", "earbuds", "noise-cancelling", "hi-fi"],
        "attrs": [("Connectivity", "Bluetooth 5.3"), ("Battery (ANC on)", "5 hours"), ("Water Resistance", "IPX7"), ("360 Audio", "Yes")],
        "img_kw": "earphones", "img_lk": 90,
    },
    {
        "name": "Apple AirPods 3rd Generation",
        "short": "Spatial Audio, MagSafe charging case, and 30-hour total battery.",
        "desc": "AirPods (3rd generation) feature Spatial Audio with dynamic head tracking. The H1 chip delivers 30-hour total battery life with the MagSafe Charging Case.",
        "cat": "audio", "brand": "apple",
        "price": "169.00", "discount": "149.00",
        "rating": "4.6", "reviews": 8900, "stock": 100, "pop": 950,
        "tags": ["wireless", "earbuds", "spatial-audio", "apple"],
        "attrs": [("Chip", "Apple H1"), ("Battery (buds)", "6 hours"), ("Sweat Resistance", "IPX4"), ("Case", "MagSafe compatible")],
        "img_kw": "earphones", "img_lk": 100,
    },

    # ── Portable Speakers ────────────────────────────────────────────────────
    {
        "name": "JBL Charge 5 Portable Speaker",
        "short": "Waterproof Bluetooth speaker with powerful JBL Pro Sound.",
        "desc": "The JBL Charge 5 features a racetrack-shaped woofer, separate tweeter, and dual passive radiators for powerful bass. IP67 waterproof rating and a USB-A port to charge your devices.",
        "cat": "audio", "brand": "jbl",
        "price": "179.95", "discount": "149.95",
        "rating": "4.7", "reviews": 7800, "stock": 75, "pop": 930,
        "tags": ["bluetooth", "portable", "waterproof", "outdoor"],
        "attrs": [("Battery Life", "20 hours"), ("Waterproof", "IP67"), ("Power Bank", "Yes"), ("Woofer", "Racetrack")],
        "img_kw": "bluetooth speaker", "img_lk": 110,
    },
    {
        "name": "JBL Flip 6 Portable Speaker",
        "short": "Compact waterproof speaker with deep bass and clear highs.",
        "desc": "JBL Flip 6 uses a two-way speaker system with separate tweeter for clear highs and a racetrack woofer for punchy bass. IP67 waterproof for outdoor adventures.",
        "cat": "audio", "brand": "jbl",
        "price": "129.95", "discount": "99.95",
        "rating": "4.6", "reviews": 5400, "stock": 90, "pop": 880,
        "tags": ["bluetooth", "portable", "waterproof", "compact"],
        "attrs": [("Battery Life", "12 hours"), ("Waterproof", "IP67"), ("PartyBoost", "Yes"), ("Weight", "550 g")],
        "img_kw": "bluetooth speaker", "img_lk": 120,
    },
    {
        "name": "Sony SRS-XB43 Extra Bass Speaker",
        "short": "Powerful Extra Bass with party lights and 24-hour battery.",
        "desc": "Pump up your sound with the SRS-XB43. Extra Bass technology delivers powerful, punchy bass. Live Sound mode emulates a concert experience with multi-directional sound.",
        "cat": "audio", "brand": "sony",
        "price": "199.99", "discount": "149.99",
        "rating": "4.5", "reviews": 2900, "stock": 45, "pop": 820,
        "tags": ["bluetooth", "portable", "extra-bass", "party"],
        "attrs": [("Battery Life", "24 hours"), ("Waterproof", "IP67"), ("Live Sound Mode", "Yes"), ("Weight", "1.18 kg")],
        "img_kw": "bluetooth speaker", "img_lk": 130,
    },
    {
        "name": "Bose SoundLink Mini II Special Edition",
        "short": "Compact speaker with surprisingly big sound and speakerphone.",
        "desc": "The SoundLink Mini II delivers full sound with dramatically deep lows. Built-in speakerphone and voice prompts make Bluetooth pairing easy.",
        "cat": "audio", "brand": "bose",
        "price": "149.00", "discount": "119.00",
        "rating": "4.6", "reviews": 3200, "stock": 55, "pop": 845,
        "tags": ["bluetooth", "portable", "compact", "speakerphone"],
        "attrs": [("Battery Life", "10 hours"), ("Speakerphone", "Yes"), ("Weight", "680 g"), ("Charging", "USB-C")],
        "img_kw": "bluetooth speaker", "img_lk": 140,
    },

    # ── Laptops ─────────────────────────────────────────────────────────────
    {
        "name": "Apple MacBook Pro 14-inch M3 Pro",
        "short": "Pro-level performance in a compact laptop powered by M3 Pro.",
        "desc": "MacBook Pro with M3 Pro delivers extraordinary performance with up to 18 hours of battery. The Liquid Retina XDR display offers P3 wide colour and ProMotion adaptive 120Hz refresh.",
        "cat": "computers", "brand": "apple",
        "price": "1999.00", "discount": "1799.00",
        "rating": "4.9", "reviews": 3100, "stock": 20, "pop": 980,
        "tags": ["laptop", "macos", "m3", "pro", "portable"],
        "attrs": [("Chip", "Apple M3 Pro"), ("RAM", "18 GB"), ("Storage", "512 GB SSD"), ("Display", "14.2\" Liquid Retina XDR"), ("Battery", "18 hours")],
        "img_kw": "macbook", "img_lk": 150,
    },
    {
        "name": "Apple MacBook Air 15-inch M2",
        "short": "Thin, light, and fanless with a stunning 15-inch display.",
        "desc": "MacBook Air 15 with M2 is the world's best consumer laptop. Completely silent with no fan, and up to 18-hour battery — perfect for creative projects.",
        "cat": "computers", "brand": "apple",
        "price": "1299.00", "discount": "1099.00",
        "rating": "4.8", "reviews": 5600, "stock": 35, "pop": 975,
        "tags": ["laptop", "macos", "m2", "thin", "fanless"],
        "attrs": [("Chip", "Apple M2"), ("RAM", "8 GB"), ("Storage", "256 GB SSD"), ("Display", "15.3\" Liquid Retina"), ("Battery", "18 hours")],
        "img_kw": "macbook", "img_lk": 160,
    },
    {
        "name": "Dell XPS 15 9530",
        "short": "Premium Windows laptop with OLED display and RTX 4060.",
        "desc": "The XPS 15 features a stunning 15.6\" OLED display with 100% DCI-P3 colour. Powered by 13th Gen Intel Core i7 with NVIDIA RTX 4060 for demanding creative applications.",
        "cat": "computers", "brand": "dell",
        "price": "1799.99", "discount": "1499.99",
        "rating": "4.6", "reviews": 1820, "stock": 18, "pop": 890,
        "tags": ["laptop", "windows", "oled", "creator", "rtx"],
        "attrs": [("Processor", "Intel Core i7-13700H"), ("RAM", "16 GB DDR5"), ("Storage", "512 GB NVMe"), ("Display", "15.6\" OLED 3.5K"), ("GPU", "NVIDIA RTX 4060")],
        "img_kw": "laptop", "img_lk": 170,
    },
    {
        "name": "ASUS ROG Zephyrus G14",
        "short": "Compact gaming powerhouse with Ryzen 9 and RTX 4060.",
        "desc": "The ROG Zephyrus G14 packs an AMD Ryzen 9 processor and NVIDIA GeForce RTX 4060 into a 14-inch chassis with AniMe Matrix LED display on the lid.",
        "cat": "computers", "brand": "asus",
        "price": "1449.99", "discount": "1199.99",
        "rating": "4.7", "reviews": 2450, "stock": 22, "pop": 910,
        "tags": ["laptop", "gaming", "amd", "rtx", "compact"],
        "attrs": [("Processor", "AMD Ryzen 9 7940HS"), ("RAM", "16 GB DDR5"), ("Storage", "1 TB NVMe"), ("Display", "14\" QHD+ 165Hz"), ("GPU", "NVIDIA RTX 4060")],
        "img_kw": "gaming laptop", "img_lk": 180,
    },
    {
        "name": "Dell Inspiron 16 Plus",
        "short": "Versatile 16-inch laptop with 12th Gen Intel and fast SSD.",
        "desc": "The Inspiron 16 Plus delivers everyday performance in a stylish chassis. The 16-inch FHD+ ComfortView Plus display reduces blue light without affecting colour accuracy.",
        "cat": "computers", "brand": "dell",
        "price": "899.99", "discount": "749.99",
        "rating": "4.4", "reviews": 1290, "stock": 40, "pop": 830,
        "tags": ["laptop", "windows", "everyday", "student"],
        "attrs": [("Processor", "Intel Core i7-12700H"), ("RAM", "16 GB DDR5"), ("Storage", "512 GB NVMe"), ("Display", "16\" FHD+ 120Hz")],
        "img_kw": "laptop", "img_lk": 190,
    },
    {
        "name": "Microsoft Surface Laptop 5",
        "short": "Premium thin and light laptop with tactile Alcantara keyboard.",
        "desc": "Surface Laptop 5 is elegant and powerful with a 13.5\" PixelSense touchscreen. The Dolby Atmos Omnisonic speakers deliver immersive audio.",
        "cat": "computers", "brand": "microsoft",
        "price": "1299.99", "discount": "999.99",
        "rating": "4.5", "reviews": 980, "stock": 25, "pop": 840,
        "tags": ["laptop", "windows", "touch", "thin", "premium"],
        "attrs": [("Processor", "Intel Core i5-1235U"), ("RAM", "8 GB"), ("Storage", "256 GB SSD"), ("Display", "13.5\" PixelSense"), ("Weight", "1.29 kg")],
        "img_kw": "laptop", "img_lk": 200,
    },
    {
        "name": "ASUS ZenBook 14 OLED",
        "short": "Slim and stylish 14-inch OLED laptop with Intel EVO certification.",
        "desc": "ZenBook 14 OLED features a 2.8K OLED display with PANTONE Validated colour accuracy. Powered by 12th Gen Intel Core, certified for Intel EVO platform.",
        "cat": "computers", "brand": "asus",
        "price": "1099.99", "discount": "899.99",
        "rating": "4.6", "reviews": 1540, "stock": 30, "pop": 860,
        "tags": ["laptop", "oled", "thin", "intel", "evo"],
        "attrs": [("Processor", "Intel Core i7-1260P"), ("RAM", "16 GB LPDDR5"), ("Storage", "512 GB NVMe"), ("Display", "14\" OLED 2.8K 90Hz"), ("Weight", "1.39 kg")],
        "img_kw": "laptop", "img_lk": 210,
    },
    {
        "name": "Apple Mac Mini M2",
        "short": "Surprisingly powerful desktop in a compact enclosure.",
        "desc": "Mac mini with M2 delivers dramatic improvements in CPU, GPU, and machine learning performance — all in the same iconic compact desktop design.",
        "cat": "computers", "brand": "apple",
        "price": "699.00", "discount": "599.00",
        "rating": "4.8", "reviews": 4100, "stock": 50, "pop": 930,
        "tags": ["desktop", "macos", "m2", "compact", "mini"],
        "attrs": [("Chip", "Apple M2"), ("RAM", "8 GB"), ("Storage", "256 GB SSD"), ("Ports", "2× USB-C, 2× USB-A, HDMI, Ethernet")],
        "img_kw": "mac mini", "img_lk": 220,
    },

    # ── Gaming Mice ─────────────────────────────────────────────────────────
    {
        "name": "Logitech G Pro X Superlight 2",
        "short": "Ultra-lightweight 60g wireless gaming mouse for pros.",
        "desc": "G Pro X Superlight 2 features the HERO 2 sensor with 32,000 DPI and POWERPLAY wireless charging compatibility. Weighing just 60g — built for the highest-performing esports professionals.",
        "cat": "gaming", "brand": "logitech",
        "price": "159.99", "discount": "129.99",
        "rating": "4.8", "reviews": 6700, "stock": 40, "pop": 960,
        "tags": ["gaming", "wireless", "mouse", "lightweight", "esports"],
        "attrs": [("Sensor", "HERO 2 (32,000 DPI)"), ("Weight", "60 g"), ("Battery", "95 hours"), ("Buttons", "5"), ("Connectivity", "Lightspeed Wireless")],
        "img_kw": "gaming mouse", "img_lk": 230,
    },
    {
        "name": "Razer DeathAdder V3 Pro Wireless",
        "short": "Iconic ergonomic gaming mouse reimagined for wireless play.",
        "desc": "The DeathAdder V3 Pro features Focus Pro 30K sensor, HyperSpeed wireless technology, and 90-hour battery life in a 64g ergonomic chassis.",
        "cat": "gaming", "brand": "razer",
        "price": "149.99", "discount": "119.99",
        "rating": "4.7", "reviews": 4300, "stock": 35, "pop": 940,
        "tags": ["gaming", "wireless", "mouse", "ergonomic", "esports"],
        "attrs": [("Sensor", "Focus Pro 30K DPI"), ("Weight", "64 g"), ("Battery", "90 hours"), ("Buttons", "5"), ("Connectivity", "HyperSpeed Wireless")],
        "img_kw": "gaming mouse", "img_lk": 240,
    },
    {
        "name": "SteelSeries Aerox 3 Wireless",
        "short": "Ultra-light honeycomb wireless gaming mouse with AquaBarrier.",
        "desc": "Aerox 3 Wireless features TrueMove Air optical sensor up to 18,000 CPI. AquaBarrier coating protects electronics from spills. Ultra-light honeycomb shell at 68g.",
        "cat": "gaming", "brand": "steelseries",
        "price": "79.99", "discount": "59.99",
        "rating": "4.5", "reviews": 3100, "stock": 60, "pop": 870,
        "tags": ["gaming", "wireless", "mouse", "lightweight", "honeycomb"],
        "attrs": [("Sensor", "TrueMove Air 18,000 CPI"), ("Weight", "68 g"), ("Battery", "200 hours"), ("Buttons", "6"), ("Water Resistance", "IP54")],
        "img_kw": "gaming mouse", "img_lk": 250,
    },
    {
        "name": "Razer Viper V2 Pro",
        "short": "58g symmetrical wireless gaming mouse with Focus Pro sensor.",
        "desc": "Viper V2 Pro is Razer's ultimate esports gaming mouse at just 58g. Features Focus Pro 30K sensor with intelligent tracking on glass and asymmetric scroll wheel resistance.",
        "cat": "gaming", "brand": "razer",
        "price": "149.99", "discount": "119.99",
        "rating": "4.8", "reviews": 5200, "stock": 30, "pop": 950,
        "tags": ["gaming", "wireless", "mouse", "ultra-light", "esports"],
        "attrs": [("Sensor", "Focus Pro 30K DPI"), ("Weight", "58 g"), ("Battery", "80 hours"), ("Shape", "Ambidextrous")],
        "img_kw": "gaming mouse", "img_lk": 260,
    },

    # ── Gaming Keyboards ─────────────────────────────────────────────────────
    {
        "name": "Corsair K100 RGB Mechanical Keyboard",
        "short": "Full-size flagship keyboard with OPX optical switches and AXON.",
        "desc": "The K100 RGB features CORSAIR AXON hyper-processing technology for 4,000Hz polling rate. OPX optical-mechanical switches respond at the speed of light with 0.4mm actuation.",
        "cat": "gaming", "brand": "corsair",
        "price": "229.99", "discount": "179.99",
        "rating": "4.7", "reviews": 2840, "stock": 20, "pop": 890,
        "tags": ["gaming", "keyboard", "mechanical", "rgb", "optical"],
        "attrs": [("Switches", "OPX Optical-Mechanical"), ("Polling Rate", "4,000 Hz"), ("Backlight", "Per-key RGB"), ("Form Factor", "Full-size"), ("Connectivity", "USB-A")],
        "img_kw": "mechanical keyboard", "img_lk": 270,
    },
    {
        "name": "Razer BlackWidow V4 Pro",
        "short": "Premium wireless gaming keyboard with Razer Green switches.",
        "desc": "BlackWidow V4 Pro delivers premium wireless performance with Razer HyperSpeed. Customisable Multi-Function Roller and 8-zone underglow lighting complete the battlestation.",
        "cat": "gaming", "brand": "razer",
        "price": "229.99", "discount": "189.99",
        "rating": "4.6", "reviews": 1950, "stock": 25, "pop": 870,
        "tags": ["gaming", "keyboard", "wireless", "mechanical", "rgb"],
        "attrs": [("Switches", "Razer Green Clicky"), ("Connectivity", "HyperSpeed Wireless / Bluetooth"), ("Battery", "200 hours"), ("Form Factor", "Full-size")],
        "img_kw": "mechanical keyboard", "img_lk": 280,
    },
    {
        "name": "SteelSeries Apex Pro TKL Wireless",
        "short": "World's fastest keyboard with adjustable OmniPoint 2.0 switches.",
        "desc": "Apex Pro TKL Wireless features OmniPoint 2.0 adjustable magnetic switches — set actuation from 0.1mm to 4.0mm per key. Compact TKL design with OLED Smart Display.",
        "cat": "gaming", "brand": "steelseries",
        "price": "199.99", "discount": "159.99",
        "rating": "4.7", "reviews": 3200, "stock": 28, "pop": 910,
        "tags": ["gaming", "keyboard", "wireless", "magnetic", "tkl"],
        "attrs": [("Switches", "OmniPoint 2.0 Adjustable"), ("Polling Rate", "8,000 Hz"), ("Display", "OLED Smart Display"), ("Form Factor", "TKL"), ("Battery", "40 hours")],
        "img_kw": "mechanical keyboard", "img_lk": 290,
    },
    {
        "name": "HyperX Alloy Origins 60",
        "short": "Compact 60% keyboard with HyperX Red linear switches.",
        "desc": "Alloy Origins 60 is HyperX's ultra-compact 60% gaming keyboard. HyperX Red linear switches and solid aircraft-grade aluminum body at an accessible price.",
        "cat": "gaming", "brand": "hyperx",
        "price": "99.99", "discount": "79.99",
        "rating": "4.5", "reviews": 2100, "stock": 55, "pop": 830,
        "tags": ["gaming", "keyboard", "mechanical", "60%", "compact"],
        "attrs": [("Switches", "HyperX Red Linear"), ("Form Factor", "60%"), ("Material", "Aluminum"), ("Backlight", "RGB"), ("Cable", "Detachable USB-C")],
        "img_kw": "mechanical keyboard", "img_lk": 300,
    },

    # ── Gaming Headsets ──────────────────────────────────────────────────────
    {
        "name": "SteelSeries Arctis Nova Pro Wireless",
        "short": "Multi-system wireless headset with ANC and hot-swap battery.",
        "desc": "Arctis Nova Pro Wireless features dual-wireless connectivity, active noise cancellation, and a GameDAC Gen 2 for Hi-Res Audio. Hot-swap battery means you never run out of power.",
        "cat": "gaming", "brand": "steelseries",
        "price": "349.99", "discount": "279.99",
        "rating": "4.7", "reviews": 1890, "stock": 20, "pop": 870,
        "tags": ["gaming", "headset", "wireless", "noise-cancelling", "hi-res"],
        "attrs": [("Connectivity", "2.4GHz + Bluetooth"), ("Battery", "22 hours + hot-swap"), ("ANC", "Yes"), ("Hi-Res Audio", "Yes")],
        "img_kw": "gaming headset", "img_lk": 310,
    },
    {
        "name": "Corsair Virtuoso RGB Wireless XT",
        "short": "Broadcast-quality microphone in a premium wireless gaming headset.",
        "desc": "Virtuoso RGB Wireless XT connects to PC, PS5, Xbox, Switch, and mobile simultaneously. Broadcast-quality microphone delivers clear communications.",
        "cat": "gaming", "brand": "corsair",
        "price": "199.99", "discount": "149.99",
        "rating": "4.6", "reviews": 1540, "stock": 30, "pop": 840,
        "tags": ["gaming", "headset", "wireless", "rgb", "multi-platform"],
        "attrs": [("Connectivity", "2.4GHz + Bluetooth + 3.5mm"), ("Battery", "20 hours"), ("Microphone", "Omni-directional broadcast")],
        "img_kw": "gaming headset", "img_lk": 320,
    },
    {
        "name": "HyperX Cloud Alpha Wireless",
        "short": "Up to 300-hour wireless gaming headset with dual chamber audio.",
        "desc": "Cloud Alpha Wireless delivers an incredible 300-hour battery life. Dual chamber audio drivers physically separate bass from mids and highs for less distortion.",
        "cat": "gaming", "brand": "hyperx",
        "price": "199.99", "discount": "149.99",
        "rating": "4.6", "reviews": 2870, "stock": 35, "pop": 855,
        "tags": ["gaming", "headset", "wireless", "long-battery"],
        "attrs": [("Battery", "300 hours"), ("Connectivity", "2.4GHz"), ("Driver", "Dual chamber 50 mm"), ("Microphone", "Detachable noise-cancelling")],
        "img_kw": "gaming headset", "img_lk": 330,
    },
    {
        "name": "Razer Kraken V3 HyperSense",
        "short": "Wired gaming headset with powerful HyperSense haptic feedback.",
        "desc": "Kraken V3 HyperSense features unique haptic feedback via the TriForce Titanium 50mm driver. THX Spatial Audio delivers precise positional audio for competitive gaming.",
        "cat": "gaming", "brand": "razer",
        "price": "129.99", "discount": "99.99",
        "rating": "4.4", "reviews": 1200, "stock": 40, "pop": 800,
        "tags": ["gaming", "headset", "wired", "haptic", "thx"],
        "attrs": [("Driver", "TriForce Titanium 50 mm"), ("Haptic", "HyperSense"), ("Surround", "THX Spatial Audio"), ("Microphone", "HyperClear Cardioid")],
        "img_kw": "gaming headset", "img_lk": 340,
    },

    # ── Gaming Monitors ──────────────────────────────────────────────────────
    {
        "name": "ASUS ROG Swift OLED PG27AQDM",
        "short": "27\" QHD OLED gaming monitor with 240Hz and G-Sync.",
        "desc": "ROG Swift OLED features a 27\" QHD OLED panel with 240Hz refresh rate and 0.03ms response time. G-Sync Compatible and AMD FreeSync Premium eliminate screen tearing.",
        "cat": "gaming", "brand": "asus",
        "price": "799.99", "discount": "649.99",
        "rating": "4.8", "reviews": 1240, "stock": 18, "pop": 890,
        "tags": ["monitor", "gaming", "oled", "240hz", "qhd"],
        "attrs": [("Panel", "OLED"), ("Resolution", "2560×1440"), ("Refresh Rate", "240 Hz"), ("Response Time", "0.03 ms"), ("Sync", "G-Sync Compatible")],
        "img_kw": "gaming monitor", "img_lk": 350,
    },
    {
        "name": "Samsung Odyssey G7 27\" Curved",
        "short": "Curved 1000R QHD gaming monitor with 240Hz and DisplayHDR 600.",
        "desc": "The Odyssey G7 features a 1000R curvature matching the curve of the human eye for reduced eye strain. Quantum Dot technology delivers 125% sRGB colour volume.",
        "cat": "gaming", "brand": "samsung",
        "price": "499.99", "discount": "379.99",
        "rating": "4.6", "reviews": 3200, "stock": 25, "pop": 870,
        "tags": ["monitor", "gaming", "curved", "qhd", "240hz"],
        "attrs": [("Panel", "VA Quantum Dot"), ("Resolution", "2560×1440"), ("Refresh Rate", "240 Hz"), ("Curvature", "1000R"), ("HDR", "DisplayHDR 600")],
        "img_kw": "gaming monitor", "img_lk": 360,
    },
    {
        "name": "LG UltraGear 27GP850-B",
        "short": "27\" QHD Nano IPS gaming monitor with 180Hz and 1ms GtG.",
        "desc": "UltraGear 27GP850-B is a 27\" QHD Nano IPS display with 1ms GtG response time, 180Hz refresh rate, and NVIDIA G-Sync Compatible / AMD FreeSync Premium Pro.",
        "cat": "gaming", "brand": "lg",
        "price": "399.99", "discount": "299.99",
        "rating": "4.7", "reviews": 4800, "stock": 30, "pop": 900,
        "tags": ["monitor", "gaming", "ips", "qhd", "180hz"],
        "attrs": [("Panel", "Nano IPS"), ("Resolution", "2560×1440"), ("Refresh Rate", "180 Hz"), ("Response Time", "1 ms GtG"), ("HDR", "VESA DisplayHDR 400")],
        "img_kw": "gaming monitor", "img_lk": 370,
    },

    # ── Controllers ──────────────────────────────────────────────────────────
    {
        "name": "Microsoft Xbox Wireless Controller",
        "short": "The most comfortable Xbox controller with textured grip and USB-C.",
        "desc": "Xbox Wireless Controller features textured grip, a Share button, USB-C connectivity, and works on Xbox Series X|S, Xbox One, Windows, Android, and iOS.",
        "cat": "gaming", "brand": "microsoft",
        "price": "64.99", "discount": "54.99",
        "rating": "4.7", "reviews": 12000, "stock": 150, "pop": 960,
        "tags": ["gaming", "controller", "xbox", "wireless"],
        "attrs": [("Connectivity", "Xbox Wireless / Bluetooth / USB-C"), ("Battery", "AA batteries"), ("Compatibility", "Xbox / PC / Android / iOS")],
        "img_kw": "xbox controller", "img_lk": 380,
    },
    {
        "name": "Razer Wolverine V2 Chroma",
        "short": "Wired Xbox controller with Razer Mecha-Tactile face buttons.",
        "desc": "Wolverine V2 Chroma features 6 remappable multi-function buttons, Razer Mecha-Tactile Action Buttons, and upgradeable thumbsticks and D-Pad. Licensed by Xbox.",
        "cat": "gaming", "brand": "razer",
        "price": "129.99", "discount": "99.99",
        "rating": "4.5", "reviews": 1800, "stock": 45, "pop": 820,
        "tags": ["gaming", "controller", "xbox", "wired", "pro"],
        "attrs": [("Connectivity", "Wired USB-A"), ("Extra Buttons", "6 remappable"), ("Triggers", "Hair trigger stops"), ("Thumbsticks", "Interchangeable")],
        "img_kw": "xbox controller", "img_lk": 390,
    },

    # ── Smartphones ─────────────────────────────────────────────────────────
    {
        "name": "Apple iPhone 15 Pro",
        "short": "Titanium design with A17 Pro chip and 3× Telephoto camera.",
        "desc": "iPhone 15 Pro features a lightweight titanium design and A17 Pro chip. The 48MP Main camera with sensor-shift OIS delivers stunning photos. Action Button adds new customisation.",
        "cat": "smartphones", "brand": "apple",
        "price": "999.00", "discount": "899.00",
        "rating": "4.8", "reviews": 18500, "stock": 60, "pop": 990,
        "tags": ["smartphone", "ios", "titanium", "pro", "5g"],
        "attrs": [("Chip", "A17 Pro"), ("Main Camera", "48 MP"), ("Display", "6.1\" Super Retina XDR OLED"), ("Storage Options", "128 GB – 1 TB"), ("5G", "Yes")],
        "img_kw": "iphone", "img_lk": 400,
    },
    {
        "name": "Samsung Galaxy S24 Ultra",
        "short": "AI-powered smartphone with built-in S Pen and 200MP camera.",
        "desc": "Galaxy S24 Ultra introduces Galaxy AI with Circle to Search, Live Translate, and Note Assist. Snapdragon 8 Gen 3 powers the 200MP camera system and built-in S Pen.",
        "cat": "smartphones", "brand": "samsung",
        "price": "1299.99", "discount": "1099.99",
        "rating": "4.8", "reviews": 9800, "stock": 40, "pop": 985,
        "tags": ["smartphone", "android", "s-pen", "ai", "5g"],
        "attrs": [("Processor", "Snapdragon 8 Gen 3"), ("Main Camera", "200 MP"), ("Display", "6.8\" Dynamic AMOLED 2X 120Hz"), ("S Pen", "Included"), ("5G", "Yes")],
        "img_kw": "samsung galaxy", "img_lk": 410,
    },
    {
        "name": "Samsung Galaxy S24",
        "short": "Compact flagship with Galaxy AI and all-day battery.",
        "desc": "Galaxy S24 brings Galaxy AI to the compact flagship format. Exynos 2400 and a bright 6.2\" FHD+ Dynamic AMOLED 2X display make it the perfect everyday phone.",
        "cat": "smartphones", "brand": "samsung",
        "price": "799.99", "discount": "699.99",
        "rating": "4.7", "reviews": 7200, "stock": 75, "pop": 965,
        "tags": ["smartphone", "android", "ai", "compact", "5g"],
        "attrs": [("Processor", "Exynos 2400"), ("Main Camera", "50 MP"), ("Display", "6.2\" Dynamic AMOLED 2X 120Hz"), ("RAM", "8 GB"), ("5G", "Yes")],
        "img_kw": "samsung galaxy", "img_lk": 420,
    },
    {
        "name": "Apple iPhone 15",
        "short": "Dynamic Island, 48MP camera, and USB-C — iPhone for everyone.",
        "desc": "iPhone 15 brings Dynamic Island to the full iPhone 15 lineup. The 48MP Main camera shoots super-high-resolution photos, and for the first time USB-C connectivity.",
        "cat": "smartphones", "brand": "apple",
        "price": "799.00", "discount": "699.00",
        "rating": "4.7", "reviews": 22000, "stock": 85, "pop": 980,
        "tags": ["smartphone", "ios", "usb-c", "dynamic-island", "5g"],
        "attrs": [("Chip", "A16 Bionic"), ("Main Camera", "48 MP"), ("Display", "6.1\" Super Retina XDR OLED"), ("Charging", "USB-C"), ("5G", "Yes")],
        "img_kw": "iphone", "img_lk": 430,
    },
    {
        "name": "Samsung Galaxy A54 5G",
        "short": "Mid-range champion with 50MP OIS camera and 5000mAh battery.",
        "desc": "Galaxy A54 5G with IP67 water resistance, 50MP OIS camera, and a 5000mAh battery that lasts two days — the best mid-range Samsung has made.",
        "cat": "smartphones", "brand": "samsung",
        "price": "449.99", "discount": "349.99",
        "rating": "4.5", "reviews": 5400, "stock": 110, "pop": 880,
        "tags": ["smartphone", "android", "mid-range", "5g", "value"],
        "attrs": [("Processor", "Exynos 1380"), ("Main Camera", "50 MP OIS"), ("Battery", "5000 mAh"), ("Water Resistance", "IP67"), ("RAM", "8 GB")],
        "img_kw": "samsung galaxy", "img_lk": 440,
    },
    {
        "name": "Samsung Galaxy Z Fold 5",
        "short": "The ultimate productivity phone that unfolds into a tablet.",
        "desc": "Galaxy Z Fold 5 is slimmer and lighter than ever with the crease-free Flex Hinge. The 7.6\" foldable display is perfect for multitasking.",
        "cat": "smartphones", "brand": "samsung",
        "price": "1799.99", "discount": "1499.99",
        "rating": "4.6", "reviews": 3100, "stock": 20, "pop": 870,
        "tags": ["smartphone", "android", "foldable", "pro", "5g"],
        "attrs": [("Processor", "Snapdragon 8 Gen 2"), ("Main Display", "7.6\" Dynamic AMOLED 2X"), ("Cover Display", "6.2\" Dynamic AMOLED"), ("RAM", "12 GB"), ("Hinge", "Flex Hinge")],
        "img_kw": "foldable phone", "img_lk": 450,
    },

    # ── Cameras ─────────────────────────────────────────────────────────────
    {
        "name": "Sony Alpha A7 IV Mirrorless Camera",
        "short": "33MP full-frame mirrorless for stills and 4K video.",
        "desc": "The A7 IV features a 33MP BSI CMOS sensor and BIONZ XR processor for detail-rich stills and 4K 60p video. 759-point phase-detection AF with real-time Eye AF.",
        "cat": "cameras", "brand": "sony",
        "price": "2499.99", "discount": "2199.99",
        "rating": "4.8", "reviews": 2900, "stock": 12, "pop": 870,
        "tags": ["mirrorless", "full-frame", "4k", "professional"],
        "attrs": [("Sensor", "33 MP Full-Frame BSI CMOS"), ("Processor", "BIONZ XR"), ("Video", "4K 60p"), ("AF Points", "759"), ("Stabilisation", "5.5-stop IBIS")],
        "img_kw": "mirrorless camera", "img_lk": 460,
    },
    {
        "name": "Sony ZV-E10 Vlog Camera",
        "short": "APS-C mirrorless designed for vloggers with side-flip screen.",
        "desc": "ZV-E10 is Sony's dedicated vlogging camera with APS-C sensor and interchangeable E-mount lenses. Side-flip screen, directional 3-capsule mic, and Background Defocus mode.",
        "cat": "cameras", "brand": "sony",
        "price": "749.99", "discount": "599.99",
        "rating": "4.6", "reviews": 3800, "stock": 35, "pop": 850,
        "tags": ["mirrorless", "vlog", "aps-c", "content-creator"],
        "attrs": [("Sensor", "24.2 MP APS-C"), ("Video", "4K 30p"), ("Screen", "Flip-out touchscreen"), ("Microphone", "3-capsule directional"), ("Lens Mount", "E-mount")],
        "img_kw": "vlog camera", "img_lk": 470,
    },
    {
        "name": "GoPro HERO12 Black",
        "short": "5.3K video, HyperSmooth 6.0, and HDR — the most powerful HERO yet.",
        "desc": "HERO12 Black delivers 5.3K60 video with HyperSmooth 6.0 stabilisation for ultra-smooth footage. HDR video and Enduro Battery make this the best HERO ever.",
        "cat": "cameras", "brand": "gopro",
        "price": "399.99", "discount": "299.99",
        "rating": "4.7", "reviews": 5600, "stock": 50, "pop": 900,
        "tags": ["action-camera", "waterproof", "4k", "outdoor", "stabilisation"],
        "attrs": [("Video", "5.3K60 / 4K120"), ("Stabilisation", "HyperSmooth 6.0"), ("Waterproof", "10 m"), ("HDR", "Yes"), ("Battery", "Enduro")],
        "img_kw": "gopro action camera", "img_lk": 480,
    },
    {
        "name": "GoPro HERO11 Black",
        "short": "Largest GoPro sensor in history with 10-bit colour.",
        "desc": "HERO11 Black features a new 1/1.9\" image sensor for a wider field of view and 10-bit colour. HyperSmooth 5.0 and in-app editing make sharing instant.",
        "cat": "cameras", "brand": "gopro",
        "price": "299.99", "discount": "249.99",
        "rating": "4.6", "reviews": 4200, "stock": 45, "pop": 870,
        "tags": ["action-camera", "waterproof", "4k", "outdoor"],
        "attrs": [("Video", "5.3K60 / 4K120"), ("Sensor", "1/1.9\""), ("Colour", "10-bit"), ("Stabilisation", "HyperSmooth 5.0"), ("Waterproof", "10 m")],
        "img_kw": "gopro action camera", "img_lk": 490,
    },
    {
        "name": "Logitech Brio 500 Full HD Webcam",
        "short": "1080p webcam with Show Mode, auto light correction, and auto framing.",
        "desc": "Brio 500 features RightLight 4 for clear video in challenging lighting, Show Mode for displaying your desk, and auto framing powered by AI.",
        "cat": "cameras", "brand": "logitech",
        "price": "129.99", "discount": "99.99",
        "rating": "4.5", "reviews": 3100, "stock": 80, "pop": 840,
        "tags": ["webcam", "1080p", "streaming", "home-office"],
        "attrs": [("Resolution", "1080p 60fps"), ("Field of View", "90°"), ("Autofocus", "Yes"), ("Connection", "USB-C"), ("Show Mode", "Yes")],
        "img_kw": "webcam", "img_lk": 500,
    },
    {
        "name": "Logitech C920x HD Pro Webcam",
        "short": "Full HD 1080p webcam — the world's most popular for streaming.",
        "desc": "C920x delivers Full HD 1080p/30fps video with HD autofocus and automatic light correction. Dual microphones capture natural stereo sound for clear calls.",
        "cat": "cameras", "brand": "logitech",
        "price": "69.99", "discount": "49.99",
        "rating": "4.6", "reviews": 18000, "stock": 200, "pop": 920,
        "tags": ["webcam", "1080p", "streaming", "budget", "home-office"],
        "attrs": [("Resolution", "1080p 30fps"), ("Autofocus", "Yes"), ("Microphone", "Dual stereo"), ("Connection", "USB-A"), ("Compatibility", "Windows / Mac / ChromeOS")],
        "img_kw": "webcam", "img_lk": 510,
    },

    # ── Productivity Monitors ─────────────────────────────────────────────────
    {
        "name": "LG 27UK850-W 4K UHD Monitor",
        "short": "27\" 4K IPS monitor with USB-C 60W power delivery and HDR10.",
        "desc": "LG 27UK850-W delivers 4K UHD resolution with DCI-P3 95% colour. USB-C with 60W power delivery charges your laptop while you work.",
        "cat": "monitors", "brand": "lg",
        "price": "449.99", "discount": "349.99",
        "rating": "4.6", "reviews": 5800, "stock": 35, "pop": 880,
        "tags": ["monitor", "4k", "usb-c", "hdr", "ips"],
        "attrs": [("Panel", "IPS"), ("Resolution", "3840×2160"), ("Refresh Rate", "60 Hz"), ("USB-C Power", "60 W"), ("HDR", "HDR10")],
        "img_kw": "computer monitor", "img_lk": 520,
    },
    {
        "name": "Dell UltraSharp U2723QE 4K Monitor",
        "short": "27\" 4K IPS Black panel with USB-C hub and 99% sRGB.",
        "desc": "UltraSharp U2723QE uses IPS Black technology for 2000:1 contrast — 2× typical IPS. Built-in KVM switch, USB-C 90W charging, and daisy-chain capability.",
        "cat": "monitors", "brand": "dell",
        "price": "699.99", "discount": "549.99",
        "rating": "4.7", "reviews": 2400, "stock": 20, "pop": 870,
        "tags": ["monitor", "4k", "usb-c", "ips-black", "professional"],
        "attrs": [("Panel", "IPS Black"), ("Resolution", "3840×2160"), ("Contrast", "2000:1"), ("USB-C Power", "90 W"), ("KVM", "Built-in")],
        "img_kw": "computer monitor", "img_lk": 530,
    },
    {
        "name": "Samsung 34\" Odyssey G5 Ultrawide",
        "short": "34\" curved ultrawide WQHD gaming monitor at 165Hz.",
        "desc": "Odyssey G5 Ultrawide offers a 21:9 aspect ratio with a 1000R curve for an immersive experience. WQHD resolution and 165Hz refresh rate deliver competitive performance.",
        "cat": "monitors", "brand": "samsung",
        "price": "499.99", "discount": "399.99",
        "rating": "4.5", "reviews": 3600, "stock": 28, "pop": 860,
        "tags": ["monitor", "ultrawide", "curved", "gaming", "qhd"],
        "attrs": [("Panel", "VA"), ("Resolution", "3440×1440"), ("Refresh Rate", "165 Hz"), ("Curvature", "1000R"), ("HDR", "HDR10")],
        "img_kw": "ultrawide monitor", "img_lk": 540,
    },
    {
        "name": "LG 34WN80C-B UltraWide Monitor",
        "short": "34\" WQHD IPS curved ultrawide for productivity and creativity.",
        "desc": "LG UltraWide 34WN80C-B provides a 21:9 WQHD view with 33% more screen space than standard FHD. Thunderbolt 3 USB-C compatible with 60W charging.",
        "cat": "monitors", "brand": "lg",
        "price": "699.99", "discount": "549.99",
        "rating": "4.6", "reviews": 2100, "stock": 22, "pop": 845,
        "tags": ["monitor", "ultrawide", "curved", "usb-c", "productivity"],
        "attrs": [("Panel", "IPS"), ("Resolution", "3440×1440"), ("Refresh Rate", "60 Hz"), ("USB-C Power", "60 W"), ("Curvature", "2300R")],
        "img_kw": "ultrawide monitor", "img_lk": 550,
    },
    {
        "name": "ASUS ProArt PA278QV 27\" WQHD",
        "short": "Factory-calibrated professional monitor with 100% sRGB and REC.709.",
        "desc": "PA278QV is factory-calibrated with a Delta E < 2 report. 100% sRGB and Rec.709 makes it ideal for photo and video editing professionals.",
        "cat": "monitors", "brand": "asus",
        "price": "399.99", "discount": "319.99",
        "rating": "4.7", "reviews": 3100, "stock": 30, "pop": 855,
        "tags": ["monitor", "professional", "colour-accurate", "wqhd"],
        "attrs": [("Panel", "IPS"), ("Resolution", "2560×1440"), ("Colour Accuracy", "Delta E < 2"), ("sRGB", "100%"), ("Refresh Rate", "75 Hz")],
        "img_kw": "computer monitor", "img_lk": 560,
    },
    {
        "name": "Dell 27 S2722DGM Gaming Monitor",
        "short": "Curved 27\" QHD gaming monitor with 165Hz and AMD FreeSync.",
        "desc": "S2722DGM combines a 27\" curved VA panel with QHD resolution and 165Hz refresh rate. AMD FreeSync Premium and 1ms MPRT eliminate tearing and blur.",
        "cat": "monitors", "brand": "dell",
        "price": "329.99", "discount": "269.99",
        "rating": "4.5", "reviews": 4200, "stock": 40, "pop": 840,
        "tags": ["monitor", "gaming", "curved", "qhd", "165hz"],
        "attrs": [("Panel", "VA"), ("Resolution", "2560×1440"), ("Refresh Rate", "165 Hz"), ("Curvature", "1800R"), ("Sync", "AMD FreeSync Premium")],
        "img_kw": "gaming monitor", "img_lk": 570,
    },

    # ── Storage ─────────────────────────────────────────────────────────────
    {
        "name": "Samsung 870 EVO 1TB SATA SSD",
        "short": "The most trusted Samsung SSD with MKX controller and 5-year warranty.",
        "desc": "870 EVO features V-NAND and Samsung's latest MKX controller for sequential read up to 560 MB/s. 5-year limited warranty and 600 TBW endurance rating.",
        "cat": "storage", "brand": "samsung",
        "price": "109.99", "discount": "79.99",
        "rating": "4.8", "reviews": 24000, "stock": 150, "pop": 960,
        "tags": ["ssd", "sata", "storage", "reliable"],
        "attrs": [("Interface", "SATA III"), ("Capacity", "1 TB"), ("Read Speed", "560 MB/s"), ("Write Speed", "530 MB/s"), ("Endurance", "600 TBW")],
        "img_kw": "ssd storage", "img_lk": 580,
    },
    {
        "name": "Samsung 990 Pro 2TB NVMe SSD",
        "short": "PCIe 4.0 NVMe with 7,450 MB/s sequential read for gaming and creators.",
        "desc": "990 Pro delivers 7,450 MB/s sequential read and 6,900 MB/s write. The optimised controller and Pascal algorithm maintain peak performance during extended workloads.",
        "cat": "storage", "brand": "samsung",
        "price": "199.99", "discount": "149.99",
        "rating": "4.8", "reviews": 8500, "stock": 70, "pop": 950,
        "tags": ["ssd", "nvme", "pcie4", "storage", "gaming"],
        "attrs": [("Interface", "PCIe 4.0 NVMe"), ("Capacity", "2 TB"), ("Read Speed", "7,450 MB/s"), ("Write Speed", "6,900 MB/s"), ("Form Factor", "M.2 2280")],
        "img_kw": "nvme ssd", "img_lk": 590,
    },
    {
        "name": "Western Digital Blue 1TB SATA SSD",
        "short": "Reliable everyday SSD with 3D NAND for desktop and laptop.",
        "desc": "WD Blue SATA SSD delivers consistently fast performance with 3D NAND technology. Ideal upgrade for slow spinning hard drives in desktops and laptops.",
        "cat": "storage", "brand": "western-digital",
        "price": "89.99", "discount": "69.99",
        "rating": "4.7", "reviews": 12000, "stock": 130, "pop": 920,
        "tags": ["ssd", "sata", "storage", "everyday"],
        "attrs": [("Interface", "SATA III"), ("Capacity", "1 TB"), ("Read Speed", "560 MB/s"), ("Write Speed", "530 MB/s"), ("Form Factor", "2.5\"")],
        "img_kw": "ssd storage", "img_lk": 600,
    },
    {
        "name": "Samsung T7 1TB Portable SSD",
        "short": "Pocket-sized USB 3.2 SSD with 1,050 MB/s transfer speed.",
        "desc": "Samsung T7 is a compact, shock-resistant portable SSD that fits in your pocket. USB 3.2 Gen 2 delivers up to 1,050 MB/s read and 1,000 MB/s write.",
        "cat": "storage", "brand": "samsung",
        "price": "119.99", "discount": "89.99",
        "rating": "4.7", "reviews": 9800, "stock": 90, "pop": 930,
        "tags": ["portable-ssd", "usb-c", "fast", "compact"],
        "attrs": [("Interface", "USB 3.2 Gen 2 (USB-C)"), ("Capacity", "1 TB"), ("Read Speed", "1,050 MB/s"), ("Dimensions", "85×57×8 mm"), ("Shock Resistance", "1,500 G")],
        "img_kw": "portable ssd", "img_lk": 610,
    },
    {
        "name": "Seagate 2TB Expansion Portable HDD",
        "short": "2TB plug-and-play USB storage for Mac and PC.",
        "desc": "Seagate Expansion is the easy way to add massive storage. Plug in via USB 3.0 and start saving files right away — no software to install.",
        "cat": "storage", "brand": "seagate",
        "price": "69.99", "discount": "54.99",
        "rating": "4.5", "reviews": 15000, "stock": 200, "pop": 890,
        "tags": ["hdd", "portable", "backup", "plug-and-play"],
        "attrs": [("Interface", "USB 3.0"), ("Capacity", "2 TB"), ("Compatibility", "Windows / Mac"), ("Form Factor", "2.5\"")],
        "img_kw": "portable hard drive", "img_lk": 620,
    },
    {
        "name": "Western Digital 4TB My Passport Portable HDD",
        "short": "Compact 4TB hard drive with hardware encryption and backup software.",
        "desc": "My Passport comes with 256-bit AES hardware encryption and password protection. WD Backup software lets you schedule automatic backups.",
        "cat": "storage", "brand": "western-digital",
        "price": "109.99", "discount": "89.99",
        "rating": "4.6", "reviews": 8900, "stock": 110, "pop": 870,
        "tags": ["hdd", "portable", "backup", "encrypted"],
        "attrs": [("Interface", "USB 3.0"), ("Capacity", "4 TB"), ("Encryption", "256-bit AES"), ("Compatibility", "Windows / Mac"), ("Software", "WD Backup included")],
        "img_kw": "portable hard drive", "img_lk": 630,
    },
    {
        "name": "Kingston DataTraveler 256GB USB 3.2",
        "short": "High-speed USB flash drive for everyday file transfer.",
        "desc": "DataTraveler 100 G3 delivers USB 3.2 Gen 1 speeds up to 130 MB/s read. Compact rotating cap protects the connector without a separate piece to lose.",
        "cat": "storage", "brand": "kingston",
        "price": "39.99", "discount": "29.99",
        "rating": "4.5", "reviews": 7600, "stock": 300, "pop": 840,
        "tags": ["usb-drive", "flash", "portable", "fast"],
        "attrs": [("Interface", "USB 3.2 Gen 1"), ("Capacity", "256 GB"), ("Read Speed", "130 MB/s"), ("Design", "Rotating cap")],
        "img_kw": "usb flash drive", "img_lk": 640,
    },
    {
        "name": "Seagate IronWolf 4TB NAS HDD",
        "short": "NAS-optimised hard drive with AgileArray for 24/7 operation.",
        "desc": "IronWolf is purpose-built for network-attached storage. AgileArray technology optimises multi-drive performance and IronWolf Health Management monitors drive health.",
        "cat": "storage", "brand": "seagate",
        "price": "109.99", "discount": "89.99",
        "rating": "4.7", "reviews": 4500, "stock": 80, "pop": 820,
        "tags": ["hdd", "nas", "server", "24-7"],
        "attrs": [("Interface", "SATA 6 Gb/s"), ("Capacity", "4 TB"), ("RPM", "5,400"), ("Workload Rate", "180 TB/year"), ("MTBF", "1,000,000 hours")],
        "img_kw": "hard drive", "img_lk": 650,
    },

    # ── Networking ───────────────────────────────────────────────────────────
    {
        "name": "ASUS RT-AX88U Pro Wi-Fi 6 Router",
        "short": "AX6000 dual-band Wi-Fi 6 router with 8 LAN ports.",
        "desc": "RT-AX88U Pro supports MU-MIMO and OFDMA for improved wireless performance. Adaptive QoS, AiProtection Pro lifetime security, and 8 gigabit LAN ports.",
        "cat": "networking", "brand": "asus",
        "price": "349.99", "discount": "279.99",
        "rating": "4.7", "reviews": 2800, "stock": 25, "pop": 870,
        "tags": ["router", "wifi6", "ax6000", "gaming", "home"],
        "attrs": [("Wi-Fi Standard", "Wi-Fi 6 (802.11ax)"), ("Bands", "AX6000 Dual-Band"), ("LAN Ports", "8× Gigabit"), ("Security", "AiProtection Pro"), ("USB", "USB 3.0 + USB 2.0")],
        "img_kw": "wifi router", "img_lk": 660,
    },
    {
        "name": "TP-Link Archer AX73 Wi-Fi 6 Router",
        "short": "AX5400 Wi-Fi 6 router with 6 antennas for whole-home coverage.",
        "desc": "Archer AX73 provides AX5400 dual-band Wi-Fi 6 speeds. TP-Link HomeShield provides advanced security and parental controls.",
        "cat": "networking", "brand": "tp-link",
        "price": "179.99", "discount": "149.99",
        "rating": "4.6", "reviews": 5200, "stock": 50, "pop": 860,
        "tags": ["router", "wifi6", "ax5400", "budget", "home"],
        "attrs": [("Wi-Fi Standard", "Wi-Fi 6 (802.11ax)"), ("Bands", "AX5400 Dual-Band"), ("Antennas", "6"), ("WAN", "Gigabit"), ("USB", "USB 3.0")],
        "img_kw": "wifi router", "img_lk": 670,
    },
    {
        "name": "TP-Link Deco XE75 Mesh Wi-Fi 6E (3-pack)",
        "short": "Tri-band Wi-Fi 6E mesh system using the ultra-fast 6 GHz band.",
        "desc": "Deco XE75 uses the new 6 GHz band for a super-fast, interference-free backhaul. Covers up to 7,200 sq ft seamlessly across 3 nodes.",
        "cat": "networking", "brand": "tp-link",
        "price": "299.99", "discount": "249.99",
        "rating": "4.6", "reviews": 1900, "stock": 30, "pop": 840,
        "tags": ["mesh", "wifi6e", "6ghz", "whole-home", "tri-band"],
        "attrs": [("Wi-Fi Standard", "Wi-Fi 6E (802.11axe)"), ("Bands", "Tri-Band AX5400"), ("Coverage", "7,200 sq ft"), ("Units", "3-pack"), ("6 GHz", "Yes")],
        "img_kw": "mesh wifi", "img_lk": 680,
    },
    {
        "name": "TP-Link TL-SG108 8-Port Gigabit Switch",
        "short": "Plug-and-play 8-port unmanaged gigabit switch.",
        "desc": "TL-SG108 is an 8-port unmanaged switch with Gigabit ports. Plug-and-play setup requires no software or management configuration.",
        "cat": "networking", "brand": "tp-link",
        "price": "29.99", "discount": None,
        "rating": "4.7", "reviews": 12000, "stock": 300, "pop": 870,
        "tags": ["switch", "gigabit", "wired", "plug-and-play", "home"],
        "attrs": [("Ports", "8× Gigabit RJ45"), ("Speed", "1000 Mbps"), ("Management", "Unmanaged"), ("Switching Capacity", "16 Gbps")],
        "img_kw": "network switch", "img_lk": 690,
    },

    # ── Keyboards & Mice ─────────────────────────────────────────────────────
    {
        "name": "Logitech MX Master 3S Wireless Mouse",
        "short": "8K DPI precision mouse with quiet clicks and MagSpeed scroll.",
        "desc": "MX Master 3S features 8,000 DPI for pixel-precise tracking on any surface including glass. MagSpeed electromagnetic scrolling is 90% quieter.",
        "cat": "keyboards-mice", "brand": "logitech",
        "price": "99.99", "discount": "79.99",
        "rating": "4.8", "reviews": 14000, "stock": 80, "pop": 970,
        "tags": ["mouse", "wireless", "productivity", "ergonomic", "quiet"],
        "attrs": [("DPI", "200–8,000"), ("Battery", "70 days"), ("Scroll", "MagSpeed electromagnetic"), ("Connectivity", "Logi Bolt USB / Bluetooth"), ("Clicks", "90% quieter")],
        "img_kw": "wireless mouse", "img_lk": 700,
    },
    {
        "name": "Logitech MX Keys Advanced Wireless Keyboard",
        "short": "Smart illuminated keyboard for multi-device productivity.",
        "desc": "MX Keys pairs perfectly with MX Master 3S. Smart backlighting activates when your hands approach and adapts to ambient light. Works across up to 3 computers.",
        "cat": "keyboards-mice", "brand": "logitech",
        "price": "119.99", "discount": "99.99",
        "rating": "4.7", "reviews": 9800, "stock": 90, "pop": 940,
        "tags": ["keyboard", "wireless", "productivity", "backlit", "multi-device"],
        "attrs": [("Layout", "Full-size"), ("Backlight", "Smart ambient adaptive"), ("Battery", "10 days with backlight"), ("Connectivity", "Logi Bolt / Bluetooth"), ("Multi-device", "3 devices")],
        "img_kw": "wireless keyboard", "img_lk": 710,
    },
    {
        "name": "Logitech MX Mechanical Wireless Keyboard",
        "short": "Wireless mechanical keyboard with tactile or linear switches.",
        "desc": "MX Mechanical is the first MX keyboard with mechanical switches — choose Tactile Quiet, Linear, or Clicky. Smart backlight and multi-OS support included.",
        "cat": "keyboards-mice", "brand": "logitech",
        "price": "169.99", "discount": "139.99",
        "rating": "4.6", "reviews": 3400, "stock": 55, "pop": 880,
        "tags": ["keyboard", "mechanical", "wireless", "productivity"],
        "attrs": [("Layout", "Full-size"), ("Switches", "Tactile Quiet / Linear / Clicky"), ("Battery", "15 days with backlight"), ("Connectivity", "Logi Bolt / Bluetooth"), ("Multi-device", "3 devices")],
        "img_kw": "mechanical keyboard", "img_lk": 720,
    },
    {
        "name": "Apple Magic Keyboard with Touch ID",
        "short": "Wireless keyboard with Touch ID for instant secure login on Mac.",
        "desc": "Magic Keyboard with Touch ID features a redesigned scissor mechanism for a comfortable, responsive feel. Touch ID enables biometric authentication for fast, secure login.",
        "cat": "keyboards-mice", "brand": "apple",
        "price": "99.00", "discount": "85.00",
        "rating": "4.7", "reviews": 8900, "stock": 100, "pop": 920,
        "tags": ["keyboard", "wireless", "apple", "touch-id", "mac"],
        "attrs": [("Layout", "Full-size"), ("Connectivity", "Bluetooth"), ("Battery", "1 month"), ("Touch ID", "Yes"), ("Charging", "Lightning")],
        "img_kw": "apple magic keyboard", "img_lk": 730,
    },
    {
        "name": "Apple Magic Mouse",
        "short": "Multi-touch surface mouse that works wirelessly with Mac.",
        "desc": "Magic Mouse features a smooth Multi-Touch surface for swipe gestures and scroll in any direction. Rechargeable with Lightning, connects via Bluetooth.",
        "cat": "keyboards-mice", "brand": "apple",
        "price": "79.00", "discount": "69.00",
        "rating": "4.5", "reviews": 7100, "stock": 120, "pop": 890,
        "tags": ["mouse", "wireless", "apple", "multi-touch", "mac"],
        "attrs": [("Surface", "Multi-Touch"), ("Battery", "1 month"), ("Connectivity", "Bluetooth"), ("Charging", "Lightning"), ("Design", "Flat")],
        "img_kw": "apple magic mouse", "img_lk": 740,
    },
    {
        "name": "Microsoft Sculpt Ergonomic Desktop",
        "short": "Split keyboard and sculpted mouse for comfortable all-day typing.",
        "desc": "Sculpt Ergonomic Desktop positions hands and wrists naturally to reduce muscle strain. The domed keyboard and cushioned palm rest promote a healthy hand position.",
        "cat": "keyboards-mice", "brand": "microsoft",
        "price": "109.99", "discount": "89.99",
        "rating": "4.4", "reviews": 4200, "stock": 60, "pop": 820,
        "tags": ["keyboard", "ergonomic", "wireless", "split", "mouse-included"],
        "attrs": [("Layout", "Split ergonomic"), ("Connectivity", "USB dongle 2.4GHz"), ("Includes", "Keyboard + Mouse + Numpad"), ("Wrist Rest", "Built-in cushion")],
        "img_kw": "ergonomic keyboard", "img_lk": 750,
    },
    {
        "name": "Logitech G305 LIGHTSPEED Wireless Gaming Mouse",
        "short": "Hero sensor + LIGHTSPEED wireless at under $50.",
        "desc": "G305 features Logitech's HERO sensor with up to 12,000 DPI. LIGHTSPEED wireless delivers 1ms report rate at a budget-friendly price.",
        "cat": "keyboards-mice", "brand": "logitech",
        "price": "49.99", "discount": "39.99",
        "rating": "4.6", "reviews": 8400, "stock": 150, "pop": 890,
        "tags": ["mouse", "gaming", "wireless", "budget", "lightspeed"],
        "attrs": [("Sensor", "HERO (12,000 DPI)"), ("Weight", "99 g"), ("Battery", "250 hours"), ("Connectivity", "LIGHTSPEED Wireless"), ("Buttons", "6")],
        "img_kw": "gaming mouse", "img_lk": 760,
    },
    {
        "name": "Logitech MX Anywhere 3 Compact Mouse",
        "short": "Compact multi-device mouse with MagSpeed scroll for travel.",
        "desc": "MX Anywhere 3 features MagSpeed electromagnetic scrolling and works on any surface including glass. Pairs with up to 3 computers via Logi Bolt or Bluetooth.",
        "cat": "keyboards-mice", "brand": "logitech",
        "price": "79.99", "discount": "59.99",
        "rating": "4.6", "reviews": 5700, "stock": 95, "pop": 870,
        "tags": ["mouse", "wireless", "compact", "travel", "multi-device"],
        "attrs": [("DPI", "200–4,000"), ("Battery", "70 days"), ("Scroll", "MagSpeed"), ("Weight", "99 g"), ("Connectivity", "Logi Bolt / Bluetooth")],
        "img_kw": "wireless mouse", "img_lk": 770,
    },
    {
        "name": "Microsoft Arc Mouse",
        "short": "Ultra-slim flexible mouse that snaps flat for easy transport.",
        "desc": "Arc Mouse snaps flat for storage in your bag. When curved, it provides a natural hand position. BlueTrack technology works on most surfaces.",
        "cat": "keyboards-mice", "brand": "microsoft",
        "price": "79.99", "discount": "59.99",
        "rating": "4.3", "reviews": 2900, "stock": 75, "pop": 800,
        "tags": ["mouse", "wireless", "travel", "compact", "foldable"],
        "attrs": [("Design", "Flexible snap-flat"), ("Battery", "6 months"), ("Connectivity", "Bluetooth"), ("Surface", "BlueTrack"), ("Weight", "87 g")],
        "img_kw": "wireless mouse", "img_lk": 780,
    },
    {
        "name": "Anker Vertical Ergonomic Wireless Mouse",
        "short": "Vertical ergonomic mouse to reduce wrist strain at an affordable price.",
        "desc": "Anker's vertical ergonomic mouse positions the hand in a natural handshake position. 5-button design with adjustable DPI.",
        "cat": "keyboards-mice", "brand": "anker",
        "price": "29.99", "discount": "22.99",
        "rating": "4.4", "reviews": 9800, "stock": 200, "pop": 840,
        "tags": ["mouse", "ergonomic", "wireless", "vertical", "budget"],
        "attrs": [("Design", "Vertical"), ("DPI", "800 / 1200 / 1600"), ("Battery", "12 months"), ("Connectivity", "USB nano receiver"), ("Buttons", "5")],
        "img_kw": "ergonomic mouse", "img_lk": 790,
    },

    # ── Cables & Adapters ─────────────────────────────────────────────────────
    {
        "name": "Anker 10-in-1 USB-C Hub",
        "short": "Expand your laptop with 10 ports including 4K HDMI and SD card.",
        "desc": "Anker's 10-in-1 hub adds 4K HDMI, VGA, 2× USB 3.0, USB-C data, SD/microSD, Ethernet, and 100W Power Delivery to any USB-C laptop.",
        "cat": "cables-adapters", "brand": "anker",
        "price": "69.99", "discount": "49.99",
        "rating": "4.6", "reviews": 8900, "stock": 120, "pop": 930,
        "tags": ["usb-c", "hub", "hdmi", "adapter", "laptop"],
        "attrs": [("Ports", "10-in-1"), ("HDMI", "4K 30Hz"), ("USB 3.0", "2× ports"), ("Card Reader", "SD + microSD"), ("Power Delivery", "100 W passthrough")],
        "img_kw": "usb hub", "img_lk": 800,
    },
    {
        "name": "Anker 7-in-1 USB-C Hub Slim",
        "short": "Slim and portable USB-C hub for everyday use.",
        "desc": "The slim 7-in-1 hub features USB-C 100W Power Delivery, 4K HDMI, 3× USB-A 3.0, and SD/microSD card slots. Compact enough for any bag.",
        "cat": "cables-adapters", "brand": "anker",
        "price": "49.99", "discount": "39.99",
        "rating": "4.5", "reviews": 6200, "stock": 150, "pop": 900,
        "tags": ["usb-c", "hub", "hdmi", "portable", "slim"],
        "attrs": [("Ports", "7-in-1"), ("HDMI", "4K 30Hz"), ("USB-A", "3× USB 3.0"), ("Power Delivery", "100 W"), ("Dimensions", "Slim profile")],
        "img_kw": "usb hub", "img_lk": 810,
    },
    {
        "name": "Anker 65W GaN Wall Charger",
        "short": "Compact GaN charger with 65W USB-C + 12W USB-A.",
        "desc": "PowerPort III GaN uses gallium nitride technology to deliver 65W in a charger half the size of traditional adapters. Charges MacBook, iPad Pro, iPhone, and Android phones.",
        "cat": "cables-adapters", "brand": "anker",
        "price": "49.99", "discount": "39.99",
        "rating": "4.7", "reviews": 11000, "stock": 200, "pop": 940,
        "tags": ["charger", "gan", "usb-c", "fast-charge", "compact"],
        "attrs": [("USB-C Power", "65 W"), ("USB-A Power", "12 W"), ("Technology", "GaN"), ("Compatibility", "MacBook / iPad / iPhone / Android")],
        "img_kw": "phone charger", "img_lk": 820,
    },
    {
        "name": "Apple USB-C MagSafe 3 Charging Cable 2m",
        "short": "Magnetically attaches to your MacBook for 140W charging.",
        "desc": "The MagSafe 3 Cable connects magnetically and charges MacBook Pro at up to 140W. LED status indicator shows connection. Braided USB-C to MagSafe 3 connector.",
        "cat": "cables-adapters", "brand": "apple",
        "price": "49.00", "discount": "39.00",
        "rating": "4.7", "reviews": 5200, "stock": 90, "pop": 870,
        "tags": ["magsafe", "charging", "macbook", "cable", "apple"],
        "attrs": [("Connector", "USB-C to MagSafe 3"), ("Power", "Up to 140 W"), ("Length", "2 m"), ("Indicator", "Magnetic LED status")],
        "img_kw": "magsafe charger", "img_lk": 830,
    },
    {
        "name": "Anker USB-C to USB-C Cable 240W (6ft)",
        "short": "240W fast-charging braided USB-C cable for laptops.",
        "desc": "Supports 240W charging for the latest laptops and 40 Gbps data transfer with Thunderbolt 4. Double braided nylon jacket withstands 35,000+ bends.",
        "cat": "cables-adapters", "brand": "anker",
        "price": "25.99", "discount": "19.99",
        "rating": "4.6", "reviews": 4800, "stock": 250, "pop": 880,
        "tags": ["usb-c", "cable", "fast-charge", "240w", "thunderbolt"],
        "attrs": [("Power", "240 W"), ("Data", "40 Gbps (Thunderbolt 4)"), ("Length", "6 ft / 1.8 m"), ("Material", "Double braided nylon")],
        "img_kw": "usb cable", "img_lk": 840,
    },
    {
        "name": "Samsung 45W Super Fast Charging Adapter",
        "short": "USB-C 45W charger for Galaxy S and Note devices.",
        "desc": "Samsung 45W Super Fast Charging Adapter delivers rapid charge to Galaxy smartphones. USB-C PD 3.0 compatibility also charges many laptops.",
        "cat": "cables-adapters", "brand": "samsung",
        "price": "49.99", "discount": "39.99",
        "rating": "4.6", "reviews": 4100, "stock": 130, "pop": 860,
        "tags": ["charger", "usb-c", "45w", "samsung", "fast-charge"],
        "attrs": [("Power", "45 W"), ("Standard", "USB-C PD 3.0"), ("Compatibility", "Galaxy S / Note / Tab"), ("Cable Included", "USB-C (1 m)")],
        "img_kw": "phone charger", "img_lk": 850,
    },

    # ── Wearables ─────────────────────────────────────────────────────────────
    {
        "name": "Apple Watch Series 9 GPS 45mm",
        "short": "The most capable Apple Watch yet with double tap gesture.",
        "desc": "Apple Watch Series 9 features the new S9 chip and Double Tap gesture to control with one hand. Always-On Retina display, blood oxygen and ECG sensors, and crash detection.",
        "cat": "wearables", "brand": "apple",
        "price": "429.00", "discount": "379.00",
        "rating": "4.8", "reviews": 9800, "stock": 70, "pop": 975,
        "tags": ["smartwatch", "apple", "fitness", "health", "gps"],
        "attrs": [("Chip", "Apple S9"), ("Display", "Always-On Retina"), ("Health", "ECG + Blood Oxygen"), ("GPS", "Yes"), ("Water Resistance", "50 m")],
        "img_kw": "apple watch", "img_lk": 860,
    },
    {
        "name": "Samsung Galaxy Watch 6 Classic 47mm",
        "short": "Iconic rotating bezel smartwatch with advanced health tracking.",
        "desc": "Galaxy Watch 6 Classic brings back the beloved rotating bezel for intuitive control. Advanced sleep coaching, body composition analysis, and 24/7 heart rate monitoring.",
        "cat": "wearables", "brand": "samsung",
        "price": "399.99", "discount": "329.99",
        "rating": "4.6", "reviews": 3200, "stock": 45, "pop": 900,
        "tags": ["smartwatch", "samsung", "fitness", "health", "rotating-bezel"],
        "attrs": [("Display", "Super AMOLED 1.5\""), ("Bezel", "Physical rotating"), ("Health", "Body Composition + Sleep Coach"), ("Water Resistance", "5 ATM + IP68"), ("OS", "Wear OS + One UI Watch")],
        "img_kw": "smartwatch", "img_lk": 870,
    },
    {
        "name": "Apple Watch SE 2nd Gen GPS 44mm",
        "short": "The essential Apple Watch with crash and fall detection.",
        "desc": "Apple Watch SE is the affordable Apple Watch with the essential features. S8 chip, crash detection, fall detection, and comprehensive fitness tracking.",
        "cat": "wearables", "brand": "apple",
        "price": "279.00", "discount": "239.00",
        "rating": "4.7", "reviews": 6700, "stock": 90, "pop": 940,
        "tags": ["smartwatch", "apple", "fitness", "budget"],
        "attrs": [("Chip", "Apple S8"), ("Crash Detection", "Yes"), ("Fall Detection", "Yes"), ("GPS", "Yes"), ("Water Resistance", "50 m")],
        "img_kw": "apple watch", "img_lk": 880,
    },
]


class Command(BaseCommand):
    help = "Seed the catalog with 88 realistic tech products with matched images."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all products, categories, and brands before seeding.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing catalog data…")
            Product.objects.all().delete()
            Category.objects.all().delete()
            Brand.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared."))

        with transaction.atomic():
            cats   = self._seed_categories()
            brands = self._seed_brands()
            created, updated = self._seed_products(cats, brands)

        self.stdout.write(
            self.style.SUCCESS(
                f"Done — {created} created, {updated} updated "
                f"({created + updated} total products)."
            )
        )

    def _seed_categories(self) -> dict[str, Category]:
        cats: dict[str, Category] = {}
        for name, slug, parent_slug in CATEGORIES:
            parent = cats.get(parent_slug) if parent_slug else None
            obj, _ = Category.objects.update_or_create(
                slug=slug, defaults={"name": name, "parent": parent}
            )
            cats[slug] = obj
        self.stdout.write(f"  {len(cats)} categories ready.")
        return cats

    def _seed_brands(self) -> dict[str, Brand]:
        brands: dict[str, Brand] = {}
        for name, slug in BRANDS:
            obj, _ = Brand.objects.update_or_create(slug=slug, defaults={"name": name})
            brands[slug] = obj
        self.stdout.write(f"  {len(brands)} brands ready.")
        return brands

    def _seed_products(
        self,
        cats: dict[str, Category],
        brands: dict[str, Brand],
    ) -> tuple[int, int]:
        created_count = 0
        updated_count = 0

        for idx, item in enumerate(PRODUCTS):
            slug = slugify(item["name"])[:200] or f"product-{idx}"
            kw   = item["img_kw"]
            lk   = item["img_lk"]

            description = item.get(
                "desc",
                f"{item['short']} Full details, specifications, and warranty "
                f"information for {item['name']}.",
            )

            product, was_created = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    "name":              item["name"],
                    "short_description": item["short"],
                    "description":       description,
                    "category":          cats[item["cat"]],
                    "brand":             brands[item["brand"]],
                    "price":             Decimal(item["price"]),
                    "discount_price":    Decimal(item["discount"]) if item.get("discount") else None,
                    "rating":            Decimal(item["rating"]),
                    "review_count":      item["reviews"],
                    "stock_quantity":    item["stock"],
                    "is_active":         True,
                    "popularity_score":  item["pop"],
                },
            )

            # Refresh tags, attributes, and images on every run
            ProductTag.objects.filter(product=product).delete()
            ProductAttribute.objects.filter(product=product).delete()
            ProductImage.objects.filter(product=product).delete()

            for tag in item.get("tags", []):
                ProductTag.objects.get_or_create(
                    product=product, tag=tag.lower().replace(" ", "-")
                )

            for attr_name, attr_value in item.get("attrs", []):
                ProductAttribute.objects.create(
                    product=product,
                    attribute_name=attr_name,
                    attribute_value=attr_value,
                )

            # Three images per product — same keyword, different lock → gallery variety
            ProductImage.objects.create(
                product=product, image_url=_img(kw, lk),     is_primary=True
            )
            ProductImage.objects.create(
                product=product, image_url=_img(kw, lk + 1), is_primary=False
            )
            ProductImage.objects.create(
                product=product, image_url=_img(kw, lk + 2), is_primary=False
            )

            if was_created:
                created_count += 1
            else:
                updated_count += 1

        return created_count, updated_count
