import streamlit as st
import pandas as pd
from db_config import call_procedure


# =========================
# ENTRY
# =========================

def show_hoa_don_tien_phong():
    st.header("🧾 QUẢN LÝ HÓA ĐƠN TIỀN PHÒNG")

    # Toast message
    if "hdtp_toast" in st.session_state and st.session_state.hdtp_toast:
        st.toast(st.session_state.hdtp_toast, icon="✅")
        st.session_state.hdtp_toast = None

    # State
    if "hdtp_action" not in st.session_state:
        st.session_state.hdtp_action = None

    if st.session_state.hdtp_action == "edit":
        ui_sua_trang_thai()
    else:
        ui_danh_sach()


# =========================
# UI: DANH SÁCH HÓA ĐƠN
# =========================

def ui_danh_sach():
    col1, col2 = st.columns([5, 1])

    with col1:
        st.subheader("📋 Danh sách hóa đơn tiền phòng")

    with col2:
        if st.button("✏️ Sửa trạng thái", key="btn_edit_hdtp"):
            st.session_state.hdtp_action = "edit"
            st.rerun()

    # Lấy dữ liệu
    success, msg, data = call_procedure("sp_hd_tien_phong_danhsach")

    if not success or not data:
        st.info("📭 Chưa có hóa đơn tiền phòng")
        return

    df = pd.DataFrame(data)
    df.columns = [
        "Mã HĐ", "MSV", "Họ tên", "Mã phòng", "Tên KTX",
        "Ngày bắt đầu", "Ngày kết thúc",
        "Loại Block", "Đơn giá",
        "Mã hóa đơn", "Trạng thái TT"
    ]

    # =========================
    # FILTER
    # =========================
    col1, col2, col3 = st.columns(3)

    with col1:
        trang_thai_list = ["Tất cả"] + list(df["Trạng thái TT"].unique())
        filter_tt = st.selectbox("Lọc theo trạng thái", trang_thai_list)

    with col2:
        search_sv = st.text_input("Tìm theo tên SV", placeholder="Nhập tên sinh viên")

    with col3:
        search_phong = st.text_input("Tìm theo mã phòng", placeholder="Nhập mã phòng")

    filtered_df = df.copy()

    if filter_tt != "Tất cả":
        filtered_df = filtered_df[filtered_df["Trạng thái TT"] == filter_tt]

    if search_sv:
        filtered_df = filtered_df[
            filtered_df["Họ tên"].str.contains(search_sv, case=False, na=False)
        ]

    if search_phong:
        filtered_df = filtered_df[
            filtered_df["Mã phòng"].str.contains(search_phong, case=False, na=False)
        ]

    # =========================
    # TABLE
    # =========================
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # METRIC
    # =========================
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Tổng hóa đơn", len(filtered_df))

    with col2:
        da_tt = len(filtered_df[filtered_df["Trạng thái TT"] == "Đã thanh toán"])
        st.metric("Đã thanh toán", da_tt)

    with col3:
        chua_tt = len(filtered_df[filtered_df["Trạng thái TT"] == "Chưa thanh toán"])
        st.metric("Chưa thanh toán", chua_tt)


# =========================
# UI: SỬA TRẠNG THÁI
# =========================

def ui_sua_trang_thai():
    st.subheader("✏️ Sửa trạng thái thanh toán")

    success, msg, data = call_procedure("sp_hd_tien_phong_danhsach")

    if not success or not data:
        st.warning("⚠️ Không có hóa đơn để sửa")
        if st.button("⬅️ Quay lại"):
            st.session_state.hdtp_action = None
            st.rerun()
        return

    # Options selectbox
    hd_options = {
        f"{row['HoTen']} | Phòng {row['MaPhong']} | {row['NgayBatDau']} → {row['NgayKetThuc']} | {row['TrangThaiTT']}": row
        for row in data
    }

    selected = st.selectbox(
        "Chọn hóa đơn",
        list(hd_options.keys())
    )

    row = hd_options[selected]

    # Thông tin hóa đơn
    st.info(
        f"**Thông tin hóa đơn:**\n\n"
        f"• Sinh viên: **{row['HoTen']}** ({row['MSV']})\n"
        f"• Phòng: **{row['MaPhong']} - {row['TenKTX']}**\n"
        f"• Thời gian: **{row['NgayBatDau']}** → **{row['NgayKetThuc']}**\n"
        f"• Loại block: **{row['LoaiBlock']}**\n"
        f"• Đơn giá block: **{row['DonGia']:,.0f} VNĐ**\n"
    )

    # Trạng thái
    trang_thai_options = ["Chưa thanh toán", "Đã thanh toán"]
    current_index = (
        trang_thai_options.index(row["TrangThaiTT"])
        if row["TrangThaiTT"] in trang_thai_options else 0
    )

    trang_thai_moi = st.selectbox(
        "Trạng thái thanh toán",
        trang_thai_options,
        index=current_index
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Cập nhật", type="primary"):
            success, msg, _ = call_procedure(
                "sp_sua_trang_thai_hoa_don",
                [row["MaHoaDon"], trang_thai_moi]
            )
            if success:
                st.session_state.hdtp_toast = "Cập nhật trạng thái thành công!"
                st.session_state.hdtp_action = None
                st.rerun()
            else:
                st.error(f"❌ {msg}")

    with col2:
        if st.button("⬅️ Quay lại"):
            st.session_state.hdtp_action = None
            st.rerun()


# =========================
# RUN
# =========================

if __name__ == "__main__":
    show_hoa_don_tien_phong()
