# CSI-DiCRA-Project

# 🌍 MP-CSI: National Climate Stack for Madhya Pradesh
**A Spatiotemporal Machine Learning Pipeline for Parametric Crop Insurance**

### 🚀 [Live Dashboard Link](https://csi-dicra-project-sdtgvwqqobb7evmvetud5g.streamlit.app/) 

## 📌 Project Overview
This project solves the **"Basis Risk"** failure in India's PMFBY insurance scheme. Current models use area-average rainfall, which misses localized compound heat-drought shocks. 

**Our Solution:** A Compound Stress Index (CSI) that identifies high-risk events by cross-referencing 15 years of daily climate vectors with district-specific phenology (crop growth) windows.

## 🛠 Tech Stack
- **Data Engineering:** GeoPandas, Rasterstats, Xarray (Zonal Statistics on 15-year NASA/DiCRA backbones)
- **ML Engine:** XGBoost Classifier (Trained on 280,000+ daily observations)
- **Deployment:** FastAPI (Backend), Docker (Containerization), Streamlit (Frontend)

## 📊 Key Results (Back-testing 2021-2024)
- **Precision:** 0.84 (High confidence in detected failure events)
- **Recall:** 0.62 (Successfully captures the majority of yield-destroying shocks)
- **Top Driver:** Compound Heat-Moisture Anomaly during the flowering phase.

## 📁 Repository Structure
- `/notebooks`: Data cleaning, 15-year feature engineering, and model validation.
- `/src`: Production FastAPI code and the trained XGBoost `.json` model.
- `/data`: GeoJSON district boundaries and processed master tables. 