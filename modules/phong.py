import streamlit as st
import pandas as pd
from db_config import call_procedure


# =========================
# PROCEDURE HELPERS
# =========================

def get_all_phong():
    success, msg, data = call_procedure("sp_ds_phong")
    if success and data:
        return pd.DataFrame(data)
    return None


def get_all_loai_phong():
    success, msg, data = call_procedure("sp_ds_loai_phong")
    if success and data:
        return pd.DataFrame(data)
    return None


def get_all_ktx():
    success, msg, data = call_procedure("sp_ds_ktx")
    if success and data:
        return pd.DataFrame(data)
    return None


# =========================
# UI: THÊM PHÒNG
# =========================

def ui_them_phong():
    st.subheader("➕ Thêm phòng")

    df_lp = get_all_loai_phong()
    df_ktx = get_all_ktx()

    if df_lp is None or df_lp.empty:
        st.warning("⚠️ Chưa có loại phòng")
        if st.button("⬅️ Quay lại", key="btn_back_no_lp"):
            st.session_state.phong_action = None
            st.rerun()
        return

    if df_ktx is None or df_ktx.empty:
        st.warning("⚠️ Chưa có ký túc xá")
        if st.button("⬅️ Quay lại", key="btn_back_no_ktx"):
            st.session_state.phong_action = None
            st.rerun()
        return

    ma_phong = st.text_input("Mã phòng", key="input_ma_phong_add")
    tang = st.number_input("Tầng", min_value=1, step=1, key="input_tang_add")

    ma_loai = st.selectbox(
        "Loại phòng",
        df_lp["MaLoai"],
        format_func=lambda x: df_lp[df_lp["MaLoai"] == x]["TenLoai"].values[0],
        key="select_loai_phong_add"
    )

    ma_ktx = st.selectbox(
        "Ký túc xá",
        df_ktx["MaKTX"],
        format_func=lambda x: df_ktx[df_ktx["MaKTX"] == x]["Ten"].values[0],
        key="select_ktx_add"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Lưu", key="btn_save_add", type="primary"):
            if not ma_phong:
                st.error("Vui lòng nhập mã phòng")
            else:
                success, msg, _ = call_procedure(
                    "sp_them_phong",
                    [ma_phong, tang, ma_loai, ma_ktx]
                )
                if success:
                    st.success("✅ Thêm phòng thành công")
                    st.session_state.phong_action = None
                    st.rerun()
                else:
                    st.error(msg)

    with col2:
        if st.button("⬅️ Quay lại", key="btn_back_add"):
            st.session_state.phong_action = None
            st.rerun()


# =========================
# UI: SỬA PHÒNG
# =========================

def ui_sua_phong():
    st.subheader("✏️ Sửa phòng")

    df = get_all_phong()
    if df is None or df.empty:
        st.warning("⚠️ Chưa có phòng để sửa")
        if st.button("⬅️ Quay lại", key="btn_back_no_phong_edit"):
            st.session_state.phong_action = None
            st.rerun()
        return

    df_lp = get_all_loai_phong()
    df_ktx = get_all_ktx()

    selected = st.selectbox(
        "Chọn phòng",
        df.index,
        format_func=lambda i: f"{df.loc[i, 'MaPhong']} - {df.loc[i, 'TenKTX']}",
        key="select_phong_edit"
    )

    row = df.loc[selected]

    # Lấy MaKTX từ tên KTX
    ma_ktx = df_ktx[df_ktx["Ten"] == row["TenKTX"]]["MaKTX"].values[0]

    tang = st.number_input(
        "Tầng",
        min_value=1,
        value=int(row["Tang"]),
        step=1,
        key="input_tang_edit"
    )

    so_nguoi = st.number_input(
        "Số người hiện tại",
        min_value=0,
        value=int(row["SoNguoiHienTai"]),
        step=1,
        key="input_so_nguoi_edit"
    )

    # Tìm index của loại phòng hiện tại
    current_lp_idx = df_lp[df_lp["TenLoai"] == row["TenLoai"]].index[0] if not df_lp[df_lp["TenLoai"] == row["TenLoai"]].empty else 0

    ma_loai = st.selectbox(
        "Loại phòng",
        df_lp["MaLoai"],
        index=int(current_lp_idx),
        format_func=lambda x: df_lp[df_lp["MaLoai"] == x]["TenLoai"].values[0],
        key="select_loai_phong_edit"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Cập nhật", key="btn_save_edit", type="primary"):
            success, msg, _ = call_procedure(
                "sp_sua_phong",
                [row["MaPhong"], ma_ktx, tang, so_nguoi, ma_loai]
            )
            if success:
                st.success("✅ Cập nhật thành công")
                st.session_state.phong_action = None
                st.rerun()
            else:
                st.error(msg)

    with col2:
        if st.button("⬅️ Quay lại", key="btn_back_edit"):
            st.session_state.phong_action = None
            st.rerun()


# =========================
# UI: XOÁ PHÒNG
# =========================

def ui_xoa_phong():
    st.subheader("🗑️ Xoá phòng")

    df = get_all_phong()
    df_ktx = get_all_ktx()

    if df is None or df.empty:
        st.warning("⚠️ Chưa có phòng để xoá")
        if st.button("⬅️ Quay lại", key="btn_back_no_phong_delete"):
            st.session_state.phong_action = None
            st.rerun()
        return

    selected = st.selectbox(
        "Chọn phòng cần xoá",
        df.index,
        format_func=lambda i: f"{df.loc[i, 'MaPhong']} - {df.loc[i, 'TenKTX']}",
        key="select_phong_delete"
    )

    row = df.loc[selected]

    # Lấy MaKTX từ tên KTX
    ma_ktx = df_ktx[df_ktx["Ten"] == row["TenKTX"]]["MaKTX"].values[0]

    st.warning(
        f"⚠️ Bạn sắp xoá phòng:\n\n"
        f"• Mã phòng: **{row['MaPhong']}**\n"
        f"• Tầng: **{row['Tang']}**\n"
        f"• Loại phòng: **{row['TenLoai']}**\n"
        f"• Ký túc xá: **{row['TenKTX']}**"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Xác nhận xoá", key="btn_confirm_delete", type="primary"):
            success, msg, _ = call_procedure(
                "sp_xoa_phong",
                [row["MaPhong"], ma_ktx]
            )
            if success:
                st.success("✅ Đã xoá phòng")
                st.session_state.phong_action = None
                st.rerun()
            else:
                st.error(msg)

    with col2:
        if st.button("⬅️ Quay lại", key="btn_back_delete"):
            st.session_state.phong_action = None
            st.rerun()


# =========================
# UI: DANH SÁCH
# =========================

def ui_danh_sach():
    col1, col2, col3, col4 = st.columns([4, 1, 1, 1])

    with col1:
        st.subheader("📋 Danh sách phòng")

    with col2:
        if st.button("➕ Thêm", key="btn_add_phong"):
            st.session_state.phong_action = "add"
            st.rerun()

    with col3:
        if st.button("✏️ Sửa", key="btn_edit_phong"):
            st.session_state.phong_action = "edit"
            st.rerun()

    with col4:
        if st.button("🗑️ Xoá", key="btn_delete_phong"):
            st.session_state.phong_action = "delete"
            st.rerun()

    df = get_all_phong()

    if df is None or df.empty:
        st.info("Chưa có phòng")
    else:
        # Đổi tên cột hiển thị
        df_display = df.rename(columns={
            "MaPhong": "Mã phòng",
            "Tang": "Tầng",
            "SoNguoiHienTai": "Số người hiện tại",
            "TenLoai": "Loại phòng",
            "SoNguoiToiDa": "Số người tối đa",
            "TenKTX": "Ký túc xá"
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True)


# =========================
# MAIN UI
# =========================

def show_phong():
    st.header("🏠 QUẢN LÝ PHÒNG")

    if "phong_action" not in st.session_state:
        st.session_state.phong_action = None

    # Hiển thị theo action
    if st.session_state.phong_action == "add":
        ui_them_phong()

    elif st.session_state.phong_action == "edit":
        ui_sua_phong()

    elif st.session_state.phong_action == "delete":
        ui_xoa_phong()

    else:
        ui_danh_sach()


if __name__ == "__main__":
    show_phong()