import os
import json
import requests
import streamlit as st

def generate_llm_advisory(metrics):
    """
    Sends calculated soil transport and physical metrics to Gemini API
    and returns a tailored agronomic advisory report.
    Supports both standard developer keys (AIzaSy...) and GCP keys (AQ...).
    """
    # 1. Retrieve API key from environment variable or Streamlit secrets
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key and hasattr(st, "secrets"):
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            pass

    if not api_key:
        return (
            "⚠️ **API Key Not Found**\n\n"
            "Please set your `GEMINI_API_KEY` in your terminal or Streamlit secrets.\n"
            "Get a free key at [aistudio.google.com](https://aistudio.google.com/)."
        )

    # Clean the API key (remove accidental quotes or whitespace)
    api_key = api_key.strip().strip('"').strip("'")

    # 2. Construct structured engineering prompt
    prompt_text = f"""
    You are an expert Soil Scientist and Agricultural Engineer advising a local farmer.
    Analyze the following image-derived soil metrics:
    
    --- SOIL PHYSICAL & GEOTECHNICAL METRICS ---
    - USDA Soil Texture Class: {metrics.get('texture_class', 'N/A')}
    - Particle Composition: {metrics.get('pct_sand', 0):.1f}% Sand, {metrics.get('pct_silt', 0):.1f}% Silt, {metrics.get('pct_clay', 0):.1f}% Clay
    - Median Grain Size (d50): {metrics.get('d50', 0):.3f} mm
    - Effective Size (d10): {metrics.get('d10', 0):.3f} mm
    - Uniformity Coefficient (Cu): {metrics.get('Cu', 0):.2f}
    - Soil Color Tone: {metrics.get('color_tone', 'Unknown')}
    
    --- TRANSPORT METRICS ---
    - Hydraulic Conductivity (K): {metrics.get('K', 'N/A')} cm/s
    - Specific Surface Area (SSA): {metrics.get('SSA', 'N/A')} m²/g
    
    --- TASK ---
    Provide a concise, professional 3-point advice report:
    1. **Water & Irrigation Strategy**: Percolation risks based on K and grain size.
    2. **Fertilizer & Retention Advisory**: Application timing (split vs. single dosing) based on SSA and color tone.
    3. **Recommended Crops & Soil Amendments**: 2-3 optimal crops and physical/chemical soil conditioning (e.g., biochar, compost, liming).
    """

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    # List of candidate models to try in order of preference
    candidate_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    
    last_error = ""

    # 3. Try standard Google AI Studio endpoint across candidate models
    for model in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                res_data = response.json()
                try:
                    return res_data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError):
                    return "⚠️ Received empty response structure from Gemini API."
            else:
                err_data = response.json().get("error", {})
                last_error = err_data.get("message", response.text)
                # If it's a 401 or 403, breaking early to handle auth issue
                if response.status_code in (401, 403):
                    break
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            continue

    # 4. If 404 occurs across models, or if it's a GCP key (AQ...), try v1 endpoint or give clear diagnosis
    if "404" in str(last_error) or "not found" in str(last_error).lower():
        # Try v1 endpoint as fallback
        url_v1 = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
        try:
            response_v1 = requests.post(url_v1, headers=headers, json=payload, timeout=30)
            if response_v1.status_code == 200:
                return response_v1.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            pass

        return (
            "❌ **API Model 404 Error**\n\n"
            f"**Error Details**: `{last_error}`\n\n"
            "### 🛠️ How to Fix This:\n"
            "1. **Enable Generative Language API**: If your key is from Google Cloud Console, ensure the **Generative Language API** is enabled for your project.\n"
            "2. **Get an AI Studio Key**: Go to [aistudio.google.com](https://aistudio.google.com/), click **Create API Key in new project**, and copy the resulting `AIzaSy...` key.\n"
            "3. **Update Terminal / Secrets**: Set `GEMINI_API_KEY` to the new `AIzaSy...` key."
        )

    if "API key not valid" in last_error or "401" in last_error or "403" in last_error:
        return (
            "❌ **Authentication Error (401/403)**\n\n"
            f"**Error Details**: `{last_error}`\n\n"
            "### 🛠️ How to Fix This:\n"
            "1. Visit [aistudio.google.com](https://aistudio.google.com/).\n"
            "2. Click **Create API Key** -> **Create API Key in new project**.\n"
            "3. Set `$env:GEMINI_API_KEY=\"AIzaSy...\"` in PowerShell and restart Streamlit."
        )

    return f"❌ **API Error**: {last_error}"
