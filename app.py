"""
HydroPulse TH: Enterprise National Water Intelligence & Climate Analytics Dashboard
ศูนย์บัญชาการและระบบสารสนเทศวิเคราะห์สถานการณ์น้ำฝนประเทศไทย
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk

from config import PROVINCE_GEO, MONTH_NAMES, SEASON_MAPPING, REGION_COLORS, PROV_ID_TO_NAME
from data_loader import (
    load_province_rainfall,
    load_historical_national,
    load_amphoe_processed,
    compute_forecast_projection
)

# ---------------------------------------------------------
# Page Configuration & Global Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="HydroPulse TH | ศูนย์วิเคราะห์สถานการณ์น้ำฝนประเทศไทย",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif;
    }
    
    /* Top Header Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.18) 0%, rgba(30, 41, 59, 0.75) 50%, rgba(99, 102, 241, 0.15) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 22px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    }
    .hero-title {
        font-size: 1.85rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .hero-subtitle {
        font-size: 0.92rem;
        color: #94a3b8;
        margin-top: 6px;
        margin-bottom: 0;
    }
    
    /* KPI Glassmorphism Cards */
    .kpi-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.28);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.5);
    }
    .kpi-title {
        font-size: 0.82rem;
        font-weight: 600;
        color: #94a3b8;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.1;
    }
    .kpi-sub {
        margin-top: 6px;
        font-size: 0.78rem;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .tag-surplus {
        color: #38bdf8;
        background: rgba(56, 189, 248, 0.15);
        padding: 2px 7px;
        border-radius: 5px;
        font-weight: 600;
    }
    .tag-deficit {
        color: #f87171;
        background: rgba(248, 113, 113, 0.15);
        padding: 2px 7px;
        border-radius: 5px;
        font-weight: 600;
    }
    .tag-normal {
        color: #a3e635;
        background: rgba(163, 230, 53, 0.15);
        padding: 2px 7px;
        border-radius: 5px;
        font-weight: 600;
    }
    
    /* Live Sync Badge */
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.18);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 2px 8px;
        border-radius: 16px;
        font-size: 0.74rem;
        font-weight: 600;
    }
    .pulse-dot {
        width: 7px;
        height: 7px;
        background-color: #34d399;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 6px #34d399;
    }
    
    /* AI Brief Box */
    .ai-brief {
        background: rgba(15, 23, 42, 0.75);
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 20px;
        color: #e2e8f0;
        font-size: 0.92rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Load Cached Datasets
# ---------------------------------------------------------
df_province = load_province_rainfall()
df_historical = load_historical_national()
df_amphoe = load_amphoe_processed()

# ---------------------------------------------------------
# Sidebar Navigation Menu
# ---------------------------------------------------------
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, rgba(14, 165, 233, 0.22) 0%, rgba(30, 41, 59, 0.85) 100%); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 14px 12px; margin-bottom: 16px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
    <div style="font-size: 1.35rem; font-weight: 700; color: #38bdf8; display: flex; align-items: center; justify-content: center; gap: 8px;">
        <span>🌧️ HydroPulse TH</span>
    </div>
    <div style="font-size: 0.72rem; color: #94a3b8; letter-spacing: 0.05em; text-transform: uppercase; margin-top: 3px;">
        National Water Intelligence
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<p style='font-size:0.8rem; font-weight:700; color:#38bdf8; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:6px;'>📌 หน้าเมนูหลัก (SELECT MODULE)</p>", unsafe_allow_html=True)

page_nav = st.sidebar.selectbox(
    "เลือกหน้าโมดูล",
    options=[
        "🏠 1. ภาพรวมระดับประเทศ",
        "🗺️ 2. แผนที่ภูมิสารสนเทศ (GIS & 3D)",
        "🏢 3. เจาะลึกรายจังหวัด & ฝนสะสม",
        "⚖️ 4. เปรียบเทียบข้ามมิติ",
        "🌦️ 5. วิเคราะห์ตามฤดูกาล & มรสุม",
        "📈 6. อนุกรมเวลา 55 ปี & พยากรณ์",
        "🏘️ 7. ข้อมูลรายอำเภอ 928 แห่ง",
        "🧪 8. แบบจำลองสถานการณ์น้ำ (What-If)",
        "📊 9. จัดอันดับ & ส่งออกข้อมูล"
    ],
    index=0,
    label_visibility="collapsed"
)

st.sidebar.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size:0.8rem; font-weight:700; color:#38bdf8; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:6px;'>🎛️ ตัวกรองข้อมูล (FILTERS)</p>", unsafe_allow_html=True)

# Global Filters
available_years = sorted(df_province['YEAR'].unique(), reverse=True)
selected_year = st.sidebar.selectbox(
    "📅 ปี (Year)",
    options=available_years,
    index=2 if 2024 in available_years else 0, # Default to 2024 for complete 12 months
    help="เลือกปีที่ต้องการวิเคราะห์ข้อมูล"
)

month_options = ["ทั้งปี (All Months / Annual Sum)"] + [f"{m}: {MONTH_NAMES[m]['th']} ({MONTH_NAMES[m]['en']})" for m in range(1, 13)]
selected_month_str = st.sidebar.selectbox(
    "📆 เดือน (Month)",
    options=month_options,
    index=0
)
is_all_months = selected_month_str.startswith("ทั้งปี")
selected_month = None if is_all_months else int(selected_month_str.split(":")[0])

region_options = ["ทุกภูมิภาค (All Regions)"] + sorted(list(set(df_province['Region'])))
selected_region = st.sidebar.selectbox(
    "🧭 ภูมิภาค (Region)",
    options=region_options,
    index=0
)

metric_mode = st.sidebar.selectbox(
    "📊 ตัวแปรชี้วัด (Metric)",
    options=["ฝนเฉลี่ย (Avg Rain)", "ฝนสูงสุด (Max Rain)", "ฝนต่ำสุด (Min Rain)"],
    index=0
)
metric_col = "AvgRain" if "เฉลี่ย" in metric_mode else ("MaxRain" if "สูงสุด" in metric_mode else "MinRain")
metric_label = "ปริมาณฝนเฉลี่ย" if "เฉลี่ย" in metric_mode else ("ปริมาณฝนสูงสุด" if "สูงสุด" in metric_mode else "ปริมาณฝนต่ำสุด")

st.sidebar.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid rgba(255,255,255,0.08);'>", unsafe_allow_html=True)

with st.sidebar.expander("🚨 ตั้งค่าเกณฑ์เตือนภัย (Alert Settings)", expanded=False):
    flood_threshold = st.slider(
        "เกณฑ์เฝ้าระวังฝนตกหนักสะสม (มม.)",
        min_value=100,
        max_value=600,
        value=300,
        step=25
    )

with st.sidebar.expander("ℹ️ แหล่งข้อมูลอ้างอิง (Data Sources)", expanded=False):
    st.markdown("""
    <div style="font-size: 0.78rem; color: #94a3b8; line-height: 1.6;">
        • สถาบันสารสนเทศทรัพยากรน้ำ (สสน. / HII)<br>
        • กรมอุตุนิยมวิทยา (TMD) Baseline 1991-2020<br>
        • สถานีตรวจวัดน้ำฝนรายอำเภอ 928 แห่ง
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Filter Dataset
# ---------------------------------------------------------
filtered_df = df_province[df_province['YEAR'] == selected_year].copy()
if not is_all_months:
    filtered_df = filtered_df[filtered_df['MONTH'] == selected_month]
