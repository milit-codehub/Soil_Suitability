"""
image_processing.py - Stage 1: OpenCV Segmentation & Feature Extraction
"""
import cv2
import numpy as np
import pandas as pd

def segment_and_extract_features(image_input, min_area_px=5):
    """
    Takes image bytes or file path, runs OpenCV binarization & contour detection,
    and extracts 15 geometric particle features.
    """
    if isinstance(image_input, bytes):
        file_bytes = np.asarray(bytearray(image_input), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    elif isinstance(image_input, str):
        img = cv2.imread(image_input)
    else:
        img = image_input

    if img is None:
        raise ValueError("Could not decode image.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

    contours, _ = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    overlay_img = img.copy()
    records = []

    for idx, cnt in enumerate(contours, start=1):
        area_px = cv2.contourArea(cnt)
        if area_px < min_area_px:
            continue

        cv2.drawContours(overlay_img, [cnt], -1, (0, 255, 0), 1)
        perim_px = cv2.arcLength(cnt, True)
        circ = (4.0 * np.pi * area_px) / (perim_px ** 2) if perim_px > 0 else 0.0

        if len(cnt) >= 5:
            (cx, cy), (d1, d2), angle = cv2.fitEllipse(cnt)
            major_px, minor_px = max(d1, d2), min(d1, d2)
        else:
            major_px, minor_px, angle = np.nan, np.nan, np.nan

        ar = (major_px / minor_px) if (minor_px and not np.isnan(minor_px) and minor_px > 0) else np.nan
        roundness = (4.0 * area_px) / (np.pi * (major_px ** 2)) if (major_px and not np.isnan(major_px) and major_px > 0) else np.nan

        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        solidity = (area_px / hull_area) if hull_area > 0 else np.nan

        rect = cv2.minAreaRect(cnt)
        (rcx, rcy), (w, h), feret_angle = rect
        feret_max_px, min_feret_px = max(w, h), min(w, h)

        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.drawContours(mask, [cnt], -1, 255, -1) 

        mean_bgr = cv2.mean(img, mask=mask) 
        b, g, r = mean_bgr[0], mean_bgr[1], mean_bgr[2]

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) 
        mean_hsv = cv2.mean(hsv, mask=mask) 
        h, s, v = mean_hsv[0], mean_hsv[1], mean_hsv[2]

        records.append({
            '': idx,
            'Area': area_px,
            'Perim.': perim_px,
            'Major': major_px,
            'Minor': minor_px,
            'Angle': angle,
            'Circ.': circ,
            'Feret': feret_max_px,
            'FeretX': int(rcx),
            'FeretY': int(rcy),
            'FeretAngle': feret_angle,
            'MinFeret': min_feret_px,
            'AR': ar,
            'Round': roundness,
            'Solidity': solidity,
            'Mean_R': round(r, 1),
            'Mean_G': round(g, 1),
            'Mean_B': round(b, 1),
            'Mean_Hue': round(h, 1),
            'Mean_Sat': round(s, 1),
            'Mean_Val': round(v, 1)
        })

    df = pd.DataFrame(records)
    overlay_rgb = cv2.cvtColor(overlay_img, cv2.COLOR_BGR2RGB)
    orig_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return df, overlay_rgb, orig_rgb
