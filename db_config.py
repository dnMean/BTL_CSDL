import mysql.connector
from mysql.connector import Error
import streamlit as st

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Thay đổi password của bạn
    'database': 'BTL_CSDL',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def get_connection():
    """Tạo kết nối đến MySQL database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        st.error(f"Lỗi kết nối database: {e}")
        return None

def call_procedure(proc_name, params=None):
    """
    Gọi stored procedure và trả về kết quả/message
    Returns: (success, message, data)
    """
    conn = get_connection()
    if not conn:
        return False, "Không thể kết nối database", None
    
    try:
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.callproc(proc_name, params)
        else:
            cursor.callproc(proc_name)
        
        # Lấy tất cả kết quả từ procedure
        results = []
        for result in cursor.stored_results():
            results.extend(result.fetchall())
        
        conn.commit()
        
        # Kiểm tra nếu có message trả về
        if results and len(results) == 1 and 'Message' in results[0]:
            return True, results[0]['Message'], None
        
        return True, "Thành công", results
        
    except Error as e:
        error_msg = str(e)
        # Xử lý message từ SIGNAL SQLSTATE
        if "1644" in error_msg:
            # Trích xuất message từ lỗi MySQL
            parts = error_msg.split(":")
            if len(parts) > 1:
                return False, parts[-1].strip(), None
        return False, f"Lỗi: {error_msg}", None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
def call_procedure_v2(proc_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.callproc(proc_name)

    rows = []
    for result in cursor.stored_results():
        rows = result.fetchall()

    cursor.close()
    conn.close()

    return rows 

def execute_query(query, params=None):
    """Thực thi query SELECT và trả về kết quả"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Error as e:
        st.error(f"Lỗi query: {e}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()