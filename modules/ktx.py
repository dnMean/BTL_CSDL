import streamlit as st
import pandas as pd
from db_config import call_procedure

def show_ktx():
    st.header("🏢 QUẢN LÝ KÝ TÚC XÁ")

    tab1, tab2 = st.tabs([
        "📋 Danh sách KTX",
        "➕ Thêm / ✏️ Sửa KTX"
    ])

    # ======================================================
    # TAB 1 – DANH SÁCH
    # ======================================================
    with tab1:
        st.subheader("📋 Danh sách KTX")

        if st.button("🔄 Tải lại"):
            st.rerun()

        success, msg, data = call_procedure("sp_ds_ktx")

        if success and data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            col1, col2 = st.columns(2)
            col1.metric("Tổng KTX", len(df))
            col2.metric("Tổng số phòng", df["SoPhong"].sum())

            st.divider()
            st.subheader("🗑️ Xóa KTX")

            ktx_map = {
                f"{row['Ten']} - {row['DiaChi']} (ID: {row['MaKTX']})": row["MaKTX"]
                for _, row in df.iterrows()
            }

            selected = st.selectbox("Chọn KTX để xóa", ktx_map.keys())

            if st.button("🗑️ Xóa KTX", type="primary"):
                ma_ktx = ktx_map[selected]
                success, msg, _ = call_procedure("sp_xoa_ktx", [ma_ktx])

                if success:
                    st.success("✅ Xóa KTX thành công")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")
        else:
            st.warning("Chưa có dữ liệu KTX")

    # ======================================================
    # TAB 2 – THÊM / SỬA
    # ======================================================
    with tab2:
        st.subheader("➕ Thêm / ✏️ Sửa KTX")

        success, _, data = call_procedure("sp_ds_ktx")
        df = pd.DataFrame(data) if data else pd.DataFrame()

        mode = st.radio("Chế độ", ["➕ Thêm mới", "✏️ Sửa"], horizontal=True)

        with st.form("form_ktx", clear_on_submit=(mode == "➕ Thêm mới")):

            if mode == "✏️ Sửa" and not df.empty:
                ktx_map = {
                    f"{row['Ten']} - {row['DiaChi']} (ID: {row['MaKTX']})": row
                    for _, row in df.iterrows()
                }
                selected = st.selectbox("Chọn KTX", ktx_map.keys())
                ktx = ktx_map[selected]
            else:
                ktx = {}

            ten = st.text_input("Tên KTX *", value=ktx.get("Ten", ""))
            dia_chi = st.text_input("Địa chỉ *", value=ktx.get("DiaChi", ""))
            so_tang = st.number_input("Số tầng *", min_value=1, value=ktx.get("SoTang", 1))
            so_phong = st.number_input("Số phòng *", min_value=1, value=ktx.get("SoPhong", 1))

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
                        [ktx["MaKTX"], ten, dia_chi, so_tang, so_phong]
                    )

                if success:
                    st.success("✅ Lưu thành công")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

if __name__ == "__main__":
    show_ktx()
