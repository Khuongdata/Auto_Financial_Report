import pandas as pd
from fpdf import FPDF
import streamlit as st
import matplotlib.pyplot as plt
import os

# Đọc dữ liệu từ file CSV
file_path = 'BCTCKH.csv'
data = pd.read_csv(file_path)
industry_data = pd.read_csv("TBN.csv")
industry_data['Năm']= pd.to_numeric(industry_data['Năm'], errors='coerce').astype(int)
industry_data['ROA'] = pd.to_numeric(industry_data['ROA'], errors='coerce')  # Sử dụng 'coerce' để thay NaN cho các giá trị không hợp lệ
industry_data['ROE'] = pd.to_numeric(industry_data['ROE'], errors='coerce')
bc_data = pd.read_csv('BCDKT.csv')
pl_data = pd.read_csv('KQKD.csv')
cf_data = pd.read_csv('LCTT.csv')
code_avg = pd.read_csv('Average_by_Code.csv')
sector_avg = pd.read_csv('Average_by_Sector.csv')
code_avg.columns = code_avg.columns.str.strip()
sector_avg.columns = sector_avg.columns.str.strip()


def add_financial_comparison_table(pdf, ticker):
    pdf.add_page()
    pdf.set_font("DejaVu", size=14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(200, 10, txt="Chỉ Số Sinh Lời", ln=True, align='C')
    pdf.set_font("DejaVu", size=10)
    pdf.set_fill_color(255, 255, 210)  # Vàng nhạt
    pdf.set_text_color(0, 0, 0)

    headers = ["Chỉ Số", ticker, "Trung Bình Ngành", "So Sánh"]
    col_widths = [80, 30, 40, 40]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1, fill=True, align='C')
    pdf.ln()

    metrics = [
        ("ROA", "Tỷ suất sinh lời trên tài sản (%)"),
        ("ROE", "Tỷ suất sinh lời trên vốn (%)"),
        ("ROS", "Tỷ suất sinh lời trên doanh thu (%)"),
        ("EBIT Margin", "Tỷ suất lợi nhuận trước lãi vay và thuế (%)"),
        ("EBITDA Margin", "Tỷ suất lợi nhuận trước khấu hao, lãi vay và thuế (%)"),
        ("Gross Profit Margin", "Tỷ suất lợi nhuận gộp (%)")
    ]

    company_filtered = code_avg[code_avg['Mã'] == ticker]
    if company_filtered.empty:
        pdf.cell(0, 10, txt=f"Không tìm thấy dữ liệu chỉ số cho công ty {ticker}", ln=True)
        return

    company_row = company_filtered.iloc[0]
    sector = company_row['Sector']

    sector_filtered = sector_avg[sector_avg['Sector'].str.strip().str.lower() == sector.strip().lower()]
    if sector_filtered.empty:
        pdf.cell(0, 10, txt=f"Không tìm thấy dữ liệu trung bình ngành cho ngành {sector}", ln=True)
        return

    sector_row = sector_filtered.iloc[0]

    for m_code, m_desc in metrics:
        val_comp = company_row[m_code]
        val_sec = sector_row[m_code]
        delta = val_comp - val_sec
        delta_str = f"{delta:+.2f}"
        color = (0, 128, 0) if delta > 0 else (220, 0, 0)

        # Ghi nhớ vị trí bắt đầu
        x_start = pdf.get_x()
        y_start = pdf.get_y()

        # Vẽ ô chỉ số (sẽ chiếm nhiều dòng nếu dài)
        pdf.multi_cell(col_widths[0], 8, f"{m_code} - {m_desc}", border=1)
        y_end = pdf.get_y()
        row_height = y_end - y_start

        # Vẽ các cột còn lại cùng dòng
        pdf.set_xy(x_start + col_widths[0], y_start)
        pdf.cell(col_widths[1], row_height, f"{val_comp:.2f}", border=1, align='R')
        pdf.cell(col_widths[2], row_height, f"{val_sec:.2f}", border=1, align='R')
        pdf.set_text_color(*color)
        pdf.cell(col_widths[3], row_height, delta_str, border=1, align='R')
        pdf.set_text_color(0, 0, 0)

        # Xuống dòng cho hàng tiếp theo
        pdf.set_y(y_end)

