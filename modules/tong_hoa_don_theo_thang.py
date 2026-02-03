import streamlit as st
import pandas as pd
from db_config import call_procedure


# =========================
# PAGE: DANH SÁCH HÓA ĐƠN
# =========================
def show_danh_sach_hoa_don():
    st.header("📊 TỔNG HÓA ĐƠN CHƯA THANH TOÁN THEO THÁNG")

    # =========================
    # LOAD DATA
    # =========================
    success, msg, data = call_procedure(
        "sp_tong_hoa_don_chua_tt_theo_thang_all_sv"
    )

    if not success or not data:
        st.info("📭 Không có dữ liệu hóa đơn chưa thanh toán")
        return

    df = pd.DataFrame(data)
    df.columns = [
        "MSV",
        "Họ tên",
        "Tháng / Năm",
        "Tiền phòng",
        "Tiền dịch vụ",
        "Tổng phải trả"
    ]

    for col in ["Tiền phòng", "Tiền dịch vụ", "Tổng phải trả"]:
        df[col] = df[col].astype(float)

    # =========================
    # FILTER
    # =========================
    col1, col2, col3 = st.columns(3)

    with col1:
        thang_list = ["Tất cả"] + sorted(df["Tháng / Năm"].unique().tolist())
        filter_thang = st.selectbox("📅 Lọc theo tháng", thang_list)

    with col2:
        search_sv = st.text_input("🔍 Tìm theo tên sinh viên")

    with col3:
        search_msv = st.text_input("🔍 Tìm theo MSV")

    filtered_df = df.copy()

    if filter_thang != "Tất cả":
        filtered_df = filtered_df[
            filtered_df["Tháng / Năm"] == filter_thang
        ]

    if search_sv:
        filtered_df = filtered_df[
            filtered_df["Họ tên"].str.contains(search_sv, case=False, na=False)
        ]

    if search_msv:
        filtered_df = filtered_df[
            filtered_df["MSV"].str.contains(search_msv, case=False, na=False)
        ]

    # =========================
    # TABLE HEADER
    # =========================
    st.subheader("📋 Danh sách hóa đơn")

    header_cols = st.columns([1.3, 2.8, 1.6, 1.6, 1.6, 1.8, 1.2])
    headers = [
        "MSV", "Họ tên", "Tháng / Năm",
        "Tiền phòng", "Tiền dịch vụ", "Tổng phải trả", "Chi tiết"
    ]

    for col, h in zip(header_cols, headers):
        col.markdown(f"**{h}**")

    st.divider()

    # =========================
    # TABLE BODY + BUTTON
    # =========================
    for idx, row in filtered_df.iterrows():
        cols = st.columns([1.3, 2.8, 1.6, 1.6, 1.6, 1.8, 1.2])

        cols[0].write(row["MSV"])
        cols[1].write(row["Họ tên"])
        cols[2].write(row["Tháng / Năm"])
        cols[3].write(f"{row['Tiền phòng']:,.0f}")
        cols[4].write(f"{row['Tiền dịch vụ']:,.0f}")
        cols[5].write(f"{row['Tổng phải trả']:,.0f}")

        if cols[6].button("👁 Xem", key=f"detail_{idx}"):
            st.session_state["current_page"] = "chi_tiet"
            st.session_state["detail_msv"] = row["MSV"]
            st.session_state["detail_ho_ten"] = row["Họ tên"]
            st.session_state["detail_thang"] = row["Tháng / Năm"]
            st.rerun()

    # =========================
    # METRIC
    # =========================
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("👨‍🎓 Số sinh viên", filtered_df["MSV"].nunique())

    with col2:
        st.metric("🧾 Số dòng hóa đơn", len(filtered_df))

    with col3:
        st.metric(
            "💰 Tổng tiền chưa thu",
            f"{filtered_df['Tổng phải trả'].sum():,.0f} VNĐ"
        )


# =========================
# PAGE: CHI TIẾT HÓA ĐƠN
# =========================
def show_chi_tiet_hoa_don():
    msv = st.session_state.get("detail_msv")
    ho_ten = st.session_state.get("detail_ho_ten")
    thang = st.session_state.get("detail_thang")

    # =========================
    # BACK BUTTON
    # =========================
    if st.button("⬅️ Quay lại danh sách"):
        st.session_state["current_page"] = "danh_sach"
        st.rerun()

    # =========================
    # HEADER
    # =========================
    st.header("🧾 CHI TIẾT HÓA ĐƠN CHƯA THANH TOÁN")
    
    # Thông tin sinh viên
    st.markdown("---")
    info_col1, info_col2, info_col3 = st.columns(3)
    
    with info_col1:
        st.markdown(f"**👤 Mã sinh viên:** {msv}")
    
    with info_col2:
        st.markdown(f"**📛 Họ tên:** {ho_ten}")
    
    with info_col3:
        st.markdown(f"**📅 Tháng / Năm:** {thang}")
    
    st.markdown("---")

    # =========================
    # LOAD DETAIL DATA
    # =========================
    success, msg, data = call_procedure(
        "sp_chi_tiet_hoa_don_chua_tt",
        [msv, thang]
    )

    if not success or not data:
        st.info("📭 Không có hóa đơn chi tiết")
        return

    df = pd.DataFrame(data)
    df.columns = [
        "Loại hóa đơn",
        "Mô tả",
        "Từ ngày",
        "Đến ngày",
        "Số tiền"
    ]

    df["Số tiền"] = df["Số tiền"].astype(float)

    # =========================
    # DETAIL TABLE
    # =========================
    st.subheader("📋 Danh sách chi tiết")
    
    st.dataframe(
        df.style.format({
            "Số tiền": "{:,.0f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # SUMMARY
    # =========================
    st.markdown("---")
    
    summary_col1, summary_col2 = st.columns(2)
    
    with summary_col1:
        st.metric(
            "🧾 Số mục",
            len(df)
        )
    
    with summary_col2:
        st.metric(
            "💰 Tổng tiền phải trả",
            f"{df['Số tiền'].sum():,.0f} VNĐ"
        )


# =========================
# MAIN CONTROLLER
# =========================
def show_tong_hoa_don_theo_thang():
    # Khởi tạo session state nếu chưa có
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "danh_sach"

    # Điều hướng theo page hiện tại
    if st.session_state["current_page"] == "danh_sach":
        show_danh_sach_hoa_don()
    elif st.session_state["current_page"] == "chi_tiet":
        show_chi_tiet_hoa_don()


# =========================
# RUN
# =========================
if __name__ == "__main__":
    show_tong_hoa_don_theo_thang()