if selected_region != "ทุกภูมิภาค (All Regions)":
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]

if is_all_months:
    prov_summary = filtered_df.groupby(['PROV_T', 'Region', 'Latitude', 'Longitude'], as_index=False).agg({
        'AvgRain': 'sum',
        'MaxRain': 'max',
        'MinRain': 'min',
        'Normal_30Y_Mean': 'sum',
        'Rain_Anomaly': 'sum'
    })
    prov_summary['Rain_Anomaly_Pct'] = ((prov_summary['AvgRain'] - prov_summary['Normal_30Y_Mean']) / prov_summary['Normal_30Y_Mean'].replace(0, 0.001)) * 100
    display_df = prov_summary
    time_label = f"ประจำปี {selected_year} (ทั้งปี)"
else:
    prov_summary = filtered_df.copy()
    display_df = prov_summary
    time_label = f"ประจำเดือน {MONTH_NAMES[selected_month]['th']} ปี {selected_year}"

# Global KPI calculations
national_avg = display_df[metric_col].mean() if len(display_df) > 0 else 0
normal_avg = display_df['Normal_30Y_Mean'].mean() if len(display_df) > 0 else 0
anomaly_delta = national_avg - normal_avg
anomaly_pct = (anomaly_delta / normal_avg * 100) if normal_avg > 0 else 0

if len(display_df) > 0:
    wettest_row = display_df.loc[display_df[metric_col].idxmax()]
    driest_row = display_df.loc[display_df[metric_col].idxmin()]
    wettest_name = wettest_row['PROV_T']
    wettest_val = wettest_row[metric_col]
    driest_name = driest_row['PROV_T']
    driest_val = driest_row[metric_col]
else:
    wettest_name, wettest_val = "-", 0
    driest_name, driest_val = "-", 0

high_risk_count = (display_df[metric_col] >= flood_threshold).sum()

# ---------------------------------------------------------
# Top Header Banner
# ---------------------------------------------------------
st.markdown(f"""
<div class="hero-banner">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div class="hero-title">
            <span>🌧️ HydroPulse TH</span>
            <span style="font-size: 1.05rem; color: #38bdf8; font-weight: 500;">| {page_nav.split(' (')[0]}</span>
        </div>
        <div class="live-badge">
            <span class="pulse-dot"></span>
            HII & TMD Data Synchronized
        </div>
    </div>
    <p class="hero-subtitle">
        มิติข้อมูล: <b>{time_label}</b> | พื้นที่: <b>{selected_region}</b> | เกณฑ์เตือนภัย: <b>{flood_threshold} มม.</b>
    </p>
</div>
""", unsafe_allow_html=True)


