import streamlit as st
import pandas as pd
from db_config import call_procedure


def show_ktx():
    st.header("🏢 QUẢN LÝ KÝ TÚC XÁ")

    tab1, tab2, tab3 = st.tabs([
        "📋 Danh sách KTX",
        "➕ Thêm / ✏️ Sửa KTX",
        "🗑️ Xoá KTX"
    ])

    # ======================================================
    # TAB 1 – DANH SÁCH
    # ======================================================
    with tab1:
        st.subheader("📋 Danh sách KTX")

        if st.button("🔄 Tải lại"):
            st.rerun()

        success, msg, data = call_procedure("sp_ds_ktx")

        if not success:
            st.error(msg)
            return

        if not data:
            st.warning("⚠️ Chưa có dữ liệu KTX")
            return

        df = pd.DataFrame(data)

        st.dataframe(df, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        col1.metric("🏢 Tổng KTX", len(df))
        col2.metric("🚪 Tổng số phòng", df["SoPhong"].sum())

    # ======================================================
    # TAB 2 – THÊM / SỬA
    # ======================================================
    with tab2:
        st.subheader("➕ Thêm / ✏️ Sửa KTX")

        success, _, data = call_procedure("sp_ds_ktx")
        df = pd.DataFrame(data) if data else pd.DataFrame()

        mode = st.radio(
            "Chế độ",
            ["➕ Thêm mới", "✏️ Sửa"],
            horizontal=True
        )

        with st.form("form_ktx", clear_on_submit=(mode == "➕ Thêm mới")):

            if mode == "✏️ Sửa" and not df.empty:
                ktx_map = {
                    f"{row['Ten']} - {row['DiaChi']} (ID: {row['MaKTX']})": row
                    for _, row in df.iterrows()
                }
                selected = st.selectbox("Chọn KTX", list(ktx_map.keys()))
                ktx = ktx_map[selected]
            else:
                ktx = {}

            ten = st.text_input("Tên KTX *", value=ktx.get("Ten", ""))
            dia_chi = st.text_input("Địa chỉ *", value=ktx.get("DiaChi", ""))
            so_tang = st.number_input("Số tầng *", min_value=1, value=int(ktx.get("SoTang", 1)))
            so_phong = st.number_input("Số phòng *", min_value=1, value=int(ktx.get("SoPhong", 1)))

            submit = st.form_submit_button("💾 Lưu", use_container_width=True)

            if submit:
                if not ten or not dia_chi:
                    st.error("❌ Vui lòng nhập đầy đủ thông tin")
                    return

                if mode == "➕ Thêm mới":
                    success, msg, _ = call_procedure(
                        "sp_them_ktx",
                        [ten, dia_chi, so_tang, so_phong]
                    )
                else:
                    success, msg, _ = call_procedure(
                        "sp_sua_ktx",
                        [int(ktx["MaKTX"]), ten, dia_chi, so_tang, so_phong]
                    )

                if success:
                    st.success("✅ Lưu thành công")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

    # ======================================================
    # TAB 3 – XOÁ KTX (GIAO DIỆN RIÊNG)
    # ======================================================
    with tab3:
        st.subheader("🗑️ Xoá KTX")

        success, _, data = call_procedure("sp_ds_ktx")
        df = pd.DataFrame(data) if data else pd.DataFrame()

        if df.empty:
            st.warning("⚠️ Không có KTX để xoá")
            return

        with st.form("form_xoa_ktx"):

            ktx_map = {
                f"{row['Ten']} - {row['DiaChi']} (ID: {row['MaKTX']})": row
                for _, row in df.iterrows()
            }

            selected = st.selectbox("Chọn KTX cần xoá *", list(ktx_map.keys()))
            ktx = ktx_map[selected]

            st.markdown("### 📌 Thông tin KTX")
            st.write(f"- 🏢 **Tên:** {ktx['Ten']}")
            st.write(f"- 📍 **Địa chỉ:** {ktx['DiaChi']}")
            st.write(f"- 🏬 **Số tầng:** {ktx['SoTang']}")
            st.write(f"- 🚪 **Số phòng:** {ktx['SoPhong']}")

            if ktx["SoPhong"] > 0:
                st.warning("⚠️ KTX đã có phòng → không thể xoá")
                can_delete = False
            else:
                st.info("✅ KTX chưa có phòng → có thể xoá")
                can_delete = True

            confirm = st.checkbox("⚠️ Tôi xác nhận muốn xoá KTX này")

            submit = st.form_submit_button(
                "🗑️ Xoá KTX",
                disabled=not can_delete or not confirm
            )

            if submit:
                success, msg, _ = call_procedure(
                    "sp_xoa_ktx",
                    [int(ktx["MaKTX"])]
                )

                if success:
                    st.success("✅ Xoá KTX thành công")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")


if __name__ == "__main__":
    show_ktx()