# Biểu đồ thanh khoản

def generate_liquidity_chart(ticker):
    metrics = ["Current Ratio", "Quick Ratio"]
    labels = ["Current Ratio", "Quick Ratio"]
    company_row = code_avg[code_avg['Mã'] == ticker].iloc[0]
    sector_row = sector_avg[sector_avg['Sector'].str.strip().str.lower() == company_row['Sector'].strip().lower()].iloc[0]

    values_company = [company_row[m] for m in metrics]
    values_sector = [sector_row[m] for m in metrics]

    x = range(len(metrics))
    plt.figure(figsize=(8, 4))
    plt.bar(x, values_company, width=0.4, label="Công ty", color='#00BFFF')
    plt.bar([i + 0.4 for i in x], values_sector, width=0.4, label="Trung bình ngành", color='white', edgecolor='#00BFFF')
    plt.xticks([i + 0.2 for i in x], labels, rotation=45)
    plt.title("Chỉ số Thanh khoản")
    plt.xlabel("Chỉ số")
    plt.legend()
    plt.tight_layout()
    filename = f"liquidity_chart_{ticker}.png"
    plt.savefig(filename)
    plt.close()
    return filename

# Biểu đồ hiệu quả hoạt động

def generate_efficiency_chart(ticker):
    metrics = ["Working Capital Turnover", "Total Asset Turnover"]
    labels = ["Working Capital Turnover", "Total Asset Turnover"]
    company_row = code_avg[code_avg['Mã'] == ticker].iloc[0]
    sector_row = sector_avg[sector_avg['Sector'].str.strip().str.lower() == company_row['Sector'].strip().lower()].iloc[0]

    values_company = [company_row[m] for m in metrics]
    values_sector = [sector_row[m] for m in metrics]

    x = range(len(metrics))
    plt.figure(figsize=(8, 4))
    plt.bar(x, values_company, width=0.4, label="Công ty", color='#00BFFF')
    plt.bar([i + 0.4 for i in x], values_sector, width=0.4, label="Trung bình ngành", color='white', edgecolor='#00BFFF')
    plt.xticks([i + 0.2 for i in x], labels, rotation=45)
    plt.title("Chỉ số Hiệu quả hoạt động")
    plt.xlabel("Chỉ số")
    plt.legend()
    plt.tight_layout()
    filename = f"efficiency_chart_{ticker}.png"
    plt.savefig(filename)
    plt.close()
    return filename

# ================== BIỂU ĐỒ TỔNG QUAN THỊ TRƯỜNG ==================

def plot_top_sectors_bar(excel_path):
    df = pd.read_excel(excel_path, sheet_name=0)
    df['Sector'] = df['Sector'].fillna('Unclassified')
    sector_counts = df['Sector'].value_counts().head(10)
    plt.figure(figsize=(8, 5))
    sector_counts.sort_values().plot(kind='barh', color='#00BFFF')
    plt.title("Top 10 ngành có số lượng công ty nhiều nhất")
    plt.xlabel("Số công ty")
    plt.tight_layout()
    chart_path = "top_sectors_bar.png"
    plt.savefig(chart_path)
    plt.close()
    return chart_path

def plot_listing_by_year(excel_path):
    df = pd.read_excel(excel_path, sheet_name=0)
    df = df[df['Hist.'].notna()]
    year_counts = df['Hist.'].astype(int).value_counts().sort_index()
    plt.figure(figsize=(8, 4))
    year_counts.plot(kind='line', marker='o', color='#1ABC9C')
    plt.title("Số lượng công ty niêm yết theo năm")
    plt.xlabel("Năm")
    plt.ylabel("Số công ty")
    plt.grid(True)
    plt.tight_layout()
    chart_path = "listing_by_year.png"
    plt.savefig(chart_path)
    plt.close()
    return chart_path
# ================== BIỂU ĐỒ GIÁ CỔ PHIẾU TỪ FILE price_formatted.csv ==================
import pandas as pd

