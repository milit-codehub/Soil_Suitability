"""
gsd_engine.py - Stage 2 & 3: Calibration, GSD Metrics (d10, d50, d60, Cu) & USDA Textural Binning
"""
import numpy as np
import pandas as pd

def classify_soil_color(mean_r, mean_g, mean_b):
    """Classifies soil color tone and estimates organic matter / mineral content."""
    brightness = (mean_r + mean_g + mean_b) / 3.0
    
    if brightness < 90:
        tone = "Dark / Organic-Rich Soil"
        desc = "High organic carbon/humus content; higher moisture and nutrient retention."
    elif brightness > 160:
        tone = "Light / Mineral-Dominant Soil"
        desc = "High quartz or coarse sand mineral content; lower organic matter."
    elif mean_r > mean_g + 15 and mean_r > mean_b + 15:
        tone = "Reddish / Ferruginous Soil"
        desc = "Contains oxidized iron minerals (hematite); typically well-drained."
    else:
        tone = "Brownish / Balanced Soil"
        desc = "Balanced mix of hydrated iron oxides and organic matter."
        
    return tone, desc, round(brightness, 1)

def calculate_gsd_and_usda(df, scale_factor=0.02):
    """
    Computes scale conversion, cumulative mass proxy passing curve,
    d10, d50, d60 percentile diameters, Uniformity Coefficient Cu, and USDA texturing.
    """
    df["Area_mm2"] = df["Area"] * (scale_factor ** 2)
    df["d_eq_mm"] = 2 * np.sqrt(df["Area_mm2"] / np.pi)

    df_sorted = df.sort_values(by="d_eq_mm").reset_index(drop=True)
    df_sorted["weight_proxy"] = df_sorted["d_eq_mm"] ** 3
    total_weight = df_sorted["weight_proxy"].sum()

    df_sorted["cum_weight"] = df_sorted["weight_proxy"].cumsum()
    df_sorted["percent_passing"] = (df_sorted["cum_weight"] / total_weight) * 100

    d10 = np.interp(10, df_sorted["percent_passing"], df_sorted["d_eq_mm"])
    d50 = np.interp(50, df_sorted["percent_passing"], df_sorted["d_eq_mm"])
    d60 = np.interp(60, df_sorted["percent_passing"], df_sorted["d_eq_mm"])
    Cu = (d60 / d10) if d10 > 0 else np.nan

    fine_soil = df_sorted[df_sorted["d_eq_mm"] <= 2.0]
    total_fine_weight = fine_soil["weight_proxy"].sum()

    sand_mask = (fine_soil["d_eq_mm"] >= 0.05) & (fine_soil["d_eq_mm"] <= 2.0)
    silt_mask = (fine_soil["d_eq_mm"] >= 0.002) & (fine_soil["d_eq_mm"] < 0.05)
    clay_mask = (fine_soil["d_eq_mm"] < 0.002)

    pct_sand = (fine_soil.loc[sand_mask, "weight_proxy"].sum() / total_fine_weight) * 100 if total_fine_weight > 0 else 0
    pct_silt = (fine_soil.loc[silt_mask, "weight_proxy"].sum() / total_fine_weight) * 100 if total_fine_weight > 0 else 0
    pct_clay = (fine_soil.loc[clay_mask, "weight_proxy"].sum() / total_fine_weight) * 100 if total_fine_weight > 0 else 0

    texture_class = _classify_usda_triangle(pct_sand, pct_silt, pct_clay)

    if "Mean_R" in df.columns:
        avg_r = int(df["Mean_R"].mean())
        avg_g = int(df["Mean_G"].mean())
        avg_b = int(df["Mean_B"].mean())
        color_tone, color_desc, avg_brightness = classify_soil_color(avg_r, avg_g, avg_b)
    else:
        avg_r, avg_g, avg_b = 120, 100, 80
        color_tone, color_desc, avg_brightness = "Brownish / Balanced Soil", "Standard soil mix.", 100.0

    return {
        'd10': d10,
        'd50': d50,
        'd60': d60,
        'Cu': Cu,
        'pct_sand': pct_sand,
        'pct_silt': pct_silt,
        'pct_clay': pct_clay,
        'texture_class': texture_class,
        'df_sorted': df_sorted,
        'avg_r': avg_r,
        'avg_g': avg_g,
        'avg_b': avg_b,
        'color_tone': color_tone,
        'color_desc': color_desc,
        'avg_brightness': avg_brightness
    }

def _classify_usda_triangle(sand, silt, clay):
    if silt + 1.5 * clay < 15:
        return "Sand"
    elif silt + 1.5 * clay >= 15 and silt + 2 * clay < 30:
        return "Loamy Sand"
    elif (clay >= 7 and clay < 20 and sand > 52 and silt + 2 * clay >= 30) or (clay < 7 and silt < 50 and silt + 2 * clay >= 30):
        return "Sandy Loam"
    elif clay >= 7 and clay < 27 and silt >= 28 and silt < 50 and sand <= 52:
        return "Loam"
    elif silt >= 50 and clay >= 12 and clay < 27:
        return "Silt Loam"
    elif silt >= 80 and clay < 12:
        return "Silt"
    elif clay >= 20 and clay < 35 and silt < 28 and sand >= 45:
        return "Sandy Clay Loam"
    elif clay >= 27 and clay < 40 and sand > 20 and sand <= 45:
        return "Clay Loam"
    elif clay >= 27 and clay < 40 and sand <= 20:
        return "Silty Clay Loam"
    elif clay >= 35 and sand >= 45:
        return "Sandy Clay"
    elif clay >= 40 and silt >= 40:
        return "Silty Clay"
    elif clay >= 40 and sand <= 45 and silt < 40:
        return "Clay"
    else:
        return "Loam (General)"
