"""
crop_recommender.py - Stage 4: FAO Crop Suitability Rule Engine
"""
from config import CROP_RULES

def evaluate_crop_suitability(usda_texture, Cu):
    """
    Evaluates FAO crop suitability ratings based on USDA texture class and Uniformity Coefficient Cu.
    """
    if usda_texture in ["Sandy Loam", "Loamy Sand", "Sand"]:
        recs = CROP_RULES["SANDY"]
    elif usda_texture in ["Loam", "Silt Loam"]:
        recs = CROP_RULES["LOAMY"]
    elif usda_texture in ["Clay", "Silty Clay", "Clay Loam"]:
        recs = CROP_RULES["CLAYEY"]
    else:
        recs = CROP_RULES["DEFAULT"]

    packing_note = (
        "Uniform particle size distribution (Cu < 4) - promotes macro-porosity and rapid infiltration."
        if Cu < 4 else
        "Well-graded soil (Cu >= 4) - exhibits higher packing density and potential compaction."
    )
    return recs, packing_note