# =========================================================
# PAGE 1: NATIONAL OVERVIEW
# =========================================================
if page_nav.startswith("🏠"):
    # AI Executive Briefing
    if anomaly_pct > 15:
        status_text = f"สูงกว่าค่าสถิติปกติ 30 ปีอย่างมีนัยสำคัญ (+{anomaly_pct:.1f}%) จัดอยู่ในสภาวะ 'ฝนชุก / เฝ้าระวังอุทกภัย'"
        advice_text = f"พบพื้นที่เฝ้าระวัง {high_risk_count} จังหวัด ควรเร่งระบายน้ำและตรวจสอบความจุเขื่อนหลัก"
    elif anomaly_pct < -15:
        status_text = f"ต่ำกว่าเกณฑ์ปกติอย่างมีนัยสำคัญ ({anomaly_pct:.1f}%) จัดอยู่ในสภาวะ 'ฝนทิ้งช่วง / เสี่ยงภัยแล้ง'"
        advice_text = "ควรวางแผนกักเก็บน้ำต้นทุนในแหล่งน้ำธรรมชาติ และบริหารการใช้น้ำภาคการเกษตร"
    else:
        status_text = f"อยู่ในเกณฑ์ปกติ (Near Normal: {anomaly_pct:+.1f}%) สอดคล้องกับวงจรสภาพอากาศเฉลี่ย 30 ปี"
        advice_text = "ภาพรวมปริมาณน้ำอยู่ในระดับสมดุล มีพื้นที่เฝ้าระวังเฉพาะจุดตามฤดูกาล"

    st.markdown(f"""
    <div class="ai-brief">
        <b>🧠 สรุปสถานการณ์ภาพรวมระดับประเทศ (Executive Brief):</b><br>
        ในคาบเวลา <b>{time_label}</b> ปริมาณน้ำฝนเฉลี่ยอยู่ที่ <b>{national_avg:,.1f} มิลลิเมตร</b> ซึ่ง{status_text} โดยจังหวัดที่มีฝนตกชุกที่สุดคือ <b>จังหวัด{wettest_name} ({wettest_val:,.1f} มม.)</b> และจังหวัดที่มีฝนน้อยที่สุดคือ <b>จังหวัด{driest_name} ({driest_val:,.1f} มม.)</b><br>
        <b>📌 ข้อเสนอแนะเชิงปฏิบัติการ:</b> {advice_text}
    </div>
    """, unsafe_allow_html=True)

    # 5 KPI Cards
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">{metric_label}</div>
            <div class="kpi-value">{national_avg:,.1f} <span style="font-size:0.9rem;color:#94a3b8">มม.</span></div>
            <div class="kpi-sub"><span class="{'tag-surplus' if anomaly_delta>=0 else 'tag-deficit'}">{anomaly_delta:+.1f} mm ({anomaly_pct:+.1f}%)</span></div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">ค่าปกติ 30 ปี</div>
            <div class="kpi-value">{normal_avg:,.1f} <span style="font-size:0.9rem;color:#94a3b8">มม.</span></div>
            <div class="kpi-sub"><span class="tag-normal">เกณฑ์อ้างอิง 1991-2020</span></div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">ฝนสูงสุด (Wettest)</div>
            <div class="kpi-value" style="font-size:1.5rem">{wettest_name}</div>
            <div class="kpi-sub"><span class="tag-surplus">🌧️ {wettest_val:,.1f} มม.</span></div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">ฝนต่ำสุด (Driest)</div>
            <div class="kpi-value" style="font-size:1.5rem">{driest_name}</div>
            <div class="kpi-sub"><span class="tag-deficit">☀️ {driest_val:,.1f} มม.</span></div>
        </div>
        """, unsafe_allow_html=True)
    with k5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">พื้นที่เฝ้าระวัง (≥ {flood_threshold} mm)</div>
            <div class="kpi-value" style="color: {'#f87171' if high_risk_count>0 else '#34d399'}">{high_risk_count} <span style="font-size:0.9rem;color:#94a3b8">จังหวัด</span></div>
            <div class="kpi-sub"><span class="{'tag-deficit' if high_risk_count>0 else 'tag-normal'}">{'⚠️ เสี่ยงน้ำล้น' if high_risk_count>0 else '✅ อยู่ในเกณฑ์ปกติ'}</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    
    # Replaced circular charts with intuitive, easy-to-read horizontal bar charts
    c_bar1, c_bar2 = st.columns([1, 1])
    with c_bar1:
        st.markdown("##### 🧭 สัดส่วนปริมาณน้ำฝนสะสมแยกตามภูมิภาค (Regional Rainfall Volume & Share %)")
        region_agg_p1 = display_df.groupby('Region', as_index=False).agg({
            metric_col: 'sum'
        })
        total_vol = region_agg_p1[metric_col].sum()
        region_agg_p1['Share_Pct'] = (region_agg_p1[metric_col] / total_vol * 100) if total_vol > 0 else 0
        region_agg_p1 = region_agg_p1.sort_values(metric_col, ascending=True)

        fig_reg_share = px.bar(
            region_agg_p1,
            x=metric_col,
            y="Region",
            orientation="h",
            color="Region",
            color_discrete_map=REGION_COLORS,
            text=region_agg_p1.apply(lambda r: f"{r[metric_col]:,.0f} มม. ({r['Share_Pct']:.1f}%)", axis=1)
        )
        fig_reg_share.update_traces(textposition='outside')
        fig_reg_share.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15, 23, 42, 0.6)',
            xaxis=dict(title=f'ปริมาณ{metric_label}รวม (มม.)', gridcolor='#334155'),
            yaxis=dict(title='', gridcolor='#334155'),
            showlegend=False,
            margin=dict(l=10, r=20, t=10, b=10)
        )
        st.plotly_chart(fig_reg_share, use_container_width=True)

    with c_bar2:
        st.markdown(f"##### 🏆 10 อันดับจังหวัดที่มี{metric_label}สูงสุด (Top 10 Wettest Provinces)")
        top10_p1 = display_df.sort_values(metric_col, ascending=True).tail(10)
        fig_top10_p1 = px.bar(
            top10_p1,
            x=metric_col,
            y="PROV_T",
            orientation="h",
            color="Region",
            color_discrete_map=REGION_COLORS,
            text=metric_col
        )
        fig_top10_p1.update_traces(texttemplate='%{text:,.1f} มม.', textposition='outside')
        fig_top10_p1.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15, 23, 42, 0.6)',
            xaxis=dict(title=f'{metric_label} (มม.)', gridcolor='#334155'),
            yaxis=dict(title='', gridcolor='#334155'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=20, t=10, b=10)
        )
        st.plotly_chart(fig_top10_p1, use_container_width=True)

    # Monthly Distribution Area Chart (if all months)
    if is_all_months:
        st.markdown(f"##### 🌊 ปริมาณฝนสะสมรายเดือนของทั้งประเทศในปี {selected_year} (Monthly Nationwide Volume)")
        m_trend = df_province[df_province['YEAR'] == selected_year].groupby('MONTH', as_index=False).agg({
            'AvgRain': 'mean',
            'Normal_30Y_Mean': 'mean'
        })
        m_trend['Month_TH'] = m_trend['MONTH'].map(lambda m: MONTH_NAMES[m]['th'])
        
        fig_area = go.Figure()
        fig_area.add_trace(go.Scatter(
            x=m_trend['Month_TH'],
            y=m_trend['AvgRain'],
            fill='tozeroy',
            name='ปริมาณฝนจริงเฉลี่ย',
            line=dict(color='#38bdf8', width=3)
        ))
        fig_area.add_trace(go.Scatter(
            x=m_trend['Month_TH'],
            y=m_trend['Normal_30Y_Mean'],
            name='ค่าปกติ 30 ปี',
            line=dict(color='#94a3b8', width=2, dash='dash')
        ))
        fig_area.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15, 23, 42, 0.6)',
            xaxis=dict(gridcolor='#334155'),
            yaxis=dict(title='ปริมาณฝน (มม.)', gridcolor='#334155'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_area, use_container_width=True)


# =========================================================
# PAGE 2: GIS & 3D MAPS
# =========================================================
elif page_nav.startswith("🗺️"):
    st.subheader("🗺️ ระบบภูมิสารสนเทศและการแสดงผลแผนที่ขั้นสูง (GIS & 3D Geospatial Engine)")
    
    map_engine = st.radio(
        "เลือกโหมดการแสดงผลแผนที่ (Rendering Engine):",
        options=["🏙️ เสาความสูง 3 มิติ (Pydeck 3D Elevation Pillars)", "📍 แผนที่จุดพิกัดสารสนเทศ (Plotly Carto Dark Map)", "🌡️ แผนที่ความหนาแน่น (Density Heatmap)"],
        horizontal=True
    )
    
    c_map1, c_map2 = st.columns([1.2, 0.8])
    with c_map1:
        if "3 มิติ" in map_engine:
            st.markdown("##### 🏙️ แผนที่ 3D Pillars (ความสูงของเสาตามปริมาณน้ำฝน)")
            st.caption("คลิกเมาส์ขวาเพื่อหมุนมุมมอง (Tilt/Bearing) หรือซูมเข้าออกได้อย่างอิสระ")
            pydf = display_df.copy()
            max_v = max(1.0, float(pydf[metric_col].max()))
            pydf['elev'] = (pydf[metric_col] / max_v) * 500000
            
            def get_color(val, max_val):
                ratio = min(1.0, max(0.0, val / max_val))
                return [int(56 + ratio * 188), int(189 - ratio * 126), int(248 - ratio * 154), 210]
            pydf['color'] = pydf[metric_col].apply(lambda v: get_color(v, max_v))
            
            layer = pdk.Layer(
                "ColumnLayer",
                data=pydf,
                get_position=["Longitude", "Latitude"],
                get_elevation="elev",
                elevation_scale=1,
                radius=14000,
                get_fill_color="color",
                pickable=True,
                auto_highlight=True,
            )
            view_state = pdk.ViewState(latitude=13.75, longitude=100.52, zoom=5.0, pitch=48, bearing=-10)
            st.pydeck_chart(pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip={"html": "<b>จังหวัด{PROV_T}</b><br>ภูมิภาค: {Region}<br>ปริมาณฝน: <b>{" + metric_col + ":.1f} มม.</b><br>ค่าปกติ 30 ปี: {Normal_30Y_Mean:.1f} มม.<br>ส่วนต่าง: {Rain_Anomaly_Pct:+.1f}%"},
                map_style="dark"
            ))
        elif "จุดพิกัด" in map_engine:
            st.markdown("##### 📍 แผนที่จุดพิกัดปริมาณน้ำฝน 77 จังหวัด")
            map_fig = px.scatter_map(
                display_df,
                lat="Latitude",
                lon="Longitude",
                size=metric_col,
                color=metric_col,
                color_continuous_scale="Viridis",
                size_max=32,
                zoom=4.8,
                center={"lat": 13.73, "lon": 100.52},
                hover_name="PROV_T",
                hover_data={"Region": True, metric_col: ":.1f mm", "Normal_30Y_Mean": ":.1f mm", "Rain_Anomaly_Pct": ":.1f %", "Latitude": False, "Longitude": False},
                map_style="carto-darkmatter"
            )
            map_fig.update_layout(margin={"r":0,"t":10,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)", font={"color": "#f8fafc"})
            st.plotly_chart(map_fig, use_container_width=True)
        else:
            st.markdown("##### 🌡️ Density Heatmap การกระจายตัวของปริมาณน้ำฝน")
            density_fig = px.density_map(
                display_df,
                lat="Latitude",
                lon="Longitude",
                z=metric_col,
                radius=35,
                center={"lat": 13.73, "lon": 100.52},
                zoom=4.8,
                map_style="carto-darkmatter",
                color_continuous_scale="Plasma"
            )
            density_fig.update_layout(margin={"r":0,"t":10,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(density_fig, use_container_width=True)
            
    with c_map2:
        st.markdown("##### 🧭 สถิติเปรียบเทียบแยกรายภาค")
        r_sum = display_df.groupby('Region', as_index=False).agg({metric_col: 'mean', 'Normal_30Y_Mean': 'mean'}).sort_values(metric_col, ascending=False)
        fig_r_bar = go.Figure()
        fig_r_bar.add_trace(go.Bar(name='ฝนจริง', x=r_sum['Region'], y=r_sum[metric_col], marker_color='#38bdf8', text=r_sum[metric_col].apply(lambda x: f"{x:.1f}"), textposition='auto'))
        fig_r_bar.add_trace(go.Bar(name='ค่าปกติ 30 ปี', x=r_sum['Region'], y=r_sum['Normal_30Y_Mean'], marker_color='#64748b', text=r_sum['Normal_30Y_Mean'].apply(lambda x: f"{x:.1f}"), textposition='auto'))
        fig_r_bar.update_layout(
            barmode='group', template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15, 23, 42, 0.6)',
            xaxis=dict(gridcolor='#334155'), yaxis=dict(title='มม.', gridcolor='#334155'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(l=10, r=10, t=25, b=10)
        )
        st.plotly_chart(fig_r_bar, use_container_width=True)
        
        st.markdown("##### 📦 Boxplot การกระจายตัวในแต่ละภาค")
        fig_box = px.box(display_df, x="Region", y=metric_col, color="Region", color_discrete_map=REGION_COLORS, points="all", hover_name="PROV_T")
        fig_box.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15, 23, 42, 0.6)', showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_box, use_container_width=True)


# =========================================================
# PAGE 3: PROVINCIAL DEEP-DIVE & CUMULATIVE
# =========================================================
elif page_nav.startswith("🏢"):
    st.subheader("🏢 วิเคราะห์เจาะลึกรายจังหวัดและกราฟฝนสะสม (Provincial & Cumulative Rainfall)")
    
    all_provinces = sorted(df_province['PROV_T'].unique())
    sel_provinces = st.multiselect(
        "📍 เลือกจังหวัดที่ต้องการวิเคราะห์ (เลือกได้หลายจังหวัด):",
        options=all_provinces,
        default=['กรุงเทพมหานคร', 'เชียงใหม่', 'ภูเก็ต'] if all(p in all_provinces for p in ['กรุงเทพมหานคร', 'เชียงใหม่', 'ภูเก็ต']) else [all_provinces[0]]
    )
    
    if len(sel_provinces) > 0:
        c_curve1, c_curve2 = st.columns([1.1, 0.9])
        
        with c_curve1:
            st.markdown(f"##### 📈 กราฟปริมาณฝนสะสมตลอดทั้งปี (Cumulative Rainfall Curve: {selected_year})")
            fig_cum = go.Figure()
            for p_name in sel_provinces:
                p_data = df_province[(df_province['PROV_T'] == p_name) & (df_province['YEAR'] == selected_year)].sort_values('MONTH').copy()
                p_data['CumRain'] = p_data['AvgRain'].cumsum()
                p_data['CumNormal'] = p_data['Normal_30Y_Mean'].cumsum()
                
                fig_cum.add_trace(go.Scatter(
                    x=p_data['Month_TH'],
                    y=p_data['CumRain'],
                    mode='lines+markers',
                    name=f'ฝนสะสมจริง ({p_name})',
                    line=dict(width=3)
                ))
                fig_cum.add_trace(go.Scatter(
                    x=p_data['Month_TH'],
                    y=p_data['CumNormal'],
                    mode='lines',
                    name=f'ปกติ 30 ปีสะสม ({p_name})',
                    line=dict(dash='dot', width=1.5)
                ))
            fig_cum.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(15, 23, 42, 0.6)',
                xaxis=dict(title='เดือน', gridcolor='#334155'),
                yaxis=dict(title='ฝนสะสมรวม (มม.)', gridcolor='#334155'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_cum, use_container_width=True)
            
        with c_curve2:
            st.markdown(f"##### 📊 ปริมาณฝนรายเดือน 12 เดือน (Monthly Actual Curves)")
            fig_monthly = go.Figure()
            for p_name in sel_provinces:
                p_data = df_province[(df_province['PROV_T'] == p_name) & (df_province['YEAR'] == selected_year)].sort_values('MONTH')
                fig_monthly.add_trace(go.Scatter(
                    x=p_data['Month_TH'],
                    y=p_data['AvgRain'],
                    mode='lines+markers',
                    name=p_name,
                    line=dict(width=2.5)
                ))
            fig_monthly.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(15, 23, 42, 0.6)',
                xaxis=dict(title='เดือน', gridcolor='#334155'),
                yaxis=dict(title='ปริมาณฝน (มม.)', gridcolor='#334155'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
            
        # Single Province Anomaly Waterfall
        main_p = sel_provinces[0]
        st.markdown(f"##### ⚖️ ส่วนต่างเทียบเกณฑ์มาตรฐาน 30 ปี (Anomaly Waterfall: จังหวัด{main_p})")
        single_p_data = df_province[(df_province['PROV_T'] == main_p) & (df_province['YEAR'] == selected_year)].sort_values('MONTH')
        anom_col = ['#38bdf8' if v >= 0 else '#f87171' for v in single_p_data['Rain_Anomaly']]
        fig_water = go.Figure(go.Bar(
            x=single_p_data['Month_TH'],
            y=single_p_data['Rain_Anomaly'],
            marker_color=anom_col,
            text=single_p_data['Rain_Anomaly'].apply(lambda x: f"{x:+.1f} มม."),
            textposition='outside'
        ))
        fig_water.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15, 23, 42, 0.6)',
            xaxis=dict(gridcolor='#334155'),
            yaxis=dict(title='ความต่างจากเกณฑ์ปกติ (มม.)', gridcolor='#334155'),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_water, use_container_width=True)
    else:
        st.info("กรุณาเลือกอย่างน้อย 1 จังหวัดเพื่อแสดงผล")


# =========================================================
# PAGE 4: CROSS-COMPARISON TOOL
# =========================================================
elif page_nav.startswith("⚖️"):
    st.subheader("⚖️ เครื่องมือเปรียบเทียบข้ามมิติ (Cross-Comparison Analysis Tool)")
    
    comp_mode = st.radio("เลือกรูปแบบการเปรียบเทียบ:", options=["📅 เปรียบเทียบรายปี (Year-over-Year: YoY)", "🧭 เปรียบเทียบรายภูมิภาค (Region vs Region)", "🔗 ความสัมพันธ์ฝนจริง vs ค่าปกติ (Correlation Scatter)"], horizontal=True)
    
    if "รายปี" in comp_mode:
        st.markdown("##### 📅 เปรียบเทียบปริมาณน้ำฝนรายปี (Year-over-Year)")
        sel_yoy_prov = st.selectbox("เลือกจังหวัด:", options=sorted(df_province['PROV_T'].unique()), index=0)
        yoy_df = df_province[df_province['PROV_T'] == sel_yoy_prov].copy()
        
        fig_yoy = px.line(
            yoy_df,
            x="Month_TH",
            y="AvgRain",
            color="YEAR",
            markers=True,
            title=f"แนวโน้มฝนรายเดือนเปรียบเทียบในแต่ละปี: จังหวัด{sel_yoy_prov}"
        )
        fig_yoy.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15, 23, 42, 0.6)', xaxis=dict(gridcolor='#334155'), yaxis=dict(title='มม.', gridcolor='#334155'))
        st.plotly_chart(fig_yoy, use_container_width=True)
        
    elif "ภูมิภาค" in comp_mode:
        st.markdown(f"##### 🧭 เปรียบเทียบสถิติปริมาณน้ำฝนรายเดือนใน 6 ภูมิภาค ({selected_year})")
        reg_month = df_province[df_province['YEAR'] == selected_year].groupby(['Region', 'MONTH', 'Month_TH'], as_index=False)['AvgRain'].mean().sort_values('MONTH')
        fig_reg_line = px.line(
            reg_month,
            x="Month_TH",
            y="AvgRain",
            color="Region",
            color_discrete_map=REGION_COLORS,
            markers=True
        )
        fig_reg_line.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15, 23, 42, 0.6)', xaxis=dict(gridcolor='#334155'), yaxis=dict(title='มม.', gridcolor='#334155'))
        st.plotly_chart(fig_reg_line, use_container_width=True)
        
    else:
        st.markdown("##### 🔗 Scatter Plot ความสัมพันธ์ระหว่างฝนจริงกับค่าสถิติปกติ 30 ปี")
        fig_scat = px.scatter(
            display_df,
            x="Normal_30Y_Mean",
            y=metric_col,
            color="Region",
            color_discrete_map=REGION_COLORS,
            hover_name="PROV_T",
            size=metric_col,
            trendline="ols",
            labels={"Normal_30Y_Mean": "ค่าปกติ 30 ปี (มม.)", metric_col: f"{metric_label} จริง (มม.)"}
        )
        fig_scat.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15, 23, 42, 0.6)', xaxis=dict(gridcolor='#334155'), yaxis=dict(gridcolor='#334155'))
        st.plotly_chart(fig_scat, use_container_width=True)


# =========================================================
# PAGE 5: SEASONAL ANALYSIS
# =========================================================
elif page_nav.startswith("🌦️"):
    st.subheader("🌦️ การวิเคราะห์ตามฤดูกาลและรอบมรสุมของไทย (Seasonal & Monsoon Dynamics)")
    st.markdown("""
    แบ่งตามเกณฑ์ 3 ฤดูกาลของกรมอุตุนิยมวิทยา:
    - ☀️ **ฤดูร้อน (Summer):** กลาง ก.พ. - กลาง พ.ค.
    - 🌧️ **ฤดูฝน (Rainy Season):** กลาง พ.ค. - กลาง ต.ค.
    - ❄️ **ฤดูหนาว (Winter):** กลาง ต.ค. - กลาง ก.พ.
    """)
    
    season_data = df_province[df_province['YEAR'] == selected_year].groupby(['Season', 'Region'], as_index=False)['AvgRain'].sum()
    
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        st.markdown("##### 📊 ปริมาณฝนสะสมแยกตามฤดูกาลในแต่ละภูมิภาค")
        fig_s_bar = px.bar(
            season_data,
            x="Region",
            y="AvgRain",
            color="Season",
            barmode="group",
            color_discrete_map={'ฤดูร้อน': '#f59e0b', 'ฤดูฝน': '#38bdf8', 'ฤดูหนาว': '#a855f7'}
        )
        fig_s_bar.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15, 23, 42, 0.6)', xaxis=dict(gridcolor='#334155'), yaxis=dict(title='ปริมาณฝนสะสม (มม.)', gridcolor='#334155'))
        st.plotly_chart(fig_s_bar, use_container_width=True)
        
    with c_s2:
        st.markdown("##### 📊 สัดส่วนปริมาณฝนแยกตาม 3 ฤดูกาล (Seasonal Breakdown & Share)")
        prov_target_s = st.selectbox("เลือกจังหวัด:", options=sorted(df_province['PROV_T'].unique()), index=0)
        p_seas = df_province[(df_province['PROV_T'] == prov_target_s) & (df_province['YEAR'] == selected_year)].groupby('Season', as_index=False)['AvgRain'].sum()
        
        tot_seas = p_seas['AvgRain'].sum()
        p_seas['Share_Pct'] = (p_seas['AvgRain'] / tot_seas * 100) if tot_seas > 0 else 0
        seasons_seq = ['ฤดูร้อน', 'ฤดูฝน', 'ฤดูหนาว']
        p_seas['Season'] = pd.Categorical(p_seas['Season'], categories=seasons_seq, ordered=True)
        p_seas = p_seas.sort_values('Season')

        fig_seas_bar = px.bar(
            p_seas,
            x='Season',
            y='AvgRain',
            color='Season',
            color_discrete_map={'ฤดูร้อน': '#f59e0b', 'ฤดูฝน': '#38bdf8', 'ฤดูหนาว': '#a855f7'},
            text=p_seas.apply(lambda r: f"{r['AvgRain']:,.1f} มม.<br>({r['Share_Pct']:.1f}%)", axis=1)
        )
        fig_seas_bar.update_traces(textposition='outside')
        fig_seas_bar.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15, 23, 42, 0.6)',
            xaxis=dict(title='ฤดูกาล', gridcolor='#334155'),
            yaxis=dict(title='ปริมาณฝนสะสม (มม.)', gridcolor='#334155'),
            showlegend=False,
            margin=dict(l=10, r=10, t=20, b=10)
        )
        st.plotly_chart(fig_seas_bar, use_container_width=True)


# =========================================================
# PAGE 6: LONG-TERM TIME SERIES (1970 - 2025)
# =========================================================
elif page_nav.startswith("📈"):
    st.subheader("📈 แนวโน้มระยะยาว 55 ปี (1970 - 2025) และแบบจำลองพยากรณ์ล่วงหน้า")
    
    # Predictive Forecast calculation
    df_fc = compute_forecast_projection(df_historical, months_ahead=12)
    
    # 55-Year Time Series
    st.markdown("##### 🌊 อนุกรมเวลาปริมาณฝนเฉลี่ยรายเดือนทั่วประเทศ (1970 - 2025)")
    fig_full = go.Figure()
    fig_full.add_trace(go.Scatter(x=df_historical['Date'], y=df_historical['MEAN'], mode='lines', name='ฝนจริงรายเดือน', line=dict(color='rgba(56, 189, 248, 0.3)', width=1)))
    fig_full.add_trace(go.Scatter(x=df_historical['Date'], y=df_historical['Roll12_Mean'], mode='lines', name='ค่าเฉลี่ยเคลื่อนที่ 12 เดือน', line=dict(color='#38bdf8', width=2)))
    fig_full.add_trace(go.Scatter(x=df_historical['Date'], y=df_historical['Roll60_Mean'], mode='lines', name='แนวโน้ม 5 ปี (Trend)', line=dict(color='#f43f5e', width=3)))
    fig_full.add_vrect(x0="2011-01-01", x1="2011-12-31", fillcolor="rgba(56, 189, 248, 0.25)", opacity=0.5, annotation_text="🌊 มหาอุทกภัย 2554", annotation_position="top left")
    fig_full.add_vrect(x0="2015-01-01", x1="2015-12-31", fillcolor="rgba(249, 115, 22, 0.25)", opacity=0.5, annotation_text="☀️ ภัยแล้งเอลนีโญ 2558", annotation_position="top left")
    fig_full.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15, 23, 42, 0.6)', xaxis=dict(gridcolor='#334155'), yaxis=dict(title='มม.', gridcolor='#334155'), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_full, use_container_width=True)
    
    c_f1, c_f2 = st.columns([1, 1])
    with c_f1:
        st.markdown("##### 🔮 แบบจำลองพยากรณ์ปริมาณน้ำฝนล่วงหน้า 12 เดือน (Forecast)")
        fig_fc_chart = go.Figure()
        fig_fc_chart.add_trace(go.Scatter(
            x=df_fc['Period'].tolist() + df_fc['Period'].tolist()[::-1],
            y=df_fc['Upper_Confidence'].tolist() + df_fc['Lower_Confidence'].tolist()[::-1],
            fill='toself', fillcolor='rgba(56, 189, 248, 0.15)', line=dict(color='rgba(255,255,255,0)'), name='ช่วงความเชื่อมั่น'
        ))
        fig_fc_chart.add_trace(go.Scatter(x=df_fc['Period'], y=df_fc['Predicted_Mean'], mode='lines+markers', name='คาดการณ์', line=dict(color='#38bdf8', width=3)))
        fig_fc_chart.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15, 23, 42, 0.6)', xaxis=dict(gridcolor='#334155'), yaxis=dict(title='มม.', gridcolor='#334155'))
        st.plotly_chart(fig_fc_chart, use_container_width=True)
        
    with c_f2:
        st.markdown("##### 🌡️ Climate Heatmap รอบ 50 ปี (Monthly Monsoon Matrix)")
        piv_rain = df_historical.pivot(index='YEAR', columns='MONTH', values='MEAN')
        piv_rain.columns = [MONTH_NAMES[m]['short'] for m in piv_rain.columns]
        fig_h_chart = px.imshow(piv_rain, labels=dict(x="เดือน", y="ปี", color="มม."), color_continuous_scale="Blues", aspect="auto")
        fig_h_chart.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_h_chart, use_container_width=True)


# =========================================================
# PAGE 7: AMPHOE EXPLORER (928 DISTRICTS)
# =========================================================
elif page_nav.startswith("🏘️"):
    st.subheader("🏘️ ศูนย์สืบค้นข้อมูลสถานีตรวจวัดระดับอำเภอ 928 แห่ง (Amphoe Explorer)")
    
    amp_provs = sorted([p for p in df_amphoe['PROV_T'].dropna().unique()])
    col_ap1, col_ap2 = st.columns(2)
    with col_ap1:
        sel_amp_p = st.selectbox("เลือกจังหวัด:", options=amp_provs, index=0)
    with col_ap2:
        sel_amp_y = st.selectbox("เลือกปีของข้อมูลอำเภอ:", options=sorted(df_amphoe['year'].unique()), index=len(df_amphoe['year'].unique())-1)
        
    amp_filtered = df_amphoe[(df_amphoe['PROV_T'] == sel_amp_p) & (df_amphoe['year'] == sel_amp_y)]
    if len(amp_filtered) > 0:
        c_am1, c_am2 = st.columns([1.1, 0.9])
        with c_am1:
            st.markdown(f"##### 🏆 จัดอันดับอำเภอฝนสะสมสูงสุดในจังหวัด{sel_amp_p} ({sel_amp_y})")
            amp_sum = amp_filtered.groupby('amphoe_code', as_index=False)['Rain_Avg'].sum().sort_values('Rain_Avg', ascending=False)
            amp_sum['รหัสอำเภอ'] = amp_sum['amphoe_code'].astype(str)
            fig_amp_bar = px.bar(amp_sum.head(12), x='รหัสอำเภอ', y='Rain_Avg', color='Rain_Avg', color_continuous_scale='Teal', text='Rain_Avg')
            fig_amp_bar.update_traces(texttemplate='%{text:.1f} มม.', textposition='outside')
            fig_amp_bar.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15, 23, 42, 0.6)', xaxis=dict(title='รหัสอำเภอ', gridcolor='#334155'), yaxis=dict(title='มม.', gridcolor='#334155'), coloraxis_showscale=False)
            st.plotly_chart(fig_amp_bar, use_container_width=True)
            
        with c_am2:
            st.markdown(f"##### 📋 ตารางข้อมูลสถานีวัดน้ำฝนรายอำเภอ")
            amp_view = amp_filtered[['month', 'Month_TH', 'amphoe_code', 'Rain_Avg']].copy()
            amp_view.columns = ['เดือน', 'ชื่อเดือน', 'รหัสอำเภอ', 'ฝนเฉลี่ย (มม.)']
            st.dataframe(amp_view, use_container_width=True, hide_index=True)


# =========================================================
# PAGE 8: WHAT-IF SIMULATOR
# =========================================================
elif page_nav.startswith("🧪"):
    st.subheader("🧪 ระบบจำลองสถานการณ์น้ำและวิกฤติสภาพอากาศ (What-If Water Simulator)")
    
    col_sim_ctrl1, col_sim_ctrl2 = st.columns([1, 1.5])
    with col_sim_ctrl1:
        sim_shift = st.slider("🌧️ ปรับเปอร์เซ็นต์ปริมาณน้ำฝนจำลอง (% Change):", min_value=-50, max_value=50, value=0, step=5, format="%+d%%")
        sim_flood_limit = st.number_input("เกณฑ์วิกฤติน้ำท่วม (มม.):", min_value=150, max_value=800, value=350, step=25)
        sim_drought_limit = st.number_input("เกณฑ์วิกฤติภัยแล้ง (มม.):", min_value=10, max_value=200, value=40, step=10)
        
    sim_df = display_df.copy()
    sim_df['SimulatedRain'] = sim_df[metric_col] * (1.0 + sim_shift / 100.0)
    sim_flood = sim_df[sim_df['SimulatedRain'] >= sim_flood_limit]
    sim_drought = sim_df[sim_df['SimulatedRain'] <= sim_drought_limit]
    
    with col_sim_ctrl2:
        st.markdown(f"##### 📊 ผลการจำลองสภาวะอากาศ ({sim_shift:+d}%)")
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("ฝนจำลองเฉลี่ย", f"{sim_df['SimulatedRain'].mean():,.1f} มม.", f"{sim_shift:+d}%")
        sc2.metric("พื้นที่เสี่ยงน้ำท่วม", f"{len(sim_flood)} จังหวัด", f"≥ {sim_flood_limit} มม.")
        sc3.metric("พื้นที่เสี่ยงภัยแล้ง", f"{len(sim_drought)} จังหวัด", f"≤ {sim_drought_limit} มม.")
        
    st.write("")
    top15_sim = sim_df.sort_values('SimulatedRain', ascending=False).head(15)
    fig_sim = go.Figure()
    fig_sim.add_trace(go.Bar(name='ฝนจริง', x=top15_sim['PROV_T'], y=top15_sim[metric_col], marker_color='#64748b'))
    fig_sim.add_trace(go.Bar(name='ฝนหลังจำลอง', x=top15_sim['PROV_T'], y=top15_sim['SimulatedRain'], marker_color='#38bdf8' if sim_shift >= 0 else '#f87171'))
    fig_sim.add_hline(y=sim_flood_limit, line_dash="dash", line_color="#ef4444", annotation_text="เกณฑ์น้ำท่วม")
    fig_sim.update_layout(barmode='group', template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15, 23, 42, 0.6)', xaxis=dict(gridcolor='#334155', tickangle=-45), yaxis=dict(title='มม.', gridcolor='#334155'))
    st.plotly_chart(fig_sim, use_container_width=True)


# =========================================================
# PAGE 9: RANKINGS & DATA EXPORT
# =========================================================
elif page_nav.startswith("📊"):
    st.subheader("📊 การจัดอันดับและศูนย์ส่งออกข้อมูล (Rankings & Data Export Hub)")
    
    r1, r2 = st.columns(2)
    with r1:
        st.markdown(f"##### 🥇 Top 10 จังหวัด{metric_label}มากที่สุด")
        top10_w = display_df.sort_values(metric_col, ascending=False).head(10)
        fig_t = px.bar(top10_w[::-1], x=metric_col, y="PROV_T", orientation="h", color=metric_col, color_continuous_scale="Teal", text=metric_col)
        fig_t.update_traces(texttemplate='%{text:.1f} มม.', textposition='inside')
        fig_t.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15, 23, 42, 0.6)', xaxis=dict(gridcolor='#334155'), yaxis=dict(title=''), coloraxis_showscale=False)
        st.plotly_chart(fig_t, use_container_width=True)
        
    with r2:
        st.markdown(f"##### 🏜️ Top 10 จังหวัด{metric_label}น้อยที่สุด")
        top10_d = display_df.sort_values(metric_col, ascending=True).head(10)
        fig_d = px.bar(top10_d[::-1], x=metric_col, y="PROV_T", orientation="h", color=metric_col, color_continuous_scale="Burg", text=metric_col)
        fig_d.update_traces(texttemplate='%{text:.1f} มม.', textposition='inside')
        fig_d.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15, 23, 42, 0.6)', xaxis=dict(gridcolor='#334155'), yaxis=dict(title=''), coloraxis_showscale=False)
        st.plotly_chart(fig_d, use_container_width=True)
        
    st.markdown("---")
    st.markdown("##### 📋 ตารางสถิติและเครื่องมือสืบค้นแบบละเอียด")
    export_df = display_df[['PROV_T', 'Region', 'AvgRain', 'MaxRain', 'MinRain', 'Normal_30Y_Mean', 'Rain_Anomaly', 'Rain_Anomaly_Pct']].copy()
    export_df.columns = ['จังหวัด', 'ภูมิภาค', 'ฝนเฉลี่ย (มม.)', 'ฝนสูงสุด (มม.)', 'ฝนต่ำสุด (มม.)', 'ค่าปกติ 30 ปี (มม.)', 'ส่วนต่าง 30Y (มม.)', 'ความต่างร้อยละ (%)']
    export_df = export_df.round(2)
    
    search_q = st.text_input("🔍 ค้นหาจังหวัด:", placeholder="พิมพ์ชื่อจังหวัด...")
    view_table = export_df[export_df['จังหวัด'].str.contains(search_q.strip(), na=False)] if search_q else export_df
    
    st.dataframe(view_table, use_container_width=True, hide_index=True)
    
    csv_bytes = view_table.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="📥 ดาวน์โหลดชุดข้อมูลเป็น CSV (Download CSV)",
        data=csv_bytes,
        file_name=f"hydropulse_thailand_{selected_year}_{selected_region}.csv",
        mime="text/csv"
    )

# ---------------------------------------------------------
# Global Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 12px 0;">
    🌧️ <b>HydroPulse TH</b> | National Water Intelligence & Climate Analytics Center<br>
    Powered by Streamlit, Pydeck, Plotly & Pandas | Ready for Deployment on Streamlit Community Cloud
</div>
""", unsafe_allow_html=True)
