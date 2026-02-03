import streamlit as st
import pandas as pd
from db_config import call_procedure, execute_query
from datetime import date

def show_sinh_vien():
    st.header("🎓 Quản lý Sinh Viên")
    
    # Tabs cho các chức năng
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Danh sách", "➕ Thêm mới", "✏️ Sửa", "🗑️ Xóa"])
    
    # ===================== TAB DANH SÁCH =====================
    with tab1:
        st.subheader("Danh sách Sinh Viên")
        if st.button("🔄 Tải lại dữ liệu", key="reload_sv"):
            st.rerun()
        
        success, message, data = call_procedure("sp_ds_SINHVIEN")
        
        if success and data:
            df = pd.DataFrame(data)
            # Đổi tên cột cho dễ đọc
            df.columns = ['Mã SV', 'Họ Tên', 'Ngày Sinh', 'Giới Tính', 'CCCD', 'SĐT']
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.info(f"Tổng số sinh viên: {len(df)}")
        elif success and not data:
            st.warning("Chưa có sinh viên nào trong hệ thống")
        else:
            st.error(message)
    
    # ===================== TAB THÊM MỚI =====================
    with tab2:
        st.subheader("Thêm Sinh Viên Mới")
        
        with st.form("form_them_sv", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                msv = st.text_input("Mã sinh viên *", placeholder="VD: SV001")
                ho_ten = st.text_input("Họ và tên *", placeholder="Nguyễn Văn A")
                ngay_sinh = st.date_input("Ngày sinh *", min_value=date(1990, 1, 1), max_value=date.today())
            
            with col2:
                gioi_tinh = st.selectbox("Giới tính *", ["Nam", "Nữ", "Khác"])
                cccd = st.text_input("Số CCCD *", placeholder="012345678901")
                sdt = st.text_input("Số điện thoại *", placeholder="0901234567")
            
            submitted = st.form_submit_button("➕ Thêm sinh viên", use_container_width=True)
            
            if submitted:
                if not all([msv, ho_ten, cccd, sdt]):
                    st.error("Vui lòng điền đầy đủ thông tin bắt buộc (*)")
                else:
                    success, message, _ = call_procedure(
                        "sp_ThemSinhVien",
                        [msv, ho_ten, ngay_sinh, gioi_tinh, cccd, sdt]
                    )
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
    
    # ===================== TAB SỬA =====================
    with tab3:
        st.subheader("Sửa Thông Tin Sinh Viên")
        
        # Lấy danh sách sinh viên để chọn
        success, _, data = call_procedure("sp_ds_SINHVIEN")
        
        if success and data:
            # Tạo dictionary để tra cứu
            sv_dict = {sv['MSV']: sv for sv in data}
            sv_options = [f"{sv['MSV']} - {sv['HoTen']}" for sv in data]
            
            selected = st.selectbox("Chọn sinh viên cần sửa", sv_options, key="select_sua_sv")
            
            if selected:
                msv_selected = selected.split(" - ")[0]
                sv_info = sv_dict[msv_selected]
                
                with st.form("form_sua_sv"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.text_input("Mã sinh viên", value=msv_selected, disabled=True)
                        ho_ten = st.text_input("Họ và tên *", value=sv_info['HoTen'])
                        ngay_sinh = st.date_input("Ngày sinh *", value=sv_info['NgaySinh'])
                    
                    with col2:
                        gioi_tinh_options = ["Nam", "Nữ", "Khác"]
                        gioi_tinh_index = gioi_tinh_options.index(sv_info['GioiTinh']) if sv_info['GioiTinh'] in gioi_tinh_options else 0
                        gioi_tinh = st.selectbox("Giới tính *", gioi_tinh_options, index=gioi_tinh_index)
                        cccd = st.text_input("Số CCCD *", value=sv_info['CCCD'])
                        sdt = st.text_input("Số điện thoại *", value=sv_info['SDT'])
                    
                    submitted = st.form_submit_button("💾 Cập nhật", use_container_width=True)
                    
                    if submitted:
                        success, message, _ = call_procedure(
                            "sp_SuaSinhVien",
                            [msv_selected, ho_ten, ngay_sinh, gioi_tinh, cccd, sdt]
                        )
                        if success:
                            st.success(f"✅ {message}")
                        else:
                            st.error(f"❌ {message}")
        else:
            st.warning("Chưa có sinh viên nào để sửa")
    
    # ===================== TAB XÓA =====================
    with tab4:
        st.subheader("Xóa Sinh Viên")
        
        success, _, data = call_procedure("sp_ds_SINHVIEN")
        
        if success and data:
            sv_options = [f"{sv['MSV']} - {sv['HoTen']}" for sv in data]
            selected = st.selectbox("Chọn sinh viên cần xóa", sv_options, key="select_xoa_sv")
            
            if selected:
                msv_selected = selected.split(" - ")[0]
                
                st.warning(f"⚠️ Bạn có chắc chắn muốn xóa sinh viên **{selected}**?")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Xác nhận xóa", type="primary", use_container_width=True):
                        success, message, _ = call_procedure("sp_XoaSinhVien", [msv_selected])
                        if success:
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
        else:
            st.warning("Chưa có sinh viên nào để xóa")

if __name__ == "__main__":
    show_sinh_vien()