price_df = pd.read_csv("C:/Users/khuon/G1/price.csv")
price_df.columns = price_df.columns.str.strip()
price_df_dates = price_df.columns[2:]  # Các cột ngày dạng MM/DD

# Hàm tạo biểu đồ giá cổ phiếu theo ngày từ file price.csv

def plot_price_from_csv(code):
    row = price_df[price_df['Code'] == code].iloc[0]
    series = row[price_df_dates]
    # Chuyển index thành datetime để vẽ trục thời gian chính xác
    series.index = pd.to_datetime(price_df_dates, format='%d-%b')
    plt.figure(figsize=(8, 4))
    plt.plot(series.index, series.values, marker='o', linestyle='-', color='#00BFFF')

    plt.title(f'Giá cổ phiếu tháng 12/2024 - {code}')
    plt.xlabel('Ngày')
    plt.ylabel('Giá đóng cửa (Close)')
    plt.grid(True)

    import matplotlib.dates as mdates
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
    plt.xticks(rotation=45)
    plt.tight_layout()

    chart_path = f"{code}_Dec2024_line_chart.png"
    plt.savefig(chart_path)
    plt.close()
    return chart_path

# ================== KẾT NỐI GEMINI API ĐỂ TỰ ĐỘNG VIẾT NỘI DUNG ==================
import google.generativeai as genai

# Cấu hình API KEY của bạn (thay bằng key thật khi sử dụng)
GEMINI_API_KEY = "AIzaSyDkqNSCiRt1Z-KZOmnO02G9MI1BFpkigaM"

def init_gemini():
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("models/gemini-1.5-pro-latest")


def generate_financial_story_gemini(code, roe, roa, sector_roe, sector_roa):
    model = init_gemini()
    prompt = f"""
    Bạn là một chuyên gia phân tích tài chính.
    So sánh chỉ số ROA (tỷ suất sinh lời trên tài sản) của công ty {code} với trung bình ngành:
    - ROA của công ty: {roa:.2f}%
    - ROA trung bình ngành: {sector_roa:.2f}%

    Hãy viết 1 câu chuyện tài chính dài rằng ROA của ngành {code} thấp vì bị ảnh hưởng bởi Covid nhưng
    nhưng công ty {code} là hậu cần quân đội  nên vẫn ổn định => mã cổ phiếu như thế nào?
    """
    response = model.generate_content(prompt)
    return response.text if response else "Không thể tạo nội dung tự động."

def plot_roa_by_sector(industry_name):
    
    filtered = industry_data[industry_data['Ngành ICB - cấp 1'] == industry_name]
    print("Ngành truyền vào:", industry_name)
    print("Dữ liệu lọc được:")
    print(filtered[['Năm', 'ROA']])

    plt.figure(figsize=(8, 5))
    plt.plot(filtered['Năm'], filtered['ROA'], marker='o', color='blue')
    plt.title(f'Biểu đồ ROA (%) ngành: {industry_name}')
    plt.xlabel("Năm")
    plt.ylabel("ROA (%)")
    plt.xticks(filtered['Năm'])  # 🟢 fix mốc năm
    plt.minorticks_on()
    plt.grid(which='major', linestyle='-', linewidth=0.5)
    plt.grid(which='minor', linestyle=':', linewidth=0.5)

    # Thêm nhãn từng điểm
    for x, y in zip(filtered['Năm'], filtered['ROA']):
        plt.text(x, y, f"{y:.2%}", ha='center', va='bottom', fontsize=15)

    plt.tight_layout()
    filename = f"roa_{industry_name}.png"
    plt.savefig(filename)
    plt.close()
    return filename

