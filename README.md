# 🌧️ HydroPulse TH: National Water Intelligence & Climate Analytics Dashboard
### ศูนย์บัญชาการวิเคราะห์สถานการณ์น้ำฝนและสภาพภูมิอากาศประเทศไทย

แดชบอร์ด Data Visualization ระดับ Enterprise Command Center พัฒนาด้วย **Streamlit**, **Pydeck (3D Geospatial)**, **Plotly**, และ **Pandas** บูรณาการข้อมูลระดับชาติจาก **สถาบันสารสนเทศทรัพยากรน้ำ (สสน. / HII)**, **กรมอุตุนิยมวิทยา (TMD)**, และสถานีตรวจวัดน้ำฝนอัตโนมัติรายอำเภอ 928 แห่ง

---

## 🚀 ฟังก์ชันการวิเคราะห์ขั้นสูง 6 มิติ (Advanced Analytics Modules)

### 1. 🧠 AI Executive Intelligence Briefing & KPI Command Center
- **สรุปรายงานสถานการณ์อัตโนมัติ (Dynamic AI Synthesis):** วิเคราะห์ประเมินภาพรวมสภาพอากาศ พร้อมดัชนีชี้วัดความผิดปกติ (% Anomaly) เทียบกับค่าปกติ 30 ปี และข้อเสนอแนะเชิงนโยบายการบริหารจัดการน้ำ (กรมชลประทาน/สทนช.)
- **5 Glassmorphic KPI Cards:** ฝนเฉลี่ย, ค่าปกติ 30 ปี, จังหวัดฝนสูงสุด (Wettest), จังหวัดฝนต่ำสุด (Driest), และจำนวนพื้นที่วิกฤติฝนตกหนักสะสม

### 2. 🌐 แผนที่แท่งความสูง 3 มิติ (Pydeck 3D Digital Twin & Geospatial Intelligence)
- **3D Rainfall Elevation Pillars:** แผนที่ 3 มิติจำลองเสาความสูงของปริมาณน้ำฝนตามพิกัด 77 จังหวัดทั่วไทย (หมุน Tilt/Pitch มุมกล้องได้อิสระ)
- **Interactive 2D Scatter Map:** แผนที่ Plotly Carto Dark พร้อม Hover Card แสดงสถิติละเอียด
- **Regional Benchmark & Boxplot:** เปรียบเทียบฝนจริงกับค่ามาตรฐาน 30 ปีแยกตาม 6 ภูมิภาค พร้อมวิเคราะห์การกระจายตัวและความแปรปรวน

### 3. 📊 วิเคราะห์รอบฤดูกาล & ค่าสถิติปกติ 30 ปี (Seasonality & Climate Normals)
- **Seasonal Profile:** จัดกลุ่มตาม 3 ฤดูกาลของไทย (☀️ ฤดูร้อน, 🌧️ ฤดูฝน, ❄️ ฤดูหนาว)
- **Multi-Province Comparison:** เปรียบเทียบเจาะลึกได้สูงสุด 3 จังหวัดพร้อมกันแบบ Side-by-Side
- **Diverging Waterfall Bar:** วิเคราะห์ภาวะฝนเกินเกณฑ์ (Surplus) หรือฝนแล้ง (Deficit) ในแต่ละเดือน
- **Seasonal Radar Profile:** แผนภาพเรดาร์แสดงเอกลักษณ์ปริมาณฝนในแต่ละฤดู

### 4. 🧪 ระบบจำลองสถานการณ์น้ำ "What-If" Water Stress Simulator
- **Extreme Weather Simulation:** ปรับสไลเดอร์เปอร์เซ็นต์ความเปลี่ยนแปลงของน้ำฝน (-50% ถึง +50%) เพื่อจำลองกรณีเกิดปรากฏการณ์ **เอลนีโญ (El Niño)** หรือ **ลานีญา (La Niña)**
- **Real-time Impact Assessment:** คำนวณจำนวนจังหวัดที่จะเข้าสู่ภาวะวิกฤติน้ำท่วม (Flash Flood Risk) และภัยแล้ง (Drought Stress) พร้อมแสดงรายชื่อจังหวัดที่ต้องเฝ้าระวังทันที

### 5. 📈 อนุกรมเวลา 55 ปี & พยากรณ์ล่วงหน้า (Long-Term Trends & 12M Forecast)
- **Time-Series Analysis (1970 - 2025):** เส้นแนวโน้ม Moving Average 12 เดือน และแนวโน้ม 5 ปี
- **Historic Extreme Events:** ไฮไลท์มหาอุทกภัยปี 2554 (2011 Flood) และภัยแล้งรุนแรงปี 2558
- **🔮 Predictive Forward Forecast (12 เดือนข้างหน้า):** พยากรณ์แนวโน้มปริมาณน้ำฝนล่วงหน้าด้วยแบบจำลองอนุกรมเวลา พร้อมแถบช่วงความเชื่อมั่น (Confidence Interval Band)
- **Climate Heatmap:** แผนที่ความร้อนรอบมรสุมรายเดือนตัดกับรายปี 50 ปี

### 6. 🏘️ เรดาร์ระดับอำเภอ 928 แห่ง (Amphoe Radar Explorer)
- สืบค้นข้อมูลสถานีวัดน้ำฝนรายอำเภอทั่วประเทศ (Dataset: `monthlyrain_amphoe_2010to2014.csv`)
- จัดอันดับอำเภอที่มีฝนสะสมสูงสุดในแต่ละจังหวัด พร้อมตารางแสดงข้อมูลอย่างละเอียด

### 7. 🏆 ศูนย์จัดอันดับ & ส่งออกข้อมูล (Rankings & Data Export)
- Top 10 Wettest vs Top 10 Driest Provinces
- ค้นหารายชื่อจังหวัดแบบ Dynamic Search
- ปุ่ม Export CSV (เข้ารหัส UTF-8 with BOM รองรับ Excel ภาษาไทยสมบูรณ์แบบ)

---

## 🛠️ วิธีการรันใช้งาน (Local Setup)

```bash
# 1. ติดตั้ง Dependencies
pip install -r requirements.txt

# 2. รันแอปพลิเคชัน
streamlit run app.py
```
เปิดเบราว์เซอร์ไปที่: `http://localhost:8501`

---

## 🌐 ขั้นตอนการ Deploy สู่ Streamlit Community Cloud (ฟรี & คลิกเดียว)

1. **Push โค้ดขึ้น GitHub:**
   ```bash
   git add .
   git commit -m "feat: HydroPulse TH National Water Intelligence Dashboard"
   git branch -M main
   git push -u origin main
   ```
2. เข้าไปที่ **[share.streamlit.io](https://share.streamlit.io)** แล้วล็อกอินด้วย GitHub
3. คลิก **"New app"** หรือ **"Deploy an app"**
4. เลือก Repository ของคุณ, Branch: `main`, Main file path: `app.py`
5. คลิก **"Deploy!"** ระบบจะติดตั้งแพ็กเกจจาก `requirements.txt` และเปิดใช้งานออนไลน์ได้ทันที

---

## 🐳 การ Deploy ด้วย Docker

```bash
docker build -t hydropulse-th .
docker run -d -p 8501:8501 --name hydropulse-app hydropulse-th
```
เข้าใช้งานที่: `http://localhost:8501`
