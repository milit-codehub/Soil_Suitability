"""
app.py - Clean Modular Streamlit UI Frontend (Student Version)
"""
import pandas as pd
import streamlit as st

from config import DEFAULT_SCALE_FACTOR, DEFAULT_MIN_AREA_PX
from image_processing import segment_and_extract_features
from gsd_engine import calculate_gsd_and_usda
from crop_recommender import evaluate_crop_suitability
from visualization import generate_diagnostic_plots

st.set_page_config(
    page_title="Soil Particle Analyzer",
    layout="wide"
)

def main():
    st.title("Soil Particle Analysis & Crop Suitability")
    st.caption("Exploratory Project | Milit Srivastava, Viral Chauhan, Aditya Singh")

    # Sidebar Configuration
    st.sidebar.header("Input Settings")
    input_mode = st.sidebar.radio("Input Source", ["Image Upload", "CSV Upload"])

    scale_factor = st.sidebar.number_input(
        "Scale Factor (mm/pixel)", 
        min_value=0.0001, 
        max_value=1.0, 
        value=DEFAULT_SCALE_FACTOR, 
        step=0.005,
        format="%.4f",
        help="Example: 10mm scale bar / 500 pixels = 0.02 mm/px"
    )

    min_area_px = st.sidebar.number_input(
        "Min Particle Area Filter (px²)",
        min_value=1,
        max_value=100,
        value=DEFAULT_MIN_AREA_PX,
        step=1
    )

    df_particles = None
    orig_img = None
    overlay_img = None

    # Input Processing
    if input_mode == "Image Upload":
        uploaded_file = st.file_uploader("Upload Soil Photograph (.jpg, .png)", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image_bytes = uploaded_file.read()
            with st.spinner("Processing image and segmenting soil particles..."):
                df_particles, overlay_img, orig_img = segment_and_extract_features(image_bytes, min_area_px=min_area_px)
            st.success(f"Successfully detected {len(df_particles)} soil particles!")
    else:
        uploaded_csv = st.file_uploader("Upload Particle Measurements CSV", type=["csv"])
        if uploaded_csv is not None:
            df_particles = pd.read_csv(uploaded_csv)
            st.success(f"Successfully loaded CSV dataset with {len(df_particles)} particle rows!")

    # Dashboard Display
    if df_particles is not None and not df_particles.empty:
        st.write("---")

        # Image Previews
        if overlay_img is not None:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Original Image")
                st.image(orig_img, use_container_width=True)
            with col2:
                st.subheader("Particle Detection Overlay")
                st.image(overlay_img, use_container_width=True)

        # Calculate GSD & USDA Metrics
        metrics = calculate_gsd_and_usda(df_particles, scale_factor=scale_factor)
        recs, packing_note = evaluate_crop_suitability(metrics['texture_class'], metrics['Cu'])

        st.subheader("Soil Classification & Metrics")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**USDA Soil Texture:** {metrics['texture_class']}")
            st.markdown(f"**Total Particles Detected:** {len(df_particles):,}")
            st.markdown(f"**d10 (Effective Size):** {metrics['d10']:.3f} mm")
            st.markdown(f"**d50 (Median Size):** {metrics['d50']:.3f} mm")
            st.markdown(f"**d60:** {metrics['d60']:.3f} mm")
            st.markdown(f"**Uniformity Coefficient (Cu):** {metrics['Cu']:.2f}")

        with col_b:
            st.markdown("**Particle Size Fractions:**")
            st.write(f"- Sand (0.05 - 2.0 mm): {metrics['pct_sand']:.1f}%")
            st.write(f"- Silt (0.002 - 0.05 mm): {metrics['pct_silt']:.1f}%")
            st.write(f"- Clay (< 0.002 mm): {metrics['pct_clay']:.1f}%")

        st.write("---")
        st.subheader("Grain Size Distribution & Particle Histogram")

        fig = generate_diagnostic_plots(
            metrics['df_sorted'], df_particles,
            metrics['d10'], metrics['d50'], metrics['d60']
        )
        st.pyplot(fig)

        # --- NEW: Soil Color & RGB Analysis Block ---
        st.write("---")
        st.subheader("🎨 Soil Color & RGB Analysis")
        col_c1, col_c2 = st.columns([1, 3])

        with col_c1:
            hex_color = f"#{metrics['avg_r']:02x}{metrics['avg_g']:02x}{metrics['avg_b']:02x}"
            st.markdown(
                f"""
                <div style="background-color:{hex_color}; width:100%; height:75px; 
                            border-radius:6px; border: 1px solid #ccc;"></div>
                """,
                unsafe_allow_html=True
            )
            st.caption(f"Color Swatch | RGB: ({metrics['avg_r']}, {metrics['avg_g']}, {metrics['avg_b']})")

        with col_c2:
            st.markdown(f"**Soil Tone Classification:** {metrics['color_tone']}")
            st.write(f"• **Mean RGB Brightness:** {metrics['avg_brightness']} / 255")
            st.write(f"• **Agronomic Context:** {metrics['color_desc']}")

        st.write("---")
        st.subheader("Crop Suitability Recommendations")
        st.caption(f"Soil Structure Note: {packing_note}")

        for rec in recs:
            st.markdown(f"**{rec['crop']}** — *{rec['rating']}*")
            st.write(f"{rec['reason']}")
            st.write("")

        st.write("---")
        csv_bytes = df_particles.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Particle Measurements (CSV)",
            data=csv_bytes,
            file_name="soil_particles_measured.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
