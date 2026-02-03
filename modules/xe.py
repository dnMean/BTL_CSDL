import streamlit as st
import pandas as pd
from db_config import call_procedure, execute_query

def show_xe():
    st.header("🏍️ Quản lý Xe")
    
    # Tabs cho các chức năng
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Danh sách", "➕ Thêm mới", "✏️ Sửa", "🗑️ Xóa"])
    
    # ===================== TAB DANH SÁCH =====================
    with tab1:
        st.subheader("Danh sách Xe đã đăng ký")
        if st.button("🔄 Tải lại dữ liệu", key="reload_xe"):
            st.rerun()
        
        success, message, data = call_procedure("sp_xe_xem_all")
        
        if success and data:
            df = pd.DataFrame(data)
            df.columns = ['Biển số', 'Màu xe', 'Hiệu xe']
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.info(f"Tổng số xe: {len(df)}")
        elif success and not data:
            st.warning("Chưa có xe nào được đăng ký trong hệ thống")
        else:
            st.error(message)
    
    # ===================== TAB THÊM MỚI =====================
    with tab2:
        st.subheader("Thêm Xe Mới")
        
        with st.form("form_them_xe", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                bien_so = st.text_input("Biển số xe *", placeholder="VD: 29A-12345")
            with col2:
                mau_xe = st.text_input("Màu xe *", placeholder="VD: Đỏ")
            with col3:
                hieu_xe = st.text_input("Hiệu xe *", placeholder="VD: Honda")
            
            submitted = st.form_submit_button("➕ Thêm xe", use_container_width=True)
            
            if submitted:
                if not all([bien_so, mau_xe, hieu_xe]):
                    st.error("Vui lòng điền đầy đủ thông tin bắt buộc (*)")
                else:
                    success, message, _ = call_procedure(
                        "sp_them_xe",
                        [bien_so, mau_xe, hieu_xe]
                    )
                    if success:
                        st.success(f"✅ Thêm xe thành công!")
                    else:
                        st.error(f"❌ {message}")
    
    # ===================== TAB SỬA =====================
    with tab3:
        st.subheader("Sửa Thông Tin Xe")
        
        success, _, data = call_procedure("sp_xe_xem_all")
        
        if success and data:
            xe_dict = {xe['BienSo']: xe for xe in data}
            xe_options = [f"{xe['BienSo']} - {xe['HieuXe']} ({xe['MauXe']})" for xe in data]
            
            selected = st.selectbox("Chọn xe cần sửa", xe_options, key="select_sua_xe")
            
            if selected:
                bien_so_selected = selected.split(" - ")[0]
                xe_info = xe_dict[bien_so_selected]
                
                with st.form("form_sua_xe"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.text_input("Biển số xe", value=bien_so_selected, disabled=True)
                    with col2:
                        mau_xe = st.text_input("Màu xe *", value=xe_info['MauXe'])
                    with col3:
                        hieu_xe = st.text_input("Hiệu xe *", value=xe_info['HieuXe'])
                    
                    submitted = st.form_submit_button("💾 Cập nhật", use_container_width=True)
                    
                    if submitted:
                        success, message, _ = call_procedure(
                            "sp_sua_xe",
                            [bien_so_selected, mau_xe, hieu_xe]
                        )
                        if success:
                            st.success(f"✅ Cập nhật xe thành công!")
                        else:
                            st.error(f"❌ {message}")
        else:
            st.warning("Chưa có xe nào để sửa")
    
    # ===================== TAB XÓA =====================
    with tab4:
        st.subheader("Xóa Xe")
        
        success, _, data = call_procedure("sp_xe_xem_all")
        
        if success and data:
            xe_options = [f"{xe['BienSo']} - {xe['HieuXe']} ({xe['MauXe']})" for xe in data]
            selected = st.selectbox("Chọn xe cần xóa", xe_options, key="select_xoa_xe")
            
            if selected:
                bien_so_selected = selected.split(" - ")[0]
                
                st.warning(f"⚠️ Bạn có chắc chắn muốn xóa xe **{selected}**?")
                st.caption("Lưu ý: Không thể xóa xe nếu xe đã có vé tháng đăng ký")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Xác nhận xóa", type="primary", use_container_width=True):
                        success, message, _ = call_procedure("sp_xe_xoa", [bien_so_selected])
                        if success:
                            st.success(f"✅ Xóa xe thành công!")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
        else:
            st.warning("Chưa có xe nào để xóa")

if __name__ == "__main__":
    show_xe()