import streamlit as st
import pandas as pd
from db_config import call_procedure, execute_query
from datetime import datetime

def show_ve_thang():
    st.header("🎫 QUẢN LÝ VÉ THÁNG")

    tab1, tab2 = st.tabs([
        "📋 Danh sách vé tháng",
        "➕ Đăng ký vé tháng"
    ])

    # ======================================================
    # TAB 1 – DANH SÁCH VÉ THÁNG
    # ======================================================
    with tab1:
        st.subheader("📋 Danh sách Vé Tháng")

        if st.button("🔄 Tải lại", key="reload_ve_thang"):
            st.rerun()

        success, message, data = call_procedure("sp_danh_sach_ve_thang")

        if success and data:
            df = pd.DataFrame(data)
            df.columns = [
                'Mã Vé',
                'Tháng',
                'Năm',
                'Biển Số',
                'MSV',
                'Họ Tên SV',
                'Giá Vé',
                'Trạng Thái'
            ]

            # ===== Filter =====
            col1, col2 = st.columns(2)
            with col1:
                filter_thang = st.selectbox(
                    "Lọc theo tháng",
                    ["Tất cả"] + sorted(df['Tháng'].unique().tolist())
                )
            with col2:
                filter_nam = st.selectbox(
                    "Lọc theo năm",
                    ["Tất cả"] + sorted(df['Năm'].unique(), reverse=True)
                )

            filtered_df = df.copy()
            if filter_thang != "Tất cả":
                filtered_df = filtered_df[filtered_df['Tháng'] == filter_thang]
            if filter_nam != "Tất cả":
                filtered_df = filtered_df[filtered_df['Năm'] == filter_nam]

            st.dataframe(filtered_df, use_container_width=True, hide_index=True)

            # ===== Thống kê =====
            col1, col2, col3 = st.columns(3)
            col1.metric("Tổng vé", len(filtered_df))
            col2.metric(
                "Đã thanh toán",
                len(filtered_df[filtered_df['Trạng Thái'] == 'Đã thanh toán'])
            )
            col3.metric(
                "Tổng tiền",
                f"{filtered_df['Giá Vé'].sum():,.0f}đ"
            )
        else:
            st.warning("Chưa có vé tháng nào")


    # ======================================================
    # TAB 2 – ĐĂNG KÝ VÉ THÁNG
    # ======================================================
    with tab2:
        st.subheader("➕ Đăng ký vé tháng")

        # Lấy sinh viên
        data_sv = execute_query("SELECT MSV, HoTen FROM SINH_VIEN")

        if not data_sv:
            st.error("Chưa có sinh viên trong hệ thống")
            return

        with st.form("form_dang_ky_ve_thang", clear_on_submit=True):
            sv_map = {
                f"{sv['MSV']} - {sv['HoTen']}": sv['MSV']
                for sv in data_sv
            }

            selected_sv = st.selectbox("Sinh viên *", sv_map.keys())
            bien_so = st.text_input("Biển số xe *", placeholder="59X1-12345")

            now = datetime.now()
            thang = st.selectbox(
                "Tháng *",
                list(range(1, 13)),
                index=now.month - 1
            )
            nam = st.selectbox(
                "Năm *",
                [now.year - 1, now.year, now.year + 1],
                index=1
            )

            st.info("""
            ℹ️ **Quy định**
            - Mỗi sinh viên tối đa **2 vé tháng / tháng**
            - **1 xe chỉ được đăng ký 1 vé tháng**
            - Giá vé cố định **100.000đ / tháng**
            """)

            submitted = st.form_submit_button(
                "➕ Đăng ký vé tháng",
                type="primary",
                use_container_width=True
            )

            if submitted:
                if not bien_so:
                    st.error("❌ Vui lòng nhập biển số xe")
                    return

                msv = sv_map[selected_sv]

                success, message, result = call_procedure(
                    "sp_dang_ky_ve_thang",
                    [msv, bien_so, thang, nam]
                )

                if success:
                    st.success("✅ Đăng ký vé tháng thành công")
                    if result:
                        st.info(f"💰 Giá vé: {result[0]['GiaVe']:,.0f}đ")
                    st.balloons()
                else:
                    st.error(f"❌ {message}")

if __name__ == "__main__":
    show_ve_thang()
