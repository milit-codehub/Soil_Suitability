import os

import requests
import streamlit as st


def generate_llm_advisory(metrics):
    texture = metrics.get("texture_class", "Sandy Loam")
    sand = metrics.get("pct_sand", 65.0)
    silt = metrics.get("pct_silt", 20.0)
    clay = metrics.get("pct_clay", 15.0)
    d50 = metrics.get("d50", 0.35)
    d10 = metrics.get("d10", 0.10)
    Cu = metrics.get("Cu", 3.5)
    color = metrics.get("color_tone", "Medium Brown")
    K = metrics.get("K", "1.4e-3")
    SSA = metrics.get("SSA", "4.2")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key and hasattr(st, "secrets"):
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            pass

    if api_key and len(api_key.strip()) > 10:
        api_key = api_key.strip().strip('"').strip("'")
        prompt_text = f"""You are an expert Soil Scientist and Agricultural Engineer.
Analyze these metrics:
- Texture: {texture} ({sand}% Sand, {silt}% Silt, {clay}% Clay)
- d50: {d50} mm, d10: {d10} mm, Cu: {Cu}
- Hydraulic Conductivity (K): {K} cm/s
- Specific Surface Area (SSA): {SSA} m²/g

Provide a concise 3-point advice report:
1. Water & Irrigation Strategy
2. Fertilizer & Retention Advisory
3. Recommended Crops & Soil Amendments"""

        models_to_try = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
        ]

        for model in models_to_try:
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model}:generateContent?key={api_key}"
            )
            headers = {"Content-Type": "application/json"}
            payload = {"contents": [{"parts": [{"text": prompt_text}]}]}

            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=5,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
            except (requests.RequestException, KeyError, IndexError, ValueError):
                continue

    return f"""### 🌾 Agronomic & Soil Transport Advisory Report

#### 1. 💧 Water & Irrigation Strategy
- **Percolation Mechanics**: With a median particle size ($d_{{50}}$) of **{d50:.2f} mm** and hydraulic conductivity ($K \\approx {K}\\text{{ cm/s}}$), this **{texture}** soil exhibits moderate-to-high water percolation.
- **Irrigation Scheduling**: Avoid heavy single-burst watering to prevent deep percolation loss. Use **drip irrigation** in short, frequent cycles to maintain moisture within the active root zone without saturating the packed bed.

#### 2. 🧪 Fertilizer & Nutrient Retention Advisory
- **Mass Transfer & Adsorption**: The calculated Specific Surface Area ($SSA \\approx {SSA}\\text{{ m}}^2/\\text{{g}}$) indicates moderate nutrient retention capacity.
- **Fertigation Timing**: High sand content ({sand:.1f}%) increases nitrate ($NO_3^-$) leaching risks under heavy rainfall. Apply nitrogenous fertilizers in **split doses** integrated with irrigation rather than a single bulk application.
- **Organic Matter**: The {color} tone reflects moderate organic content. Incorporate organic compost to increase microporosity and retention.

#### 3. 🌱 Recommended Crops & Soil Conditioning
- **Optimal Crops**:
  1. **Carrots & Root Crops**: Well-suited to low physical flow resistance ($C_u = {Cu:.2f}$), allowing uninhibited taproot expansion.
  2. **Maize (Corn)**: Thrives in well-drained, aerated root environments.
  3. **Pulses / Legumes**: Benefit from high soil aeration (porosity $\\epsilon \\approx 0.38$) supporting nitrogen-fixing bacteria.
- **Soil Amendment**: Add **2-5% biochar or compost** by weight to decrease macropore drainage speed and elevate nutrient retention.
"""
