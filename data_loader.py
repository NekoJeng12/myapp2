"""
Data Loader and Preprocessor for Thailand Rainfall Intelligence Dashboard
"""
import os
import pandas as pd
import numpy as np
import streamlit as st
from config import PROVINCE_GEO, MONTH_NAMES, SEASON_MAPPING, PROV_ID_TO_NAME

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data(show_spinner="กำลังโหลดข้อมูลปริมาณน้ำฝนรายจังหวัด...")
def load_province_rainfall() -> pd.DataFrame:
    """
    Loads spatial rainfall data (2018-2026), 30-year climate normal baseline,
    and merges geographic metadata (region, lat, lon).
    """
    spatial_path = os.path.join(CURRENT_DIR, 'spatial-rain-hii.csv')
    avg30_path = os.path.join(CURRENT_DIR, 'avg30y_2020_update202111_province.csv')
    
    # Load raw CSVs
    df_spatial = pd.read_csv(spatial_path, encoding='utf-8-sig')
    df_avg30 = pd.read_csv(avg30_path, encoding='utf-8-sig')
    
    # Clean baseline columns
    df_avg30 = df_avg30.rename(columns={
        'MEAN': 'Normal_30Y_Mean',
        'MIN': 'Normal_30Y_Min',
        'MAX': 'Normal_30Y_Max'
    })
    
    # Merge with 30-year climate normal baseline
    merged = pd.merge(
        df_spatial,
        df_avg30[['MONTH', 'PROV_CODE', 'Normal_30Y_Mean', 'Normal_30Y_Min', 'Normal_30Y_Max']],
        left_on=['MONTH', 'PROV_ID'],
        right_on=['MONTH', 'PROV_CODE'],
        how='left'
    )
    if 'PROV_CODE' in merged.columns:
        merged = merged.drop(columns=['PROV_CODE'])
        
    # Map regions and coordinates
    merged['Region'] = merged['PROV_T'].map(lambda p: PROVINCE_GEO.get(p, {}).get('region', 'อื่นๆ'))
    merged['Latitude'] = merged['PROV_T'].map(lambda p: PROVINCE_GEO.get(p, {}).get('lat', 13.0))
    merged['Longitude'] = merged['PROV_T'].map(lambda p: PROVINCE_GEO.get(p, {}).get('lon', 101.0))
    
    # Calculate Climate Anomalies (Actual - Normal baseline)
    merged['Rain_Anomaly'] = merged['AvgRain'] - merged['Normal_30Y_Mean']
    merged['Rain_Anomaly_Pct'] = (merged['Rain_Anomaly'] / merged['Normal_30Y_Mean'].replace(0, 0.001)) * 100
    
    # Add localized month & season representations
    merged['Month_TH'] = merged['MONTH'].map(lambda m: MONTH_NAMES[m]['th'])
    merged['Month_EN'] = merged['MONTH'].map(lambda m: MONTH_NAMES[m]['en'])
    merged['Month_Short'] = merged['MONTH'].map(lambda m: MONTH_NAMES[m]['short'])
    merged['Season'] = merged['MONTH'].map(lambda m: SEASON_MAPPING[m]['season'])
    merged['Season_Icon'] = merged['MONTH'].map(lambda m: SEASON_MAPPING[m]['icon'])
    merged['Period'] = merged['YEAR'].astype(str) + '-' + merged['MONTH'].apply(lambda x: f"{x:02d}")
    
    return merged

