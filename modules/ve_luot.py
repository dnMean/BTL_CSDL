import streamlit as st
import pandas as pd
from db_config import call_procedure, execute_query
from datetime import datetime

def show_ve_luot():
    st.header("🎟️ QUẢN LÝ VÉ XE")

    tab1, tab2, tab3 = st.tabs([
        "📋 Danh sách vé",
        "➕ Xe vào",
        "🚗 Xe ra"
    ])

    # ======================================================
    # TAB 1 – DANH SÁCH VÉ
    # ======================================================
    with tab1:
        st.subheader("📋 Danh sách vé xe")

        if st.button("🔄 Tải lại"):
            st.rerun()

        success, msg, data = call_procedure("sp_danh_sach_ve_xe")

        if success and data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            col1, col2, col3 = st.columns(3)
            col1.metric("Tổng vé", len(df))
            col2.metric("Đang gửi", len(df[df['Trạng Thái'] == 'Đang gửi']))
            col3.metric("Tổng tiền", f"{df['Giá Vé'].sum():,.0f}đ")
        else:
            st.warning("Chưa có dữ liệu vé")

    # ======================================================
    # TAB 2 – XE VÀO
    # ======================================================
    with tab2:
        st.subheader("🚗 Xe vào – Tạo vé lượt")

        now = datetime.now()
        st.info(f"⏰ {now.strftime('%d/%m/%Y %H:%M:%S')}")

        # Lấy danh sách sinh viên (query đơn giản, OK)
        data_sv = execute_query("SELECT MSV, HoTen FROM SINH_VIEN")

        if not data_sv:
            st.error("Chưa có sinh viên")
            return

        with st.form("form_xe_vao", clear_on_submit=True):
            sv_map = {
                f"{sv['MSV']} - {sv['HoTen']}": sv['MSV']
                for sv in data_sv
            }

            sv_select = st.selectbox("Sinh viên", sv_map.keys())
            bien_so = st.text_input("Biển số xe", placeholder="59X1-12345")

            submit = st.form_submit_button(
                "🚗 Ghi nhận xe vào",
                type="primary",
                use_container_width=True
            )

            if submit:
                if not bien_so:
                    st.error("❌ Chưa nhập biển số")
                    return

                msv = sv_map[sv_select]

                success, msg, result = call_procedure(
                    "sp_tao_ve_luot",
                    [msv, bien_so]
                )

                if success:
                    st.success("✅ Tạo vé thành công")
                    if result:
                        st.json(result[0])
                    st.balloons()
                else:
                    st.error(msg)

    # ======================================================
    # TAB 3 – XE RA
    # ======================================================
    # ======================================================
    with tab3:
        st.subheader("🚗 Xe ra")

        # 👉 Gọi procedure
        success, msg, data_gui = call_procedure("sp_ds_xe_dang_gui")

        if not success or not data_gui:
            st.warning("🅿️ Không có xe đang gửi")
            return

        df = pd.DataFrame(data_gui)
        st.dataframe(df, use_container_width=True, hide_index=True)

        options = {
            f"{v['BienSoXe']} - {v['HoTen']} ({v['ThoiGianVao']})": v['MaVe']
            for v in data_gui
        }

        selected = st.selectbox("Chọn xe ra", options.keys())

        # Checkbox thanh toán
        da_thanh_toan = st.checkbox("💳 Đã thanh toán")

        if st.button("🚗 Ghi nhận xe ra", type="primary", use_container_width=True):
            ma_ve = options[selected]

            success, msg, result = call_procedure(
                "sp_update_ve_luot",
                [ma_ve, int(da_thanh_toan)]
            )

            if success:
                st.success("✅ Xe đã ra")

                if result:
                    st.info(
                        f"💰 Giá vé: {result[0]['GiaVe']:,.0f}đ | "
                        f"Thanh toán: {'Đã thanh toán' if da_thanh_toan else 'Chưa thanh toán'}"
                    )

                st.balloons()
                st.rerun()
            else:
                st.error(msg)




if __name__ == "__main__":
    show_ve_luot()
