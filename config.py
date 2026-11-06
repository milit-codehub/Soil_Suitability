"""
config.py - Configuration Constants & Crop Suitability Matrix Rules
"""

DEFAULT_SCALE_FACTOR = 0.02  # mm/pixel
DEFAULT_MIN_AREA_PX = 5      # minimum particle area filter in pixels

# USDA Particle Size Bin Thresholds (in mm)
SAND_MIN_MM = 0.05
SAND_MAX_MM = 2.0
SILT_MIN_MM = 0.002
SILT_MAX_MM = 0.05
CLAY_MAX_MM = 0.002

# FAO Crop Suitability Matrix
CROP_RULES = {
    "SANDY": [
        {"crop": "Root & Tuber Crops (Carrots, Potatoes, Peanuts)", "rating": "S1 (Highly Suitable)", "badge": "🟢", "reason": "Friable, low soil impedance allows unrestricted root/tuber expansion."},
        {"crop": "Legumes & Pulses (Chickpeas, Cowpeas)", "rating": "S1 (Highly Suitable)", "badge": "🟢", "reason": "Excellent aeration prevents root rot and aids nitrogen nodulation."},
        {"crop": "Cereal Crops (Maize, Wheat, Barley)", "rating": "S2 (Moderately Suitable)", "badge": "🟡", "reason": "Good aeration; higher permeability may require supplementary irrigation."},
        {"crop": "Wetland Paddy Rice", "rating": "N (Not Suitable)", "badge": "🔴", "reason": "High percolation rate restricts standing water retention required for rice paddy."}
    ],
    "LOAMY": [
        {"crop": "Cereal Crops (Maize, Wheat, Barley)", "rating": "S1 (Highly Suitable)", "badge": "🟢", "reason": "Ideal balance of water retention, porosity, and nutrient availability."},
        {"crop": "Pulses & Oilseeds (Soybeans, Mustard)", "rating": "S1 (Highly Suitable)", "badge": "🟢", "reason": "Optimal moisture retention and root aeration."},
        {"crop": "Root Crops (Radish, Beetroot)", "rating": "S2 (Moderately Suitable)", "badge": "🟡", "reason": "Favorable growth environment provided soil remains friable."}
    ],
    "CLAYEY": [
        {"crop": "Wetland Paddy Rice", "rating": "S1 (Highly Suitable)", "badge": "🟢", "reason": "Fine texture and low permeability support flooded field conditions."},
        {"crop": "Sugarcane", "rating": "S1 (Highly Suitable)", "badge": "🟢", "reason": "High moisture retention capacity supports heavy nutrient intake."},
        {"crop": "Root & Tuber Crops", "rating": "N (Not Suitable)", "badge": "🔴", "reason": "High mechanical resistance and soil compaction restrict root penetration."}
    ],
    "DEFAULT": [
        {"crop": "General Field Crops (Wheat, Sorghum)", "rating": "S2 (Moderately Suitable)", "badge": "🟡", "reason": "Medium texture supports standard agronomic practices."}
    ]
}