@st.cache_data(show_spinner="กำลังโหลดข้อมูลอนุกรมเวลาระดับประเทศ (1970-2025)...")
def load_historical_national() -> pd.DataFrame:
    """
    Loads nationwide long-term rainfall time series (1970-2025)
    and computes rolling averages and decades.
    """
    hist_path = os.path.join(CURRENT_DIR, 'o_th1970-current_thai.csv')
    df_hist = pd.read_csv(hist_path, encoding='utf-8-sig')
    
    # Parse date
    df_hist['Date'] = pd.to_datetime(df_hist['YEAR'].astype(str) + '-' + df_hist['MONTH'].astype(str) + '-01')
    df_hist = df_hist.sort_values('Date').reset_index(drop=True)
    
    # Decades and seasonal info
    df_hist['Decade'] = (df_hist['YEAR'] // 10) * 10
    df_hist['Decade_Str'] = df_hist['Decade'].astype(str) + 's'
    df_hist['Month_TH'] = df_hist['MONTH'].map(lambda m: MONTH_NAMES[m]['th'])
    df_hist['Month_Short'] = df_hist['MONTH'].map(lambda m: MONTH_NAMES[m]['short'])
    df_hist['Season'] = df_hist['MONTH'].map(lambda m: SEASON_MAPPING[m]['season'])
    
    # 12-month and 60-month (5-year) rolling averages
    df_hist['Roll12_Mean'] = df_hist['MEAN'].rolling(window=12, min_periods=6).mean()
    df_hist['Roll60_Mean'] = df_hist['MEAN'].rolling(window=60, min_periods=24).mean()
    
    return df_hist

@st.cache_data(show_spinner="กำลังโหลดสถิติระดับอำเภอ...")
def load_amphoe_processed() -> pd.DataFrame:
    """
    Loads district-level rainfall (2010-2014) and maps province names.
    """
    amphoe_path = os.path.join(CURRENT_DIR, 'monthlyrain_amphoe_2010to2014.csv')
    df_amphoe = pd.read_csv(amphoe_path, encoding='utf-8-sig')
    df_amphoe['PROV_ID'] = df_amphoe['amphoe_code'] // 100
    df_amphoe['PROV_T'] = df_amphoe['PROV_ID'].map(PROV_ID_TO_NAME)
    df_amphoe['Region'] = df_amphoe['PROV_T'].map(lambda p: PROVINCE_GEO.get(p, {}).get('region', 'อื่นๆ'))
    df_amphoe['Month_TH'] = df_amphoe['month'].map(lambda m: MONTH_NAMES.get(m, {}).get('th', f'เดือน {m}'))
    return df_amphoe

def compute_forecast_projection(df_hist: pd.DataFrame, months_ahead: int = 12) -> pd.DataFrame:
    """
    Computes a 12-month forward predictive projection based on seasonal decomposition
    and modern decadal trend drift.
    """
    seasonal_means = df_hist.groupby('MONTH')['MEAN'].mean()
    seasonal_stds = df_hist.groupby('MONTH')['MEAN'].std()
    
    # Trend from recent 10 years (2015-2025)
    recent = df_hist[df_hist['YEAR'] >= 2015].copy()
    x = np.arange(len(recent))
    y = recent['MEAN'].values
    poly = np.polyfit(x, y, 1)
    
    last_year = int(df_hist['YEAR'].max())
    last_month = int(df_hist[df_hist['YEAR'] == last_year]['MONTH'].max())
    
    forecast_rows = []
    for i in range(1, months_ahead + 1):
        target_m = (last_month + i - 1) % 12 + 1
        target_yr = last_year + (last_month + i - 1) // 12
        base_val = seasonal_means[target_m]
        std_val = seasonal_stds[target_m]
        
        # projected value with slope
        projected = max(0.0, base_val + poly[0] * (len(recent) + i))
        upper_band = projected + (std_val * 0.8)
        lower_band = max(0.0, projected - (std_val * 0.8))
        
        forecast_rows.append({
            'Year': target_yr,
            'Month': target_m,
            'Month_TH': MONTH_NAMES[target_m]['th'],
            'Period': f"{target_yr}-{target_m:02d}",
            'Predicted_Mean': round(projected, 2),
            'Upper_Confidence': round(upper_band, 2),
            'Lower_Confidence': round(lower_band, 2)
        })
        
    return pd.DataFrame(forecast_rows)