def plot_roe_by_sector(industry_name):
    filtered = industry_data[industry_data['Ngành ICB - cấp 1'] == industry_name]
    if filtered.empty:
        print(f"Không tìm thấy dữ liệu ROE cho ngành: {industry_name}")
        return None
    plt.figure(figsize=(8, 5))
    plt.plot(filtered['Năm'], filtered['ROE'], marker='x', color='green')
    plt.title(f'Biểu đồ ROE (%) ngành: {industry_name}')
    plt.xlabel("Năm")
    plt.ylabel("ROE (%)")
    plt.xticks(filtered['Năm'])  # 🟢 fix mốc năm
    plt.minorticks_on()
    plt.grid(which='major', linestyle='-', linewidth=0.5)
    plt.grid(which='minor', linestyle=':', linewidth=0.5)
    
    

    # Thêm nhãn từng điểm
    for x, y in zip(filtered['Năm'], filtered['ROE']):
        plt.text(x, y, f"{y:.2%}", ha='center', va='bottom', fontsize=15)

    plt.tight_layout()
    filename = f"roe_{industry_name}.png"
    plt.savefig(filename)
    plt.close()
    return filename


# Lọc dữ liệu từ cột C đến K (Mã công ty, Tên công ty, Sàn giao dịch, Ngành nghề, Quý và Năm)
company_info = data.iloc[:, 2:11]

# Kiểm tra font tồn tại hay không
FONT_PATH = "DejaVuSans.ttf"
if not os.path.exists(FONT_PATH):
    FONT_PATH = None  # Nếu không tìm thấy, dùng font mặc định của FPDF

# Hàm thêm bảng tài chính vào PDF
def add_financial_table(pdf, data, title, ticker, fields):
    pdf.add_page()
    pdf.set_font("DejaVu", size=14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.set_font("DejaVu", size=10)
    pdf.set_fill_color(255, 255, 210)  # Vàng nhạt
    pdf.set_text_color(0, 0, 0)

    headers = ["Chỉ tiêu", "Giá trị"]
    col_widths = [120, 70]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1, fill=True, align='C')
    pdf.ln()

    filtered_data = data[data['Mã'] == ticker]
    if filtered_data.empty:
        pdf.cell(0, 10, txt=f"Không tìm thấy dữ liệu cho công ty {ticker}", ln=True)
        return

    for field in fields:
        value = filtered_data[field].values[0] if field in filtered_data.columns else "N/A"
        pdf.cell(col_widths[0], 8, field, border=1)
        pdf.cell(col_widths[1], 8, f"{value}", border=1, align='R')
        pdf.ln()

# Hàm tạo PDF cho từng công ty
def create_pdf(ticker, info):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
# Thêm màu nền cho trang bìa
    pdf.set_fill_color(255, 223, 186)  # Màu vàng nhạt
    pdf.rect(0, 0, 210, 297, 'F')  # Màu nền cho toàn bộ trang
