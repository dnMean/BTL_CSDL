import streamlit as st

# Import các module chức năng
from modules.sinh_vien import show_sinh_vien
from modules.xe import show_xe
from modules.ve_thang import show_ve_thang
from modules.ve_luot import show_ve_luot
from modules.hop_dong import show_hop_dong
from modules.hoa_don_dich_vu import show_hoa_don_dich_vu
from modules.ktx import show_ktx
from modules.loai_phong import show_loai_phong
from modules.bang_gia import show_bang_gia
from modules.phong import show_phong
from modules.hoa_don_tien_phong import show_hoa_don_tien_phong
from modules.dich_vu import show_dich_vu
from modules.su_dung_dich_vu import show_su_dung_dich_vu
from modules.tong_hoa_don_theo_thang import show_tong_hoa_don_theo_thang
from modules.thong_ke_doanh_thu_dich_vu import show_thong_ke_doanh_thu
# Cấu hình trang
st.set_page_config(
    page_title="Quản lý Ký Túc Xá",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .stButton > button {
        width: 100%;
    }
    .menu-item {
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar - Menu điều hướng
with st.sidebar:
    st.markdown('<p class="sidebar-header">🏠 Quản lý KTX</p>', unsafe_allow_html=True)
    st.divider()
    
    # Menu options
    menu_options = {
        "🏠 Trang chủ": "home",
        "🎓 Quản lý Sinh Viên": "sinh_vien",
        "🏍️ Quản lý Xe": "xe",
        "🎫 Quản lý Vé Tháng": "ve_thang",
        "🎟️ Quản lý Vé Lượt": "ve_luot",
        "📝 Quản lý Hợp Đồng": "hop_dong",
        "🧾 Hóa Đơn Dịch Vụ": "hoa_don_dich_vu",
        "🏢 Quản lý KTX" : "ktx",
        "Quản lý loại phòng": "loai_phong",
        "Quản lý Bảng Giá": "bang_gia",
        "Quản lý Phòng": "phong",
        "Quản lý Hoá đơn tiền phòng": "hop_dong_tien_phong",
        "Quản lý Dịch vụ" : "dich_vu",
        "Quản lý Sử dụng dịch vụ": "su_dung_dich_vu",
        "Tổng hoá đơn theo tháng": "tong_hoa_don_theo_thang",
        "Thống kê doanh thu dịch vụ": "thong_ke_doanh_thu_dich_vi"
    }
    
    # Sử dụng radio buttons cho menu
    selected_menu = st.radio(
        "📋 Chọn chức năng",
        options=list(menu_options.keys()),
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Thông tin kết nối
    st.markdown("### ⚙️ Cấu hình DB")
    st.caption("Host: localhost")
    st.caption("Database: BTL_CSDL")
    
    # Kiểm tra kết nối
    from db_config import get_connection
    conn = get_connection()
    if conn:
        st.success("✅ Đã kết nối DB")
        conn.close()
    else:
        st.error("❌ Lỗi kết nối DB")

# Main content area
if menu_options[selected_menu] == "home":
    # Trang chủ
    st.markdown('<p class="main-header">🏠 Hệ Thống Quản Lý Ký Túc Xá</p>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 👋 Chào mừng đến với hệ thống quản lý ký túc xá!
    
    Hệ thống này giúp bạn quản lý các hoạt động của ký túc xá một cách hiệu quả.
    """)
    
    st.divider()
    
elif menu_options[selected_menu] == "sinh_vien":
    show_sinh_vien()

elif menu_options[selected_menu] == "xe":
    show_xe()

elif menu_options[selected_menu] == "ve_thang":
    show_ve_thang()

elif menu_options[selected_menu] == "ve_luot":
    show_ve_luot()

elif menu_options[selected_menu] == "hop_dong":
    show_hop_dong()

elif menu_options[selected_menu] == "hoa_don_dich_vu":
    show_hoa_don_dich_vu()
elif menu_options[selected_menu] == "ktx":
    show_ktx()
elif menu_options[selected_menu] == "loai_phong":
    show_loai_phong()

elif menu_options[selected_menu] == "bang_gia":
    show_bang_gia()

elif menu_options[selected_menu] == "phong":
    show_phong()

elif menu_options[selected_menu] == "hop_dong_tien_phong":
    show_hoa_don_tien_phong()

elif menu_options[selected_menu] == "dich_vu":
    show_dich_vu()


elif menu_options[selected_menu] == "su_dung_dich_vu":
    show_su_dung_dich_vu()


elif menu_options[selected_menu] == "tong_hoa_don_theo_thang":
    show_tong_hoa_don_theo_thang()

elif menu_options[selected_menu] == "thong_ke_doanh_thu_dich_vi":
    show_thong_ke_doanh_thu()

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8rem;">
    © 2024 Hệ thống Quản lý Ký Túc Xá | Developed with ❤️ using Streamlit
</div>
""", unsafe_allow_html=True)