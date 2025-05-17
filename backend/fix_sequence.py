#!/usr/bin/env python3
"""
Script để sửa lỗi trùng lặp ID trong bảng images và reset sequence
"""
import os
import sys
from app.utils.db import get_db_connection

def main():
    """
    Sửa lỗi trùng lặp ID trong bảng images và reset sequence
    """
    try:
        # Thiết lập kết nối cơ sở dữ liệu
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Lấy ID lớn nhất hiện tại trong bảng images
        cursor.execute("SELECT MAX(id) FROM images")
        max_id = cursor.fetchone()[0]
        
        if max_id is None:
            print("Bảng images trống, không cần reset sequence.")
            return 0
        
        print(f"ID lớn nhất hiện tại trong bảng images: {max_id}")
        
        # Reset sequence để bắt đầu từ giá trị lớn hơn max_id
        new_start = max_id + 1
        cursor.execute(f"ALTER SEQUENCE images_id_seq RESTART WITH {new_start}")
        
        print(f"Đã reset sequence images_id_seq để bắt đầu từ {new_start}")
        
        # Kiểm tra xem sequence đã được reset chưa
        cursor.execute("SELECT nextval('images_id_seq')")
        next_val = cursor.fetchone()[0]
        
        print(f"Giá trị tiếp theo của sequence: {next_val}")
        
        # Reset lại sequence sau khi kiểm tra
        cursor.execute(f"ALTER SEQUENCE images_id_seq RESTART WITH {new_start}")
        
        # Lưu các thay đổi
        conn.commit()
        
        # Đóng kết nối
        cursor.close()
        conn.close()
        
        print("Hoàn tất việc sửa lỗi trùng lặp ID trong bảng images.")
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main()) 