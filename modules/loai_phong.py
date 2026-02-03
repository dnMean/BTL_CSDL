import streamlit as st
import pandas as pd
from db_config import call_procedure, execute_query

def show_loai_phong():

    if "page" not in st.session_state:
        st.session_state.page = "list"

    # ======================
    # LẤY DỮ LIỆU CHUNG
    # ======================
    data = execute_query("CALL sp_ds_loai_phong()")
    df = pd.DataFrame(data)

    # ======================================================
    # PAGE: DANH SÁCH
    # ======================================================
    if st.session_state.page == "list":
        col1, col2 = st.columns([7, 3])

        with col1:
            st.subheader("📋 Danh sách loại phòng")

        with col2:
            c1, c2, c3 = st.columns(3)
            if c1.button("➕"):
                st.session_state.page = "add"
                st.rerun()
            if c2.button("✏️"):
                st.session_state.page = "edit"
                st.rerun()
            if c3.button("🗑️"):
                st.session_state.page = "delete"
                st.rerun()

        if df.empty:
            st.info("Chưa có loại phòng")
        else:
            st.dataframe(df, use_container_width=True)

    # ======================================================
    # PAGE: THÊM
    # ======================================================
    elif st.session_state.page == "add":
        st.subheader("➕ Thêm loại phòng")

        with st.form("form_add"):
            ten = st.text_input("Tên loại phòng")
            mota = st.text_area("Mô tả")
            dientich = st.number_input("Diện tích (m²)", min_value=0.0)
            songuoi = st.number_input("Số người tối đa", min_value=1)

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Lưu"):
                    call_procedure(
                        "sp_them_loai_phong",
                        (ten, mota, dientich, songuoi)
                    )
                    st.success("✅ Thêm thành công")
                    st.session_state.page = "list"
                    st.rerun()

            with col2:
                if st.form_submit_button("⬅️ Huỷ"):
                    st.session_state.page = "list"
                    st.rerun()

    # ======================================================
    # PAGE: SỬA
    # ======================================================
    elif st.session_state.page == "edit":
        st.subheader("✏️ Sửa loại phòng")

        if df.empty:
            st.warning("Không có dữ liệu")
            return

        ma_loai = st.selectbox(
            "Chọn loại phòng",
            df["MaLoai"],
            format_func=lambda x: df[df["MaLoai"] == x]["TenLoai"].values[0]
        )

        row = df[df["MaLoai"] == ma_loai].iloc[0]

        with st.form("form_edit"):
            ten = st.text_input("Tên loại", row["TenLoai"])
            mota = st.text_area("Mô tả", row["MoTa"])
            dientich = st.number_input("Diện tích", value=float(row["DienTich"]))
            songuoi = st.number_input("Số người tối đa", value=int(row["SoNguoiToiDa"]))

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Cập nhật"):
                    call_procedure(
                        "sp_sua_loai_phong",
                        (ma_loai, ten, mota, dientich, songuoi)
                    )
                    st.success("✅ Cập nhật thành công")
                    st.session_state.page = "list"
                    st.rerun()

            with col2:
                if st.form_submit_button("⬅️ Huỷ"):
                    st.session_state.page = "list"
                    st.rerun()

    # ======================================================
    # PAGE: XOÁ
    # ======================================================
    elif st.session_state.page == "delete":
        st.subheader("🗑️ Xoá loại phòng")

        if df.empty:
            st.warning("Không có dữ liệu")
            return

        ma_loai = st.selectbox(
            "Chọn loại phòng cần xoá",
            df["MaLoai"],
            format_func=lambda x: df[df["MaLoai"] == x]["TenLoai"].values[0]
        )

        st.warning("⚠️ Thao tác không thể hoàn tác")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("❌ Xoá"):
                call_procedure("sp_xoa_loai_phong", (ma_loai,))
                st.success("🗑️ Đã xoá")
                st.session_state.page = "list"
                st.rerun()

        with col2:
            if st.button("⬅️ Huỷ"):
                st.session_state.page = "list"
                st.rerun()

if __name__ == "__main__":
    show_loai_phong()