import os
import streamlit as st

def get_api_key():
    """Retrieve Gemini API key from Streamlit secrets or environment variables."""
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY", None)

def generate_llm_advisory(metrics):
    """
    Generates a personalized agronomic advisory report by passing soil physical,
    geotechnical, and transport metrics to the Gemini LLM API.
    """
    api_key = get_api_key()
    if not api_key:
        return (
            "⚠️ **API Key Missing**: Could not find `GEMINI_API_KEY`.\n\n"
            "**How to set up your free key:**\n"
            "1. Get a free API Key from [Google AI Studio](https://aistudio.google.com/).\n"
            "2. **For Local Testing:** Run `export GEMINI_API_KEY='your_key'` in terminal.\n"
            "3. **For Streamlit Cloud:** Add `GEMINI_API_KEY = 'your_key'` under App Settings -> Secrets."
        )

    # Extract parameters safely
    texture_class = metrics.get('texture_class', 'Unknown')
    pct_sand = metrics.get('pct_sand', 0)
    pct_silt = metrics.get('pct_silt', 0)
    pct_clay = metrics.get('pct_clay', 0)
    d50 = metrics.get('d50', 0)
    d10 = metrics.get('d10', 0)
    Cu = metrics.get('Cu', 0)
    color_tone = metrics.get('color_tone', 'Balanced Soil')
    brightness = metrics.get('avg_brightness', 100)
    color_desc = metrics.get('color_desc', 'Standard soil mix')
    K = metrics.get('K_cm_s', 'Not calculated')
    SSA = metrics.get('SSA_m2_g', 'Not calculated')
    porosity = metrics.get('porosity', 'Not calculated')

    prompt = f"""
You are an expert Agricultural Engineer and Chemical Transport Specialist advising a local farmer.
Analyze the following image-derived soil physical parameters and chemical engineering transport metrics:

--- SOIL GEOMETRY & TEXTURE METRICS ---
- USDA Soil Texture Class: {texture_class}
- Particle Composition: {pct_sand:.1f}% Sand, {pct_silt:.1f}% Silt, {pct_clay:.1f}% Clay
- Median Particle Size (d50): {d50:.3f} mm
- Effective Particle Size (d10): {d10:.3f} mm
- Uniformity Coefficient (Cu = d60/d10): {Cu:.2f}

--- SOIL COLOR & OPTICAL METRICS ---
- Soil Tone Classification: {color_tone}
- Mean RGB Brightness: {brightness:.1f} / 255
- Optical Tone Description: {color_desc}

--- TRANSPORT & CHEMICAL ENGINEERING PARAMETERS ---
- Hydraulic Conductivity (K): {K} cm/s (Kozeny-Carman transport model)
- Specific Surface Area (SSA): {SSA} m²/g
- Estimated Porosity (ε): {porosity}

--- INSTRUCTIONS ---
Based strictly on these physical and transport properties, generate a structured, professional agronomic advisory report in Markdown:
1. **Irrigation & Water Management Strategy**: Explain water percolation rates, drainage risk, and watering frequency based on Hydraulic Conductivity (K) and effective grain size (d10).
2. **Fertilizer & Nutrient Retention Advisory**: Explain nutrient leaching risk and fertilizer timing (e.g., split dosing vs. single application) based on Specific Surface Area (SSA) and soil organic tone.
3. **Optimal Crops & Soil Conditioning**: List 2-3 suitable crops and recommend physical/chemical amendments (e.g., organic compost, liming, or biochar).
4. **Chemical Engineering Physics Summary**: Briefly explain the fluid transport mechanics (e.g., hydraulic resistance, Kozeny-Carman flow) underlying your advice.
"""

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except ImportError:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as legacy_err:
            return f"❌ Error executing Generative AI call: {str(legacy_err)}"
    except Exception as err:
        return f"❌ Error communicating with Gemini API: {str(err)}"
