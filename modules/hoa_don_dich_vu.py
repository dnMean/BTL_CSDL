import streamlit as st
import pandas as pd
from datetime import date
from db_config import call_procedure_v2


def show_hoa_don_dich_vu():
    st.header("🧾 QUẢN LÝ HÓA ĐƠN DỊCH VỤ")

    # ================= TAB =================
    tab1, = st.tabs(["📋 Danh sách hóa đơn"])

    with tab1:
        col_reload, col_space = st.columns([1, 5])
        with col_reload:
            if st.button("🔄 Tải lại dữ liệu"):
                st.rerun()

        # ================= LẤY DỮ LIỆU =================
        data = call_procedure_v2("get_hoa_don_dich_vu")

        if not data:
            st.warning("Không có dữ liệu hóa đơn dịch vụ")
            return

        df = pd.DataFrame(
            data,
            columns=[
                "Mã Hóa Đơn",
                "Tháng-Năm",
                "Trạng Thái TT",
                "Mã Sinh Viên",
                "Họ Tên",
                "Tổng Tiền"
            ]
        )


        # ================= FORMAT =================
        df["Trạng Thái"] = df["Trạng Thái TT"].apply(
            lambda x: "Đã thanh toán" if x == 1 else "Chưa thanh toán"
        )

        df.drop(columns=["Trạng Thái TT"], inplace=True)


        # ================= FILTER =================
        col1, col2, col3 = st.columns(3)

        with col1:
            filter_status = st.selectbox(
                "Trạng thái",
                ["Tất cả", "Đã thanh toán", "Chưa thanh toán"]
            )

        with col2:
            months = ["Tất cả"] + sorted(df["Tháng-Năm"].unique().tolist(), reverse=True)
            filter_month = st.selectbox("Tháng/Năm", months)

        with col3:
            keyword = st.text_input(
                "Tìm MSV / Tên SV",
                placeholder="Nhập MSV hoặc họ tên..."
            )

        filtered_df = df.copy()

        if filter_status != "Tất cả":
            filtered_df = filtered_df[filtered_df["Trạng Thái"] == filter_status]

        if filter_month != "Tất cả":
            filtered_df = filtered_df[filtered_df["Tháng/Năm"] == filter_month]

        if keyword:
            filtered_df = filtered_df[
                filtered_df["MSV"].str.contains(keyword, case=False, na=False) |
                filtered_df["Họ Tên SV"].str.contains(keyword, case=False, na=False)
            ]

        # ================= TABLE =================
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        # ================= METRICS =================
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Tổng hóa đơn", len(filtered_df))

        with col2:
            da_tt = len(filtered_df[filtered_df["Trạng Thái"] == "Đã thanh toán"])
            st.metric("Đã thanh toán", da_tt)

        with col3:
            chua_tt = len(filtered_df[filtered_df["Trạng Thái"] == "Chưa thanh toán"])
            st.metric("Chưa thanh toán", chua_tt)

        with col4:
            tong_tien = filtered_df["Tổng Tiền"].sum()
            st.metric("Tổng tiền vé xe", f"{tong_tien:,.0f} VNĐ")

        # ================= HÓA ĐƠN QUÁ HẠN =================
        today = date.today()

        overdue_df = filtered_df[
            (filtered_df["Trạng Thái"] == "Chưa thanh toán") 
        ]


if __name__ == "__main__":
    show_hoa_don_dich_vu()
