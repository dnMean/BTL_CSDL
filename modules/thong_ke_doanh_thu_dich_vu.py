import streamlit as st
import pandas as pd
from db_config import call_procedure, execute_query
from datetime import datetime

def show_thong_ke_doanh_thu():
    st.header("📊 THỐNG KÊ DOANH THU DỊCH VỤ")

    tab1, tab2 = st.tabs([
        "📋 Thống kê theo tháng",
        "📈 Biểu đồ doanh thu"
    ])

    # ======================================================
    # TAB 1 – THỐNG KÊ THEO THÁNG
    # ======================================================
    with tab1:
        st.subheader("📋 Thống kê doanh thu dịch vụ theo tháng")

        # ===== Bộ lọc =====
        col1, col2, col3 = st.columns([2, 2, 1])
        
        now = datetime.now()
        
        with col1:
            thang = st.selectbox(
                "Chọn tháng *",
                list(range(1, 13)),
                index=now.month - 1,
                format_func=lambda x: f"Tháng {x}"
            )
        
        with col2:
            nam = st.selectbox(
                "Chọn năm *",
                [now.year - 2, now.year - 1, now.year, now.year + 1],
                index=2
            )
        
        with col3:
            st.write("")  # Spacer
            st.write("")
            btn_search = st.button("🔍 Tìm kiếm", type="primary", use_container_width=True)

        # ===== Gọi procedure =====
        if btn_search or 'data_thong_ke' not in st.session_state:
            success, message, data = call_procedure(
                "ThongKeDoanhThuDichVu",
                [thang, nam]
            )

            if success and data:
                st.session_state.data_thong_ke = data
                st.session_state.thang_selected = thang
                st.session_state.nam_selected = nam
            else:
                st.session_state.data_thong_ke = None

        # ===== Hiển thị dữ liệu =====
        if st.session_state.get('data_thong_ke'):
            data = st.session_state.data_thong_ke
            df = pd.DataFrame(data)
            
            # Đổi tên cột
            df.columns = [
                'Tên Dịch Vụ',
                'Tháng/Năm',
                'Đơn Giá',
                'Đơn Vị',
                'Tổng Số Lượng',
                'Tổng Doanh Thu'
            ]

            # ===== Thống kê tổng quan =====
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            # Xử lý None trước khi tính toán
            df['Tổng Doanh Thu'] = df['Tổng Doanh Thu'].fillna(0)
            df['Tổng Số Lượng'] = df['Tổng Số Lượng'].fillna(0)
            df['Đơn Giá'] = df['Đơn Giá'].fillna(0)
            
            tong_doanh_thu = df['Tổng Doanh Thu'].sum()
            so_dich_vu = len(df)
            tong_so_luong = df['Tổng Số Lượng'].sum()
            
            col1.metric(
                "💰 Tổng Doanh Thu",
                f"{tong_doanh_thu:,.0f}đ"
            )
            col2.metric(
                "📦 Số Loại Dịch Vụ",
                so_dich_vu
            )
            col3.metric(
                "📊 Tổng Số Lượng",
                f"{tong_so_luong:,.0f}"
            )
            col4.metric(
                "📅 Kỳ Thống Kê",
                f"{st.session_state.get('thang_selected', thang)}/{st.session_state.get('nam_selected', nam)}"
            )

            st.markdown("---")

            # ===== Bảng chi tiết =====
            st.subheader("📋 Chi tiết doanh thu theo dịch vụ")
            
            # Format hiển thị (xử lý None)
            df_display = df.copy()
            df_display['Đơn Giá'] = df_display['Đơn Giá'].apply(
                lambda x: f"{x:,.0f}đ" if x is not None else "0đ"
            )
            df_display['Tổng Số Lượng'] = df_display['Tổng Số Lượng'].apply(
                lambda x: f"{x:,.0f}" if x is not None else "0"
            )
            df_display['Tổng Doanh Thu'] = df_display['Tổng Doanh Thu'].apply(
                lambda x: f"{x:,.0f}đ" if x is not None else "0đ"
            )
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # ===== Dòng tổng cộng =====
            st.success(f"**📌 TỔNG CỘNG DOANH THU: {tong_doanh_thu:,.0f}đ**")

            # ===== Xuất dữ liệu =====
            st.markdown("---")
            st.subheader("📥 Xuất dữ liệu")
            
            col1, col2 = st.columns(2)
            
            with col1:
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📄 Tải xuống CSV",
                    data=csv,
                    file_name=f"thong_ke_doanh_thu_{thang}_{nam}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                try:
                    from io import BytesIO
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Thống kê')
                    
                    st.download_button(
                        label="📊 Tải xuống Excel",
                        data=buffer.getvalue(),
                        file_name=f"thong_ke_doanh_thu_{thang}_{nam}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                except ImportError:
                    st.warning("Cần cài đặt openpyxl để xuất Excel")

        else:
            st.warning("⚠️ Không có dữ liệu. Vui lòng chọn tháng/năm và nhấn Tìm kiếm.")

    # ======================================================
    # TAB 2 – BIỂU ĐỒ DOANH THU
    # ======================================================
    with tab2:
        st.subheader("📈 Biểu đồ doanh thu")

        if st.session_state.get('data_thong_ke'):
            data = st.session_state.data_thong_ke
            df = pd.DataFrame(data)
            df.columns = [
                'Tên Dịch Vụ',
                'Tháng/Năm',
                'Đơn Giá',
                'Đơn Vị',
                'Tổng Số Lượng',
                'Tổng Doanh Thu'
            ]
            
            # Xử lý None
            df['Tổng Doanh Thu'] = df['Tổng Doanh Thu'].fillna(0)
            df['Tổng Số Lượng'] = df['Tổng Số Lượng'].fillna(0)
            df['Đơn Giá'] = df['Đơn Giá'].fillna(0)

            # ===== Biểu đồ cột =====
            st.subheader("📊 Doanh thu theo dịch vụ")
            st.bar_chart(
                df.set_index('Tên Dịch Vụ')['Tổng Doanh Thu'],
                use_container_width=True
            )

            # ===== Biểu đồ tròn (dùng plotly nếu có) =====
            try:
                import plotly.express as px
                
                st.subheader("🥧 Tỷ lệ doanh thu")
                fig = px.pie(
                    df,
                    values='Tổng Doanh Thu',
                    names='Tên Dịch Vụ',
                    hole=0.4
                )
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label'
                )
                st.plotly_chart(fig, use_container_width=True)
                
            except ImportError:
                st.info("💡 Cài đặt plotly để xem biểu đồ tròn: pip install plotly")

            # ===== Bảng xếp hạng =====
            st.subheader("🏆 Xếp hạng doanh thu")
            
            df_rank = df.sort_values('Tổng Doanh Thu', ascending=False).reset_index(drop=True)
            df_rank.index = df_rank.index + 1
            df_rank.index.name = 'Hạng'
            
            df_rank_display = df_rank[['Tên Dịch Vụ', 'Tổng Số Lượng', 'Tổng Doanh Thu']].copy()
            df_rank_display['Tổng Doanh Thu'] = df_rank_display['Tổng Doanh Thu'].apply(
                lambda x: f"{x:,.0f}đ" if x is not None else "0đ"
            )
            
            st.dataframe(df_rank_display, use_container_width=True)

        else:
            st.warning("⚠️ Vui lòng chọn tháng/năm ở tab 'Thống kê theo tháng' trước.")


if __name__ == "__main__":
    show_thong_ke_doanh_thu()