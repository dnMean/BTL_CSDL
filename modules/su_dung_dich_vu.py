import streamlit as st
import pandas as pd
from datetime import datetime, date
from db_config import call_procedure

def show_su_dung_dich_vu():
    st.header("📊 Quản lý Sử Dụng Dịch Vụ")
    
    # ===== TOAST =====
    if "sddv_toast" in st.session_state and st.session_state.sddv_toast:
        st.toast(st.session_state.sddv_toast, icon="✅")
        st.session_state.sddv_toast = None
    
    tab1, tab2, tab3 = st.tabs(["📋 Danh sách", "➕ Thêm mới", "✏️ Sửa / 🗑️ Xóa"])
    
    # ================= TAB 1: DANH SÁCH =================
    with tab1:
        st.subheader("📋 Danh sách sử dụng dịch vụ")
        
        # Lấy danh sách
        success, _, data = call_procedure("sp_ds_su_dung_dich_vu")
        
        if success and data:
            df_original = pd.DataFrame(data)
            
            # ===== THANH TÌM KIẾM =====
            st.markdown("### 🔍 Tìm kiếm & Lọc")
            
            col_search1, col_search2, col_search3, col_search4 = st.columns(4)
            
            with col_search1:
                search_msv = st.text_input(
                    "🆔 Mã SV",
                    placeholder="Nhập mã sinh viên...",
                    key="search_msv"
                )
            
            with col_search2:
                search_ten = st.text_input(
                    "👤 Tên sinh viên",
                    placeholder="Nhập tên...",
                    key="search_ten"
                )
            
            with col_search3:
                search_trangthai = st.selectbox(
                    "💳 Trạng thái",
                    options=["Tất cả", "Đã thanh toán", "Chưa thanh toán"],
                    key="search_trangthai"
                )
            
            with col_search4:
                # Lấy danh sách tháng/năm có trong dữ liệu
                months_available = sorted(
                    df_original['Thang_Nam'].apply(
                        lambda x: pd.to_datetime(x).strftime('%m/%Y')
                    ).unique(),
                    reverse=True
                )
                search_thang = st.selectbox(
                    "📅 Tháng/Năm",
                    options=["Tất cả"] + months_available,
                    key="search_thang"
                )
            
            # ===== LỌC DỮ LIỆU =====
            df_filtered = df_original.copy()
            
            # Lọc theo Mã SV
            if search_msv:
                df_filtered = df_filtered[
                    df_filtered['MSV'].str.contains(search_msv, case=False, na=False)
                ]
            
            # Lọc theo Tên
            if search_ten:
                df_filtered = df_filtered[
                    df_filtered['HoTen'].str.contains(search_ten, case=False, na=False)
                ]
            
            # Lọc theo Trạng thái
            if search_trangthai == "Đã thanh toán":
                df_filtered = df_filtered[df_filtered['TrangThaiTT'] == 1]
            elif search_trangthai == "Chưa thanh toán":
                df_filtered = df_filtered[df_filtered['TrangThaiTT'] == 0]
            
            # Lọc theo Tháng/Năm
            if search_thang != "Tất cả":
                df_filtered = df_filtered[
                    df_filtered['Thang_Nam'].apply(
                        lambda x: pd.to_datetime(x).strftime('%m/%Y')
                    ) == search_thang
                ]
            
            st.divider()
            
            # ===== HIỂN THỊ KẾT QUẢ =====
            if len(df_filtered) > 0:
                # Tính toán trước khi format
                total_amount = df_filtered['ThanhTien'].sum()
                chua_thanh_toan = len(df_filtered[df_filtered['TrangThaiTT'] == 0])
                
                # Format dữ liệu để hiển thị
                df_display = df_filtered.copy()
                
                # Format currency columns
                df_display['DonGia'] = df_display['DonGia'].apply(lambda x: f"{x:,.0f} đ")
                df_display['ThanhTien'] = df_display['ThanhTien'].apply(lambda x: f"{x:,.0f} đ")
                
                # Format date
                df_display['Thang_Nam'] = pd.to_datetime(df_display['Thang_Nam']).dt.strftime('%m/%Y')
                
                # Format trạng thái
                df_display['TrangThaiTT'] = df_display['TrangThaiTT'].apply(
                    lambda x: '✅ Đã thanh toán' if x == 1 else '⏳ Chưa thanh toán'
                )
                
                # Rename columns
                df_display = df_display.rename(columns={
                    'MASD': 'Mã SD',
                    'MSV': 'Mã SV',
                    'HoTen': 'Họ tên',
                    'TenDV': 'Dịch vụ',
                    'SoLuong': 'Số lượng',
                    'DonGia': 'Đơn giá',
                    'ThanhTien': 'Thành tiền',
                    'MaHoaDon': 'Mã hóa đơn',
                    'Thang_Nam': 'Tháng/Năm',
                    'TrangThaiTT': 'Trạng thái'
                })
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                # Thống kê
                col1, col2, col3, col4 = st.columns(4)
                
                col1.metric("Kết quả tìm kiếm", len(df_filtered))
                col2.metric("Tổng số dịch vụ", len(df_original))
                col3.metric("Tổng tiền (đã lọc)", f"{total_amount:,.0f} đ")
                col4.metric("Chưa thanh toán", chua_thanh_toan)
                
            else:
                st.warning("⚠️ Không tìm thấy kết quả phù hợp với điều kiện tìm kiếm")
                
                # Vẫn hiển thị thống kê tổng
                col1, col2 = st.columns(2)
                total_all = df_original['ThanhTien'].sum()
                col1.metric("Tổng số dịch vụ", len(df_original))
                col2.metric("Tổng tiền (tất cả)", f"{total_all:,.0f} đ")
        else:
            st.info("Chưa có dữ liệu sử dụng dịch vụ")
    
    # ================= TAB 2: THÊM MỚI =================
    with tab2:
        st.subheader("➕ Thêm sử dụng dịch vụ mới")
        
        # Lấy danh sách sinh viên
        success_sv, _, data_sv = call_procedure("sp_ds_SINHVIEN")
        # Lấy danh sách dịch vụ
        success_dv, _, data_dv = call_procedure("sp_ds_dichvu")
        
        if not (success_sv and data_sv):
            st.warning("⚠️ Không có sinh viên trong hệ thống")
            return
        
        if not (success_dv and data_dv):
            st.warning("⚠️ Không có dịch vụ trong hệ thống")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Chọn sinh viên
            sv_options = [
                f"{sv['MSV']} - {sv['HoTen']}" for sv in data_sv
            ]
            selected_sv = st.selectbox(
                "Chọn sinh viên *",
                sv_options,
                key="add_msv"
            )
            msv = selected_sv.split(' - ')[0]
            
            # Số lượng
            so_luong = st.number_input(
                "Số lượng *",
                min_value=1,
                value=1,
                step=1,
                key="add_so_luong"
            )
        
        with col2:
            # Chọn dịch vụ
            dv_options = [
                f"{dv['TenDV']} - {dv['DonGia']:,.0f}đ/{dv['DonVi']}" 
                for dv in data_dv
            ]
            selected_dv = st.selectbox(
                "Chọn dịch vụ *",
                dv_options,
                key="add_madv"
            )
            # Lấy MADV từ index
            madv = data_dv[dv_options.index(selected_dv)]['MADV']
            
            # Ngày sử dụng
            ngay_su_dung = st.date_input(
                "Ngày sử dụng *",
                value=date.today(),
                key="add_ngay_su_dung"
            )
        
        # Hiển thị thông tin tạm tính
        selected_dv_data = data_dv[dv_options.index(selected_dv)]
        thanh_tien = so_luong * float(selected_dv_data['DonGia'])
        
        st.info(f"""
        📝 **Thông tin sử dụng dịch vụ:**
        - Sinh viên: **{selected_sv}**
        - Dịch vụ: **{selected_dv_data['TenDV']}**
        - Số lượng: **{so_luong}** {selected_dv_data['DonVi']}
        - Đơn giá: **{selected_dv_data['DonGia']:,.0f}** đ
        - Thành tiền: **{thanh_tien:,.0f}** đ
        - Tháng: **{ngay_su_dung.strftime('%m/%Y')}**
        """)
        
        if st.button("➕ Thêm sử dụng dịch vụ", type="primary", use_container_width=True):
            success, message, _ = call_procedure(
                "sp_them_su_dung_dich_vu",
                [msv, madv, so_luong, ngay_su_dung]
            )
            
            if success:
                st.session_state.sddv_toast = "Thêm sử dụng dịch vụ thành công!"
                st.rerun()
            else:
                st.error(f"❌ {message}")
    
    # ================= TAB 3: SỬA / XÓA =================
    with tab3:
        st.subheader("✏️ Sửa / 🗑️ Xóa sử dụng dịch vụ")
        
        success, _, data = call_procedure("sp_ds_su_dung_dich_vu")
        
        if not (success and data):
            st.info("Chưa có dữ liệu để chỉnh sửa")
            return
        
        # Tạo dictionary mapping
        sddv_dict = {item['MASD']: item for item in data}
        
        # Tạo options cho selectbox
        sddv_options = [
            f"{item['HoTen']} - {item['TenDV']} - {item['SoLuong']} x {item['DonGia']:,.0f}đ ({pd.to_datetime(item['Thang_Nam']).strftime('%m/%Y')})"
            for item in data
        ]
        
        selected = st.selectbox(
            "Chọn sử dụng dịch vụ cần chỉnh sửa",
            sddv_options,
            key="select_sddv"
        )
        
        # Lấy MASD
        masd_selected = list(sddv_dict.keys())[sddv_options.index(selected)]
        sddv = sddv_dict[masd_selected]
        
        # Hiển thị thông tin
        st.markdown(f"""
        **📌 Thông tin hiện tại:**
        - Sinh viên: **{sddv['HoTen']}** (MSV: {sddv['MSV']})
        - Dịch vụ: **{sddv['TenDV']}**
        - Đơn giá: **{sddv['DonGia']:,.0f}** đ
        - Tháng: **{pd.to_datetime(sddv['Thang_Nam']).strftime('%m/%Y')}**
        - Mã hóa đơn: **{sddv['MaHoaDon']}**
        """)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✏️ Chỉnh sửa")
            
            # Chỉ cho phép sửa số lượng
            new_so_luong = st.number_input(
                "Số lượng mới *",
                min_value=1,
                value=int(sddv['SoLuong']),
                step=1,
                key=f"edit_sl_{masd_selected}"
            )
            
            # Tính lại thành tiền
            new_thanh_tien = new_so_luong * float(sddv['DonGia'])
            st.info(f"Thành tiền mới: **{new_thanh_tien:,.0f}** đ")
            
            if st.button("💾 Cập nhật", type="primary", use_container_width=True):
                success, message, _ = call_procedure(
                    "sp_sua_su_dung_dich_vu",
                    [masd_selected, new_so_luong]
                )
                
                if success:
                    st.session_state.sddv_toast = "Cập nhật thành công!"
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
        
        with col2:
            st.markdown("### 🗑️ Xóa")
            
            st.warning("""
            ⚠️ **Lưu ý:** Xóa sử dụng dịch vụ sẽ:
            - Xóa bản ghi này khỏi hệ thống
            - Nếu hóa đơn không còn dịch vụ nào, hóa đơn cũng sẽ bị xóa
            """)
            
            confirm_delete = st.checkbox(
                "Xác nhận xóa sử dụng dịch vụ này",
                key=f"confirm_del_{masd_selected}"
            )
            
            if st.button("🗑️ Xóa", use_container_width=True):
                if not confirm_delete:
                    st.warning("⚠️ Vui lòng xác nhận xóa")
                    return
                
                success, message, _ = call_procedure(
                    "sp_xoa_su_dung_dich_vu",
                    [masd_selected]
                )
                
                if success:
                    st.session_state.sddv_toast = "Xóa thành công!"
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

if __name__ == "__main__":
    show_su_dung_dich_vu()