# Kiểm tra và đặt font
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font("DejaVu", size=12)


    # Thêm tiêu đề
    pdf.set_text_color(0, 51, 102)  # Màu xanh đậm cho tiêu đề
    pdf.cell(200, 10, txt='Báo cáo phân tích công ty', ln=True, align='C')
    pdf.cell(200, 10, txt=f"Báo cáo thông tin công ty: {info['Mã']} - {info['Tên công ty']}", ln=True, align='C')
    pdf.ln(10)

    # Thêm thông tin công ty
    pdf.set_text_color(0, 0, 0)  # Màu đen cho nội dung
    for column in company_info.columns:
        pdf.cell(200, 10, txt=f"{column}: {str(info[column])}", ln=True)
        
    pdf.ln(10)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())

    bcdkt_fields = ["Tiền và tương đương tiền", "TỔNG CỘNG TÀI SẢN", "Vay và nợ thuê tài chính ngắn hạn", "Vay và nợ thuê tài chính dài hạn", "Người mua trả tiền trước ngắn hạn", "Người mua trả tiền trước dài hạn", "VỐN CHỦ SỞ HỮU", "Vốn góp của chủ sở hữu", "Thặng dư vốn cổ phần", "Vốn khác", "TỔNG CỘNG NGUỒN VỐN"]
    kqkd_fields = ["Doanh thu thuần", "Lợi nhuận gộp về bán hàng và cung cấp dịch vụ", "Lợi nhuận thuần từ hoạt động kinh doanh", "Chi phí tài chính", "Lợi nhuận khác", "Lợi nhuận sau thuế thu nhập doanh nghiệp"]
    lctt_fields = ["Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh (TT)", "Lưu chuyển tiền tệ từ hoạt động tài chính (TT)", "Lưu chuyển tiền tệ ròng từ hoạt động đầu tư (TT)", "Tiền và tương đương tiền cuối kỳ (TT)"]

      # Bảng Cân đối kế toán
    add_financial_table(pdf, bc_data, "BẢNG CÂN ĐỐI KẾ TOÁN 2023 (VND)", ticker, bcdkt_fields)

    # Bảng KQKD
    add_financial_table(pdf, pl_data, "KẾT QUẢ KINH DOANH 2023 (VND)", ticker, kqkd_fields)

    # Bảng Lưu chuyển tiền tệ
    add_financial_table(pdf, cf_data, "LƯU CHUYỂN TIỀN TỆ 2023 (VND)", ticker, lctt_fields)


       # Trang biểu đồ ROA và ROE cùng một trang
    # Trang biểu đồ ROA và ROE cùng một trang
    roa_chart = plot_roa_by_sector(info['Ngành ICB - cấp 1'])
    roe_chart = plot_roe_by_sector(info['Ngành ICB - cấp 1'])
    pdf.add_page()
    pdf.set_font("DejaVu", size=14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(200, 10, txt=f"Biểu đồ ROA (%) - Ngành {info['Ngành ICB - cấp 1']}", ln=True, align='C')
    pdf.image(roa_chart, x=10, y=30, w=190)
    pdf.set_y(145)
    pdf.cell(200, 10, txt=f"Biểu đồ ROE (%) - Ngành {info['Ngành ICB - cấp 1']}", ln=True, align='C')
    pdf.image(roe_chart, x=10, y=160, w=190)



     # Trang bảng so sánh chỉ số
    add_financial_comparison_table(pdf, ticker)
    # Biểu đồ thanh khoản + hiệu quả hoạt động chèn cùng trang "Chỉ số Sinh Lời"
    liquidity_chart = generate_liquidity_chart(ticker)
    efficiency_chart = generate_efficiency_chart(ticker)
    pdf.add_page()
    pdf.set_font("DejaVu", size=14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(200, 10, txt=f"Biểu đồ so sánh Chỉ số Thanh khoản - {ticker}", ln=True, align='C')
    pdf.image(liquidity_chart, x=10, y=30, w=190)
    pdf.set_y(145)
    pdf.cell(200, 10, txt=f"Biểu đồ so sánh Chỉ số Hiệu quả hoạt động - {ticker}", ln=True, align='C')
    pdf.image(efficiency_chart, x=10, y=160, w=190)

    # ================== CHÈN VÀO create_pdf ==================
    # Thêm trang biểu đồ tổng quan thị trường
    try:
        sector_chart = plot_top_sectors_bar("Cleaned_Vietnam_Price.xlsx")
        listing_chart = plot_listing_by_year("Cleaned_Vietnam_Price.xlsx")

        pdf.add_page()
        pdf.set_font("DejaVu", size=14)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(200, 10, txt="Tổng quan ngành nghề niêm yết tại Việt Nam", ln=True, align='C')
        pdf.image(sector_chart, x=10, y=30, w=190)
        pdf.set_y(145)
        pdf.cell(200, 10, txt="Tổng quan số lượng niêm yết theo năm", ln=True, align='C')
        pdf.image(listing_chart, x=10, y=160, w=190)

    except Exception as e:
        pdf.add_page()
        pdf.set_font("DejaVu", size=12)
        pdf.set_text_color(255, 0, 0)
        pdf.cell(200, 10, txt=f"Lỗi khi tạo biểu đồ tổng quan thị trường: {e}", ln=True)

# ================== THÊM VÀO create_pdf ==================
    try:
        code = info['Mã']  # Dựa trên mã công ty được chọn từ giao diện
        if code in price_df['Code'].values:
            price_chart = plot_price_from_csv(code)
            pdf.add_page()
            pdf.set_font("DejaVu", size=14)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(200, 10, txt=f"Biểu đồ giá cổ phiếu tháng 12/2024 - {code}", ln=True, align='C')
            pdf.image(price_chart, x=10, y=30, w=190)
        else:
            pdf.add_page()
            pdf.set_font("DejaVu", size=12)
            pdf.set_text_color(255, 0, 0)
            pdf.cell(200, 10, txt=f"Không tìm thấy dữ liệu giá cổ phiếu cho {code} trong file price.csv", ln=True)
    except Exception as e:
        pdf.add_page()
        pdf.set_font("DejaVu", size=12)
        pdf.set_text_color(255, 0, 0)
        pdf.cell(200, 10, txt=f"Lỗi khi tạo biểu đồ giá cổ phiếu tháng 12/2024: {e}", ln=True)

        # ================== CÁCH THÊM VÀO PDF ==================
    try:
        company_row = code_avg[code_avg['Mã'] == ticker].iloc[0]
        sector_row = sector_avg[sector_avg['Sector'].str.strip().str.lower() == company_row['Sector'].strip().lower()].iloc[0]

        story_text = generate_financial_story_gemini(
            code=ticker,
            roe=company_row['ROE'],
            roa=company_row['ROA'],
            sector_roe=sector_row['ROE'],
            sector_roa=sector_row['ROA'],

        )
            # 👉 Tiêu đề với font to hơn
        pdf.add_page()
        pdf.set_font("DejaVu", size=15)           # Font to cho tiêu đề
        pdf.set_text_color(0, 51, 102)            # Màu xanh đậm
        pdf.cell(200, 10, txt="CÂU CHUYỆN TÀI CHÍNH", ln=True, align='C')
        pdf.ln(5)

        # 👉 Nội dung với font nhỏ hơn
        pdf.set_font("DejaVu", size=11)           # Font nhỏ hơn cho nội dung
        pdf.set_text_color(0, 0, 0)               # Màu đen
        pdf.multi_cell(0, 8, story_text)
    except Exception as e:
        pdf.add_page()
        pdf.set_font("DejaVu", size=12)
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 10, f"Lỗi khi sinh nội dung AI: {str(e)}", ln=True)
    # Lưu báo cáo PDF
    pdf_filename = f"{ticker}_company_report.pdf"
    pdf.output(pdf_filename, 'F')

    return pdf_filename

# Giao diện Streamlit
st.title('Chọn công ty để xuất báo cáo PDF')
st.write("Chọn mã công ty từ danh sách dưới đây để xuất báo cáo PDF.")

# Tạo danh sách các mã công ty để người dùng chọn
ticker_list = company_info['Mã'].unique()
selected_ticker = st.selectbox('Chọn mã công ty', ticker_list)

# Hiển thị thông tin công ty khi chọn
st.write('Báo cáo phânn tích công ty')
selected_company = company_info[company_info['Mã'] == selected_ticker].iloc[0]
st.write(f"Thông tin công ty: {selected_company['Tên công ty']}")
st.write(f"Sàn giao dịch: {selected_company['Sàn']}")
st.write(f"Ngành cấp 1: {selected_company['Ngành ICB - cấp 1']}")
st.write(f"Ngành cấp 2: {selected_company['Ngành ICB - cấp 2']}")
st.write(f"Ngành cấp 3: {selected_company['Ngành ICB - cấp 3']}")
st.write(f"Ngành cấp 4: {selected_company['Ngành ICB - cấp 4']}")
st.write(f"Quý: {selected_company['Quý']}")
st.write(f"Năm: {selected_company['Năm']}")
st.write("Danh sách ngành trong file TBN.csv:")
st.write(industry_data['Ngành ICB - cấp 1'].unique())

# Khi người dùng chọn công ty và nhấn nút, tạo PDF
if st.button('Tạo báo cáo PDF'):
    pdf_file = create_pdf(selected_ticker, selected_company)
    st.success(f"Đã tạo báo cáo PDF cho công ty {selected_ticker}")

    # Cho phép người dùng tải file PDF
    with open(pdf_file, "rb") as file:
        st.download_button(
            label="Tải xuống báo cáo PDF",
            data=file,
            file_name=pdf_file,
            mime="application/pdf"
        )