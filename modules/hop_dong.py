import streamlit as st
import pandas as pd
from db_config import call_procedure, execute_query
from datetime import date, timedelta


def get_don_gia(ma_loai, loai_block):
    """Lấy đơn giá từ bảng giá theo loại phòng và loại block"""
    query = """
        SELECT DonGia 
        FROM BANG_GIA 
        WHERE MaLoai = %s
          AND LoaiBlock = %s
        LIMIT 1
    """
    result = execute_query(query, (ma_loai, loai_block))
    if result:
        return result[0]['DonGia']
    return 0



def show_hop_dong():
    st.header("📝 Quản lý Hợp Đồng")
    
    # Hiển thị toast message nếu có
    if "hd_toast" in st.session_state and st.session_state.hd_toast:
        st.toast(st.session_state.hd_toast, icon="✅")
        st.session_state.hd_toast = None
    
    # Tabs cho các chức năng
    tab1, tab2, tab3 = st.tabs(["📋 Danh sách", "➕ Thêm mới", "✏️ Sửa"])
    
    # ===================== TAB DANH SÁCH =====================
    with tab1:
        st.subheader("Danh sách Hợp Đồng")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_status = st.selectbox(
                "Lọc theo trạng thái", 
                ["Tất cả","Đang hiệu lực", "Hết hạn"],
                key="filter_trang_thai"
            )
        with col2:
            search_sv = st.text_input("Tìm theo tên SV", placeholder="Nhập tên...", key="search_sv")
        with col3:
            if st.button("🔄 Tải lại dữ liệu", key="reload_hd"):
                st.rerun()
        
        # Gọi procedure với tham số trạng thái
        success, message, data = call_procedure("sp_hd_xem_all", [])

        if success and data:
            df = pd.DataFrame(data)
            df.columns = [
                'Mã HĐ', 'Ngày Ký', 'Ngày Bắt Đầu', 'Ngày Kết Thúc',
                'Loại Block', 'Đơn Giá/Block', 'Trạng Thái',
                'MSV', 'Họ Tên SV', 'Mã Phòng', 'Tên KTX'
            ]


            filtered_df = df.copy()

            # 🔹 Filter theo trạng thái
            if filter_status != "Tất cả":
                filtered_df = filtered_df[
                    filtered_df['Trạng Thái'] == filter_status
                ]

            # 🔹 Filter theo tên SV
            if search_sv:
                filtered_df = filtered_df[
                    filtered_df['Họ Tên SV'].str.contains(
                        search_sv, case=False, na=False
                    )
                ]

            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Chưa có hợp đồng nào")
    
    # ===================== TAB THÊM MỚI =====================
    with tab2:
        st.subheader("Thêm Hợp Đồng Mới")
        
        # Lấy danh sách sinh viên
        success_sv, _, data_sv = call_procedure("sp_ds_SINHVIEN")
        # Lấy danh sách phòng
        success_phong, _, data_phong = call_procedure("sp_ds_phong")
        
        if not (success_sv and data_sv):
            st.error("Không thể tải danh sách sinh viên")
            return
        
        if not (success_phong and data_phong):
            st.error("Không thể tải danh sách phòng")
            return
        
        # Lấy thông tin MaLoai cho mỗi phòng
        phong_loai_query = """
            SELECT p.MaPhong, p.MaLoai, k.Ten AS TenKTX, k.MaKTX
            FROM PHONG p
            JOIN KTX k ON p.MaKTX = k.MaKTX
        """
        phong_loai_data = execute_query(phong_loai_query)
        phong_loai_dict = {}
        if phong_loai_data:
            for item in phong_loai_data:
                key = f"{item['MaPhong']}_{item['TenKTX']}"
                phong_loai_dict[key] = {
                    'MaLoai': item['MaLoai'],
                    'MaKTX': item['MaKTX']
                }
        
        # Khởi tạo session state cho đơn giá
        if "hd_don_gia" not in st.session_state:
            st.session_state.hd_don_gia = 0
        if "hd_ma_loai" not in st.session_state:
            st.session_state.hd_ma_loai = None
        if "hd_ma_ktx" not in st.session_state:
            st.session_state.hd_ma_ktx = None
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Chọn sinh viên
            sv_options = [f"{sv['MSV']} - {sv['HoTen']}" for sv in data_sv]
            selected_sv = st.selectbox("Chọn sinh viên *", sv_options, key="select_sv_add")
            
            # Chọn phòng
            phong_options = [f"{p['MaPhong']} - {p['TenKTX']} (Tầng {p['Tang']}, {p['SoNguoiHienTai']}/{p['SoNguoiToiDa']})" 
                            for p in data_phong]
            selected_phong = st.selectbox("Chọn phòng *", phong_options, key="select_phong_add")
            
            ngay_ky = st.date_input("Ngày ký *", value=date.today(), key="ngay_ky_add")
            ngay_bat_dau = st.date_input("Ngày bắt đầu *", value=date.today(), key="ngay_bat_dau_add")
        with col2:
            ngay_ket_thuc = st.date_input("Ngày kết thúc *", value=date.today() + timedelta(days=120), key="ngay_ket_thuc_add")
            
            # Loại block: 10, 15, 30
            loai_block = st.selectbox("Loại block *", ["10", "15", "chẵn tháng"], key="loai_block_add")
            
            # Parse thông tin phòng để lấy MaLoai
            phong_info = selected_phong.split(" - ")
            ma_phong = phong_info[0]
            ten_ktx = phong_info[1].split(" (")[0]
            
            phong_key = f"{ma_phong}_{ten_ktx}"
            
            # Tính đơn giá realtime
            don_gia = 0
            ma_loai = None
            ma_ktx = None
            
            if phong_key in phong_loai_dict:
                ma_loai = phong_loai_dict[phong_key]['MaLoai']
                ma_ktx = phong_loai_dict[phong_key]['MaKTX']
                don_gia = get_don_gia(ma_loai, loai_block)
            
            # Cập nhật session state
            st.session_state.hd_don_gia = don_gia
            st.session_state.hd_ma_loai = ma_loai
            st.session_state.hd_ma_ktx = ma_ktx
            
            # Hiển thị đơn giá (không cho chỉnh)
            st.metric(
                "Đơn Giá/ Block (VNĐ)", 
                value=f"{don_gia:,.0f}" if don_gia else "Chưa có giá"
            )
                    
        st.info("""
            ℹ️ **Lưu ý:**
            - Mỗi sinh viên chỉ được có một hợp đồng còn hiệu lực tại một thời điểm
            - Phòng phải còn chỗ trống để đăng ký
            - Đơn giá được lấy tự động từ bảng giá theo loại phòng và loại block
        """)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("➕ Thêm hợp đồng", type="primary", use_container_width=True, key="btn_them_hd"):
                if st.session_state.hd_don_gia == 0:
                    st.error("Không tìm thấy đơn giá cho loại phòng và loại block này. Vui lòng kiểm tra bảng giá.")
                elif st.session_state.hd_ma_ktx is None:
                    st.error("Không tìm thấy thông tin KTX")
                else:
                    msv = selected_sv.split(" - ")[0]
                    
                    success, message, _ = call_procedure(
                        "sp_hd_them",
                        [ngay_ky, ngay_bat_dau, ngay_ket_thuc, loai_block, 
                         st.session_state.hd_don_gia, msv, ma_phong, st.session_state.hd_ma_ktx]
                    )
                    
                    if success:
                        st.session_state.hd_toast = "Thêm hợp đồng thành công!"
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    # ===================== TAB SỬA =====================
    with tab3:
        st.subheader("Sửa Hợp Đồng")
        
        success, _, data = call_procedure("sp_hd_xem_all")
        
        if success and data:
            hd_dict = {hd['MaHD']: hd for hd in data}
            
            # Lấy thêm thông tin sinh viên
            query = """
                SELECT hd.MaHD, sv.HoTen 
                FROM HOP_DONG hd 
                JOIN SINH_VIEN sv ON hd.MSV = sv.MSV
            """
            sv_info = execute_query(query)
            sv_dict = {item['MaHD']: item['HoTen'] for item in sv_info} if sv_info else {}
            
            hd_options = [f"{hd['MaHD'][:8]}... - {sv_dict.get(hd['MaHD'], 'N/A')}" for hd in data]
            
            selected = st.selectbox("Chọn hợp đồng cần sửa", hd_options, key="select_sua_hd")
            
            if selected:
                ma_hd_selected = list(hd_dict.keys())[hd_options.index(selected)]
                hd_info = hd_dict[ma_hd_selected]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.text_input("Mã hợp đồng", value=ma_hd_selected[:20] + "...", disabled=True, key="ma_hd_edit")
                    ngay_bat_dau = st.date_input("Ngày bắt đầu *", value=hd_info['NgayBatDau'], key="ngay_bat_dau_edit")
                    ngay_ket_thuc = st.date_input("Ngày kết thúc *", value=hd_info['NgayKetThuc'], key="ngay_ket_thuc_edit")
                
                with col2:
                    loai_block_options = ["10", "15", "chẵn tháng"]
                    current_loai_block = hd_info['LoaiBlock']
                    loai_block_index = loai_block_options.index(current_loai_block) if current_loai_block in loai_block_options else 0
                    loai_block = st.selectbox("Loại block *", loai_block_options, index=loai_block_index, key="loai_block_edit")
                    
                    don_gia = st.number_input("Đơn giá (VNĐ) *", min_value=0, value=int(hd_info['DonGia']), step=50000, key="don_gia_edit")
                    
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💾 Cập nhật", type="primary", use_container_width=True, key="btn_cap_nhat_hd"):
                        success, message, _ = call_procedure(
                            "sp_hd_sua",
                            [ma_hd_selected, ngay_bat_dau, ngay_ket_thuc, loai_block, don_gia]
                        )
                        if success:
                            st.session_state.hd_toast = "Cập nhật hợp đồng thành công!"
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
        else:
            st.warning("Chưa có hợp đồng nào để sửa")
    
    

if __name__ == "__main__":
    show_hop_dong()