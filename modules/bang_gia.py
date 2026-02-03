import streamlit as st
import pandas as pd
from db_config import call_procedure


# =========================
# PROCEDURE HELPERS
# =========================

def get_all_bang_gia():
    success, msg, data = call_procedure("sp_get_all_bang_gia")
    if success and data:
        return pd.DataFrame(data)
    return None


def get_all_loai_phong():
    success, msg, data = call_procedure("sp_ds_loai_phong")
    if success and data:
        return pd.DataFrame(data)
    return None


# =========================
# UI: THÊM BẢNG GIÁ
# =========================

def ui_them_bang_gia():
    st.subheader("➕ Thêm bảng giá")

    df_lp = get_all_loai_phong()
    if df_lp is None or df_lp.empty:
        st.warning("⚠️ Chưa có loại phòng")
        if st.button("⬅️ Quay lại", key="btn_back_no_lp"):
            st.session_state.bg_action = None
            st.rerun()
        return

    ma_loai = st.selectbox(
        "Loại phòng",
        df_lp["MaLoai"],
        format_func=lambda x: df_lp[df_lp["MaLoai"] == x]["TenLoai"].values[0],
        key="select_loai_phong_add"
    )

    loai_block = st.selectbox(
        "Loại Block",
        options=["10", "15", "Chẵn tháng"],
        key="input_block_add"
    )
    don_gia = st.number_input("Đơn giá", min_value=0.0, step=100000.0, format="%.0f", key="input_gia_add")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Lưu", key="btn_save_add", type="primary"):
            success, msg, _ = call_procedure(
                "sp_add_bang_gia",
                [ma_loai, loai_block, don_gia]
            )
            if success:
                st.success("✅ Thêm bảng giá thành công")
                st.session_state.bg_action = None
                st.rerun()
            else:
                st.error(msg)

    with col2:
        if st.button("⬅️ Quay lại", key="btn_back_add"):
            st.session_state.bg_action = None
            st.rerun()


# =========================
# UI: SỬA BẢNG GIÁ
# =========================

def ui_sua_bang_gia():
    st.subheader("✏️ Sửa bảng giá")

    df = get_all_bang_gia()
    if df is None or df.empty:
        st.warning("⚠️ Chưa có bảng giá để sửa")
        if st.button("⬅️ Quay lại", key="btn_back_no_bg_edit"):
            st.session_state.bg_action = None
            st.rerun()
        return

    selected = st.selectbox(
        "Chọn bảng giá",
        df.index,
        format_func=lambda i: f"{df.loc[i, 'TenLoai']} | Block {df.loc[i, 'LoaiBlock']}",
        key="select_bang_gia_edit"
    )

    row = df.loc[selected]

    don_gia_moi = st.number_input(
        "Đơn giá mới",
        min_value=0.0,
        value=float(row["DonGia"]),
        step=100000.0,
        format="%.0f",
        key="input_gia_edit"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Cập nhật", key="btn_save_edit", type="primary"):
            success, msg, _ = call_procedure(
                "sp_update_bang_gia",
                [row["MaLoai"], int(row["LoaiBlock"]), don_gia_moi]
            )
            if success:
                st.success("✅ Cập nhật thành công")
                st.session_state.bg_action = None
                st.rerun()
            else:
                st.error(msg)

    with col2:
        if st.button("⬅️ Quay lại", key="btn_back_edit"):
            st.session_state.bg_action = None
            st.rerun()


# =========================
# UI: XOÁ BẢNG GIÁ
# =========================

def ui_xoa_bang_gia():
    st.subheader("🗑️ Xoá bảng giá")

    df = get_all_bang_gia()
    if df is None or df.empty:
        st.warning("⚠️ Chưa có bảng giá để xoá")
        if st.button("⬅️ Quay lại", key="btn_back_no_bg_delete"):
            st.session_state.bg_action = None
            st.rerun()
        return

    selected = st.selectbox(
        "Chọn bảng giá cần xoá",
        df.index,
        format_func=lambda i: f"{df.loc[i, 'TenLoai']} | Block {df.loc[i, 'LoaiBlock']}",
        key="select_bang_gia_delete"
    )

    row = df.loc[selected]

    st.warning(
        f"⚠️ Bạn sắp xoá bảng giá:\n\n"
        f"• Loại phòng: **{row['TenLoai']}**\n"
        f"• Block: **{row['LoaiBlock']}**"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Xác nhận xoá", key="btn_confirm_delete", type="primary"):
            success, msg, _ = call_procedure(
                "sp_delete_bang_gia",
                [row["MaLoai"], int(row["LoaiBlock"])]
            )
            if success:
                st.success("✅ Đã xoá bảng giá")
                st.session_state.bg_action = None
                st.rerun()
            else:
                st.error(msg)

    with col2:
        if st.button("⬅️ Quay lại", key="btn_back_delete"):
            st.session_state.bg_action = None
            st.rerun()


# =========================
# UI: DANH SÁCH
# =========================

def ui_danh_sach():
    col1, col2, col3, col4 = st.columns([4, 1, 1, 1])

    with col1:
        st.subheader("📋 Danh sách bảng giá")

    with col2:
        if st.button("➕ Thêm", key="btn_add_bg"):
            st.session_state.bg_action = "add"
            st.rerun()

    with col3:
        if st.button("✏️ Sửa", key="btn_edit_bg"):
            st.session_state.bg_action = "edit"
            st.rerun()

    with col4:
        if st.button("🗑️ Xoá", key="btn_delete_bg"):
            st.session_state.bg_action = "delete"
            st.rerun()

    df = get_all_bang_gia()

    if df is None or df.empty:
        st.info("Chưa có bảng giá")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


# =========================
# MAIN UI
# =========================

def show_bang_gia():
    st.header("💰 QUẢN LÝ BẢNG GIÁ")

    if "bg_action" not in st.session_state:
        st.session_state.bg_action = None

    # Hiển thị theo action
    if st.session_state.bg_action == "add":
        ui_them_bang_gia()

    elif st.session_state.bg_action == "edit":
        ui_sua_bang_gia()

    elif st.session_state.bg_action == "delete":
        ui_xoa_bang_gia()

    else:
        ui_danh_sach()


if __name__ == "__main__":
    show_bang_gia()