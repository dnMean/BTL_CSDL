import streamlit as st
import pandas as pd
from db_config import call_procedure

def show_dich_vu():
    st.header("🧾 Quản lý Dịch Vụ")
    
    # ===== TOAST =====
    if "dv_toast" in st.session_state and st.session_state.dv_toast:
        st.toast(st.session_state.dv_toast, icon="✅")
        st.session_state.dv_toast = None
    
    tab1, tab2, tab3 = st.tabs(["📋 Danh sách", "➕ Thêm mới", "✏️ Sửa / 🗑️ Xóa"])
    
    # ================= TAB 1: DANH SÁCH =================
    with tab1:
        st.subheader("Danh sách dịch vụ")
        success, _, data = call_procedure("sp_ds_dichvu")
        
        if success and data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            col1.metric("Tổng dịch vụ", len(df))
            col2.metric("Giá TB", f"{df['DonGia'].mean():,.0f} đ")
        else:
            st.info("Chưa có dịch vụ nào")
    
    # ================= TAB 2: THÊM =================
    with tab2:
        st.subheader("➕ Thêm dịch vụ mới")
        
        ten_dv = st.text_input("Tên dịch vụ", key="add_ten_dv")
        don_gia = st.number_input(
            "Đơn giá (VNĐ)",
            min_value=0.0,  # ✅ Đổi từ 0 thành 0.0
            step=1000.0,
            key="add_don_gia"
        )
        don_vi = st.text_input("Đơn vị", key="add_don_vi")
        mo_ta = st.text_area("Mô tả", key="add_mo_ta")
        
        if st.button("➕ Thêm dịch vụ", type="primary", use_container_width=True):
            if not ten_dv or not don_vi:
                st.warning("⚠️ Vui lòng nhập đầy đủ thông tin bắt buộc")
                return
            
            success, message, _ = call_procedure(
                "sp_them_dich_vu",
                [ten_dv, don_gia, don_vi, mo_ta]
            )
            
            if success:
                st.session_state.dv_toast = "Thêm dịch vụ thành công!"
                st.rerun()
            else:
                st.error(f"❌ {message}")
    
    # ================= TAB 3: SỬA / XOÁ =================
    with tab3:
        st.subheader("✏️ Sửa / 🗑️ Xóa dịch vụ")
        
        success, _, data = call_procedure("sp_ds_dichvu")
        if not (success and data):
            st.info("Chưa có dịch vụ để chỉnh sửa")
            return
        
        # map MADV -> record
        dv_dict = {dv["MADV"]: dv for dv in data}
        dv_options = [
            f"{dv['TenDV']} ({dv['DonVi']})" for dv in data
        ]
        
        selected = st.selectbox("Chọn dịch vụ", dv_options)
        madv_selected = list(dv_dict.keys())[dv_options.index(selected)]
        dv = dv_dict[madv_selected]
        
        col1, col2 = st.columns(2)
        
        with col1:
            ten_dv = st.text_input(
                "Tên dịch vụ *",
                value=dv["TenDV"],
                key=f"edit_ten_{madv_selected}"
            )
            don_gia = st.number_input(
                "Đơn giá (VNĐ) *",
                min_value=0.0,  # ✅ Đổi từ 0 thành 0.0
                step=1000.0,
                value=float(dv["DonGia"]),
                key=f"edit_gia_{madv_selected}"
            )
        
        with col2:
            don_vi = st.text_input(
                "Đơn vị *",
                value=dv["DonVi"],
                key=f"edit_donvi_{madv_selected}"
            )
            mo_ta = st.text_area(
                "Mô tả",
                value=dv["MoTa"] or "",
                key=f"edit_mota_{madv_selected}"
            )
        
        col_btn1, col_btn2 = st.columns(2)
        
        # ===== CẬP NHẬT =====
        with col_btn1:
            if st.button("💾 Cập nhật", type="primary", use_container_width=True):
                success, message, _ = call_procedure(
                    "sp_sua_dich_vu",
                    [madv_selected, ten_dv, don_gia, don_vi, mo_ta]
                )
                
                if success:
                    st.session_state.dv_toast = "Cập nhật dịch vụ thành công!"
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
        
        # ===== XOÁ =====
        with col_btn2:
            confirm = st.checkbox(
                "Xác nhận xoá dịch vụ",
                key=f"confirm_xoa_{madv_selected}"
            )
            
            if st.button("🗑️ Xoá dịch vụ", use_container_width=True):
                if not confirm:
                    st.warning("⚠️ Vui lòng xác nhận xoá")
                    return
                
                success, message, _ = call_procedure(
                    "sp_xoa_dich_vu",
                    [madv_selected]
                )
                
                if success:
                    st.session_state.dv_toast = "Xoá dịch vụ thành công!"
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

if __name__ == "__main__":
    show_dich_vu()