use BTL_CSDL;


DROP PROCEDURE IF EXISTS sp_ThemSinhVien;

DELIMITER $$

CREATE PROCEDURE sp_ThemSinhVien(
    IN p_MSV VARCHAR(36),
    IN p_HoTen VARCHAR(100),
    IN p_NgaySinh DATE,
    IN p_GioiTinh VARCHAR(10),
    IN p_CCCD VARCHAR(20),
    IN p_SDT VARCHAR(15)
)
BEGIN
    IF EXISTS (SELECT 1 FROM SINH_VIEN WHERE MSV = p_MSV) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'MSV đã tồn tại';
    END IF;

    INSERT INTO SINH_VIEN (MSV, HoTen, NgaySinh, GioiTinh, CCCD, SDT)
    VALUES (p_MSV, p_HoTen, p_NgaySinh, p_GioiTinh, p_CCCD, p_SDT);

    SELECT 'Thêm sinh viên thành công' AS Message;
END$$

DELIMITER ;


-- Sửa Sinh Viên
DROP PROCEDURE IF EXISTS sp_SuaSinhVien;

DELIMITER $$

CREATE PROCEDURE sp_SuaSinhVien(
    IN p_MSV VARCHAR(36),
    IN p_HoTen VARCHAR(100),
    IN p_NgaySinh DATE,
    IN p_GioiTinh VARCHAR(10),
    IN p_CCCD VARCHAR(20),
    IN p_SDT VARCHAR(15)
)
BEGIN
    -- Kiểm tra MSV có tồn tại không
    IF NOT EXISTS (SELECT 1 FROM SINH_VIEN WHERE MSV = p_MSV) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'MSV không tồn tại';
    END IF;

    -- Update sinh viên
    UPDATE SINH_VIEN
    SET 
        HoTen = p_HoTen,
        NgaySinh = p_NgaySinh,
        GioiTinh = p_GioiTinh,
        CCCD = p_CCCD,
        SDT = p_SDT
    WHERE MSV = p_MSV;

    SELECT 'Cập nhật sinh viên thành công' AS Message;
END$$

DELIMITER ;

-- Xoá sinh viên
DROP PROCEDURE IF EXISTS sp_XoaSinhVien;

DELIMITER $$

CREATE PROCEDURE sp_XoaSinhVien(
    IN p_MSV VARCHAR(36)
)
BEGIN
    -- Kiểm tra MSV có tồn tại không
    IF NOT EXISTS (SELECT 1 FROM SINH_VIEN WHERE MSV = p_MSV) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'MSV không tồn tại';
    END IF;

    -- Xoá sinh viên
    DELETE FROM SINH_VIEN
    WHERE MSV = p_MSV;

    SELECT 'Xoá sinh viên thành công' AS Message;
END$$

DELIMITER ;

-- DANH SACH SV
DROP PROCEDURE IF EXISTS sp_ds_SINHVIEN;

DELIMITER $$

CREATE PROCEDURE sp_ds_SINHVIEN()
BEGIN
    SELECT * FROM SINH_VIEN;
END$$

DELIMITER ;


-- THEM DICH_VU
DROP PROCEDURE IF EXISTS sp_them_dich_vu;

DROP PROCEDURE IF EXISTS sp_them_dich_vu;
DELIMITER $$

CREATE PROCEDURE sp_them_dich_vu(
    IN p_TenDV VARCHAR(50),
    IN p_DonGia DECIMAL(18,2),
    IN p_DonVi VARCHAR(20),
    IN p_MoTa VARCHAR(255)
)
BEGIN
    START TRANSACTION;

    -- Validate tên dịch vụ
    IF p_TenDV IS NULL OR TRIM(p_TenDV) = '' THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Tên dịch vụ không được để trống';

    -- Validate đơn giá
    ELSEIF p_DonGia <= 0 THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Đơn giá phải lớn hơn 0';

    -- Check trùng tên
    ELSEIF EXISTS (
        SELECT 1 FROM DICH_VU WHERE TenDV = p_TenDV
    ) THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Dịch vụ đã tồn tại';

    ELSE
        INSERT INTO DICH_VU (
            MADV, TenDV, DonGia, DonVi, MoTa
        )
        VALUES (
            UUID(), p_TenDV, p_DonGia, p_DonVi, p_MoTa
        );

        COMMIT;
    END IF;
END$$

DELIMITER ;



-- SUA DICH VU

DROP PROCEDURE IF EXISTS sp_sua_dich_vu;
DELIMITER $$

CREATE PROCEDURE sp_sua_dich_vu(
    IN p_MADV CHAR(36),
    IN p_TenDV VARCHAR(50),
    IN p_DonGia DECIMAL(18,2),
    IN p_DonVi VARCHAR(20),
    IN p_MoTa VARCHAR(255)
)
BEGIN
    START TRANSACTION;

    -- Check tồn tại
    IF NOT EXISTS (
        SELECT 1 FROM DICH_VU WHERE MADV = p_MADV
    ) THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Dịch vụ không tồn tại';

    -- Validate đơn giá
    ELSEIF p_DonGia <= 0 THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Đơn giá phải lớn hơn 0';

    -- Check trùng tên (trừ chính nó)
    ELSEIF EXISTS (
        SELECT 1 FROM DICH_VU 
        WHERE TenDV = p_TenDV
          AND MADV <> p_MADV
    ) THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Tên dịch vụ đã được sử dụng';

    ELSE
        UPDATE DICH_VU
        SET
            TenDV = p_TenDV,
            DonGia = p_DonGia,
            DonVi = p_DonVi,
            MoTa   = p_MoTa
        WHERE MADV = p_MADV;

        COMMIT;
    END IF;
END$$

DELIMITER ;

-- XOA DICH VU
DROP PROCEDURE IF EXISTS sp_xoa_dich_vu;
DELIMITER $$

CREATE PROCEDURE sp_xoa_dich_vu(
    IN p_MADV CHAR(36)
)
BEGIN
    DECLARE v_count INT;

    -- Check tồn tại
    IF NOT EXISTS (
        SELECT 1 FROM DICH_VU WHERE MADV = p_MADV
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Dịch vụ không tồn tại';
    END IF;

    -- Check đã sử dụng chưa
    SELECT COUNT(*)
    INTO v_count
    FROM SU_DUNG_DICH_VU
    WHERE MADV = p_MADV;

    IF v_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Không thể xoá: Dịch vụ đã được sử dụng';
    ELSE
        DELETE FROM DICH_VU WHERE MADV = p_MADV;
    END IF;
END$$

DELIMITER ;


-- DANH SACH DICH VU
DROP PROCEDURE IF EXISTS sp_ds_dichvu;
DELIMITER $$

CREATE PROCEDURE sp_ds_dichvu()
BEGIN
    SELECT
        MADV,
        TenDV,
        DonGia,
        DonVi,
        MoTa
    FROM DICH_VU
    ORDER BY TenDV;
END$$

DELIMITER ;


-- Thêm Phong
DROP PROCEDURE IF EXISTS sp_them_phong;

DELIMITER $$

CREATE PROCEDURE sp_them_phong(
    IN p_MaPhong VARCHAR(20),
    IN p_Tang INT,
    IN p_MaLoai CHAR(36),
    IN p_MaKTX INT
)
BEGIN
    DECLARE v_count INT;

    -- Kiểm tra phòng đã tồn tại trong KTX chưa
    SELECT COUNT(*) 
    INTO v_count
    FROM PHONG
    WHERE MaPhong = p_MaPhong AND MaKTX = p_MaKTX;

    IF v_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Phòng đã tồn tại trong ký túc xá';
    ELSE
        INSERT INTO PHONG(
            MaPhong, Tang, SoNguoiHienTai, MaLoai, MaKTX
        )
        VALUES (
            p_MaPhong, p_Tang, 0, p_MaLoai, p_MaKTX
        );
    END IF;
END$$

DELIMITER ;

-- Sửa PHONG
DROP PROCEDURE IF EXISTS sp_sua_phong;

DELIMITER $$

CREATE PROCEDURE sp_sua_phong(
    IN p_MaPhong VARCHAR(20),
    IN p_MaKTX INT,
    IN p_Tang INT,
    IN p_SoNguoiHienTai INT,
    IN p_MaLoai CHAR(36)
)
BEGIN
    UPDATE PHONG
    SET
        Tang = p_Tang,
        SoNguoiHienTai = p_SoNguoiHienTai,
        MaLoai = p_MaLoai
    WHERE MaPhong = p_MaPhong
      AND MaKTX = p_MaKTX;
END$$

DELIMITER ;


-- Xoá PHONG
DROP PROCEDURE IF EXISTS sp_xoa_phong;

DELIMITER $$

CREATE PROCEDURE sp_xoa_phong(
    IN p_MaPhong VARCHAR(20),
    IN p_MaKTX INT
)
BEGIN
    DECLARE v_count INT;

    SELECT COUNT(*)
    INTO v_count
    FROM HOP_DONG
    WHERE MaPhong = p_MaPhong
      AND MaKTX = p_MaKTX;

    IF v_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Không thể xoá: Phòng đã có hợp đồng';
    ELSE
        DELETE FROM PHONG
        WHERE MaPhong = p_MaPhong
          AND MaKTX = p_MaKTX;
    END IF;
END$$

DELIMITER ;


-- DANH SACH PHONG
DROP PROCEDURE IF EXISTS sp_ds_phong;

DELIMITER $$

CREATE PROCEDURE sp_ds_phong()
BEGIN
    SELECT 
        p.MaPhong,
        p.Tang,
        p.SoNguoiHienTai,
        lp.TenLoai,
        lp.SoNguoiToiDa,
        k.Ten AS TenKTX
    FROM PHONG p
    JOIN LOAI_PHONG lp ON p.MaLoai = lp.MaLoai
    JOIN KTX k ON p.MaKTX = k.MaKTX;
END$$

DELIMITER ;

-- THEM KTX
DROP PROCEDURE IF EXISTS sp_them_ktx;

DELIMITER $$

CREATE PROCEDURE sp_them_ktx(
    IN p_Ten VARCHAR(100),
    IN p_DiaChi VARCHAR(255),
    IN p_SoTang INT,
    IN p_SoPhong INT
)
BEGIN
    DECLARE v_count INT;

    SELECT COUNT(*)
    INTO v_count
    FROM KTX
    WHERE Ten = p_Ten AND DiaChi = p_DiaChi;

    IF v_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Ký túc xá đã tồn tại';
    ELSE
        INSERT INTO KTX(Ten, DiaChi, SoTang, SoPhong)
        VALUES (p_Ten, p_DiaChi, p_SoTang, p_SoPhong);
    END IF;
END$$

DELIMITER ;

-- SUA KTX
DROP PROCEDURE IF EXISTS sp_sua_ktx;

DELIMITER $$

CREATE PROCEDURE sp_sua_ktx(
    IN p_MaKTX INT,
    IN p_Ten VARCHAR(100),
    IN p_DiaChi VARCHAR(255),
    IN p_SoTang INT,
    IN p_SoPhong INT
)
BEGIN
    UPDATE KTX
    SET
        Ten = p_Ten,
        DiaChi = p_DiaChi,
        SoTang = p_SoTang,
        SoPhong = p_SoPhong
    WHERE MaKTX = p_MaKTX;
END$$

DELIMITER ;

-- XOA KTX

DROP PROCEDURE IF EXISTS sp_xoa_ktx;

DELIMITER $$

CREATE PROCEDURE sp_xoa_ktx(
    IN p_MaKTX INT
)
BEGIN
    DECLARE v_count INT;

    SELECT COUNT(*)
    INTO v_count
    FROM PHONG
    WHERE MaKTX = p_MaKTX;

    IF v_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Không thể xoá: KTX đã có phòng';
    ELSE
        DELETE FROM KTX WHERE MaKTX = p_MaKTX;
    END IF;
END$$

DELIMITER ;

-- LAY DANH SACH KTX
DROP PROCEDURE IF EXISTS sp_ds_ktx;

DELIMITER $$

CREATE PROCEDURE sp_ds_ktx()
BEGIN
    SELECT * FROM KTX;
END$$

DELIMITER ;

-- THÊM LOAI_PHONG
DROP PROCEDURE IF EXISTS sp_them_loai_phong;

DELIMITER $$

CREATE PROCEDURE sp_them_loai_phong(
    IN p_TenLoai VARCHAR(100),
    IN p_MoTa VARCHAR(255),
    IN p_DienTich DECIMAL(10,2),
    IN p_SoNguoiToiDa INT
)
BEGIN
    DECLARE v_count INT;

    SELECT COUNT(*)
    INTO v_count
    FROM LOAI_PHONG
    WHERE TenLoai = p_TenLoai;

    IF v_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Loại phòng đã tồn tại';
    ELSE
        INSERT INTO LOAI_PHONG(
            MaLoai, TenLoai, MoTa, DienTich, SoNguoiToiDa
        )
        VALUES (
            UUID(), p_TenLoai, p_MoTa, p_DienTich, p_SoNguoiToiDa
        );
    END IF;
END$$

DELIMITER ;

-- SỬA LOAI_PHONG

DROP PROCEDURE IF EXISTS sp_sua_loai_phong;

DELIMITER $$

CREATE PROCEDURE sp_sua_loai_phong(
    IN p_MaLoai CHAR(36),
    IN p_TenLoai VARCHAR(100),
    IN p_MoTa VARCHAR(255),
    IN p_DienTich DECIMAL(10,2),
    IN p_SoNguoiToiDa INT
)
BEGIN
    UPDATE LOAI_PHONG
    SET
        TenLoai = p_TenLoai,
        MoTa = p_MoTa,
        DienTich = p_DienTich,
        SoNguoiToiDa = p_SoNguoiToiDa
    WHERE MaLoai = p_MaLoai;
END$$

DELIMITER ;

-- XOA LOAI_PHONG
DROP PROCEDURE IF EXISTS sp_xoa_loai_phong;

DELIMITER $$

CREATE PROCEDURE sp_xoa_loai_phong(
    IN p_MaLoai CHAR(36)
)
BEGIN
    DECLARE v_count_phong INT;
    DECLARE v_count_gia INT;

    SELECT COUNT(*)
    INTO v_count_phong
    FROM PHONG
    WHERE MaLoai = p_MaLoai;

    SELECT COUNT(*)
    INTO v_count_gia
    FROM BANG_GIA
    WHERE MaLoai = p_MaLoai;

    IF v_count_phong > 0 OR v_count_gia > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Không thể xoá: Loại phòng đang được sử dụng';
    ELSE
        DELETE FROM LOAI_PHONG WHERE MaLoai = p_MaLoai;
    END IF;
END$$

DELIMITER ;

-- DANH SACH LOAI_PHONG
DROP PROCEDURE IF EXISTS sp_ds_loai_phong;

DELIMITER $$

CREATE PROCEDURE sp_ds_loai_phong()
BEGIN
    SELECT * FROM LOAI_PHONG;
END$$

DELIMITER ;



-- Thêm XE
DROP PROCEDURE IF EXISTS sp_them_xe;

DELIMITER $$

CREATE PROCEDURE sp_them_xe(
    IN p_BienSo VARCHAR(15),
    IN p_MauXe VARCHAR(15),
    IN p_HieuXe VARCHAR(15)
)
BEGIN
    -- Kiểm tra trùng biển số
    IF EXISTS (SELECT 1 FROM XE WHERE BienSo = p_BienSo) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Biển số xe đã tồn tại';
    ELSE
        INSERT INTO XE(BienSo, MauXe, HieuXe)
        VALUES (p_BienSo, p_MauXe, p_HieuXe);
    END IF;
END$$

DELIMITER ;

-- SỬA XE
DROP PROCEDURE IF EXISTS sp_sua_xe;

DELIMITER $$

CREATE PROCEDURE sp_sua_xe(
    IN p_BienSo VARCHAR(15),
    IN p_MauXe VARCHAR(15),
    IN p_HieuXe VARCHAR(15)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM XE WHERE BienSo = p_BienSo) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Không tìm thấy xe để cập nhật';
    ELSE
        UPDATE XE
        SET 
            MauXe = p_MauXe,
            HieuXe = p_HieuXe
        WHERE BienSo = p_BienSo;
    END IF;
END$$

DELIMITER ;


-- DS XE
DROP PROCEDURE IF EXISTS sp_xe_xem_all;

DELIMITER $$

CREATE PROCEDURE sp_xe_xem_all()
BEGIN
    SELECT * FROM XE;
END$$

DELIMITER ;

-- Xoa Xe
DROP PROCEDURE IF EXISTS sp_xe_xoa;

DELIMITER $$

CREATE PROCEDURE sp_xe_xoa(
    IN p_BienSo VARCHAR(15)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM XE WHERE BienSo = p_BienSo) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Không tìm thấy xe để xóa';
    ELSE
        DELETE FROM XE
        WHERE BienSo = p_BienSo;
    END IF;
END$$

DELIMITER ;


-- THEM HOP DONG
-- DROP PROCEDURE IF EXISTS sp_hd_them;
-- DELIMITER $$

-- CREATE PROCEDURE sp_hd_them(
--     IN p_NgayKy DATE,
--     IN p_NgayBatDau DATE,
--     IN p_NgayKetThuc DATE,
--     IN p_LoaiBlock VARCHAR(20),
--     IN p_DonGia DECIMAL(18,2),
--     IN p_MSV VARCHAR(36),
--     IN p_MaPhong VARCHAR(20),
--     IN p_MaKTX INT
-- )
-- BEGIN
--     DECLARE v_MaHD CHAR(36);
--     DECLARE v_SoNguoiHienTai INT;
--     DECLARE v_SoNguoiToiDa INT;
--     DECLARE v_MaLoai CHAR(36);

--     START TRANSACTION;

--     -- 1. Kiểm tra sinh viên tồn tại
--     IF NOT EXISTS (
--         SELECT 1 FROM SINH_VIEN WHERE MSV = p_MSV
--     ) THEN
--         ROLLBACK;
--         SIGNAL SQLSTATE '45000'
--         SET MESSAGE_TEXT = 'Sinh viên không tồn tại';

--     -- 2. Kiểm tra phòng tồn tại
--     ELSEIF NOT EXISTS (
--         SELECT 1 FROM PHONG
--         WHERE MaPhong = p_MaPhong
--           AND MaKTX   = p_MaKTX
--     ) THEN
--         ROLLBACK;
--         SIGNAL SQLSTATE '45000'
--         SET MESSAGE_TEXT = 'Phòng không tồn tại';

--     -- 3. Lấy MaLoai + số người hiện tại + số người tối đa
--     ELSE
--         SELECT 
--             IFNULL(p.SoNguoiHienTai, 0),
--             lp.SoNguoiToiDa,
--             p.MaLoai
--         INTO v_SoNguoiHienTai, v_SoNguoiToiDa, v_MaLoai
--         FROM PHONG p
--         JOIN LOAI_PHONG lp ON p.MaLoai = lp.MaLoai
--         WHERE p.MaPhong = p_MaPhong
--           AND p.MaKTX   = p_MaKTX
--         FOR UPDATE;
--     END IF;

--     -- 4. Kiểm tra phòng còn chỗ trống
--     IF v_SoNguoiHienTai >= v_SoNguoiToiDa THEN
--         ROLLBACK;
--         SIGNAL SQLSTATE '45000'
--         SET MESSAGE_TEXT = 'Phòng đã đủ số người tối đa';

--     -- 5. Kiểm tra sinh viên đã có hợp đồng còn hiệu lực
--     ELSEIF EXISTS (
--         SELECT 1
--         FROM HOP_DONG
--         WHERE MSV = p_MSV
--           AND NgayKetThuc >= CURDATE()
--     ) THEN
--         ROLLBACK;
--         SIGNAL SQLSTATE '45000'
--         SET MESSAGE_TEXT = 'Sinh viên đã có hợp đồng còn hiệu lực';

--     ELSE
--         -- 6. Sinh mã hợp đồng
--         SET v_MaHD = UUID();

--         -- 7. Insert hợp đồng
--         INSERT INTO HOP_DONG (
--             MaHD, NgayKy, NgayBatDau, NgayKetThuc,
--             LoaiBlock, DonGia,
--             MSV, MaPhong, MaKTX
--         )
--         VALUES (
--             v_MaHD, p_NgayKy, p_NgayBatDau, p_NgayKetThuc,
--             p_LoaiBlock, p_DonGia,
--             p_MSV, p_MaPhong, p_MaKTX
--         );

--         -- 8. Cập nhật số người hiện tại
--         UPDATE PHONG
--         SET SoNguoiHienTai = v_SoNguoiHienTai + 1
--         WHERE MaPhong = p_MaPhong
--           AND MaKTX   = p_MaKTX;

--         -- 9. Tạo hóa đơn tiền phòng
--         INSERT INTO HOA_DON_TIEN_PHONG (
--             MaHoaDon,
--             NgayXuat,
--             HanThanhToan,
--             TrangThaiTT,
--             MaHD
--         )
--         VALUES (
--             UUID(),
--             p_NgayBatDau,
--             LAST_DAY(DATE_ADD(p_NgayBatDau, INTERVAL 1 MONTH)),
--             0,
--             v_MaHD
--         );

--         COMMIT;
--     END IF;
-- END$$

-- DELIMITER ;
DROP PROCEDURE IF EXISTS sp_hd_them;
DELIMITER $$

CREATE PROCEDURE sp_hd_them(
    IN p_NgayKy DATE,
    IN p_NgayBatDau DATE,
    IN p_NgayKetThuc DATE,
    IN p_LoaiBlock VARCHAR(20),   -- VD: '10' hoặc 'CHAN_THANG'
    IN p_DonGia DECIMAL(18,2),
    IN p_MSV VARCHAR(36),
    IN p_MaPhong VARCHAR(20),
    IN p_MaKTX INT
)
BEGIN
    DECLARE v_MaHD CHAR(36);
    DECLARE v_SoNguoiHienTai INT;
    DECLARE v_SoNguoiToiDa INT;
    DECLARE v_MaLoai CHAR(36);

    DECLARE v_TuNgay DATE;
    DECLARE v_DenNgay DATE;
    DECLARE v_BlockNgay INT;

    START TRANSACTION;

    -- 1. Kiểm tra sinh viên
    IF NOT EXISTS (SELECT 1 FROM SINH_VIEN WHERE MSV = p_MSV) THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Sinh viên không tồn tại';

    -- 2. Kiểm tra phòng
    ELSEIF NOT EXISTS (
        SELECT 1 FROM PHONG
        WHERE MaPhong = p_MaPhong AND MaKTX = p_MaKTX
    ) THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Phòng không tồn tại';

    ELSE
        -- 3. Lấy thông tin phòng
        SELECT 
            IFNULL(p.SoNguoiHienTai, 0),
            lp.SoNguoiToiDa,
            p.MaLoai
        INTO v_SoNguoiHienTai, v_SoNguoiToiDa, v_MaLoai
        FROM PHONG p
        JOIN LOAI_PHONG lp ON p.MaLoai = lp.MaLoai
        WHERE p.MaPhong = p_MaPhong
          AND p.MaKTX   = p_MaKTX
        FOR UPDATE;
    END IF;

    -- 4. Check số người
    IF v_SoNguoiHienTai >= v_SoNguoiToiDa THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Phòng đã đủ số người';

    -- 5. Check hợp đồng còn hiệu lực
    ELSEIF EXISTS (
    SELECT 1
    FROM HOP_DONG hd
    WHERE hd.MSV = p_MSV
      AND p_NgayBatDau <= hd.NgayKetThuc
) THEN
    ROLLBACK;
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Sinh viên có hợp đồng còn hiệu lực';

    ELSE
        -- 6. Tạo hợp đồng
        SET v_MaHD = UUID();

        INSERT INTO HOP_DONG (
            MaHD, NgayKy, NgayBatDau, NgayKetThuc,
            LoaiBlock, DonGia,
            MSV, MaPhong, MaKTX
        )
        VALUES (
            v_MaHD, p_NgayKy, p_NgayBatDau, p_NgayKetThuc,
            p_LoaiBlock, p_DonGia,
            p_MSV, p_MaPhong, p_MaKTX
        );

        -- 7. Update số người
        UPDATE PHONG
        SET SoNguoiHienTai = v_SoNguoiHienTai + 1
        WHERE MaPhong = p_MaPhong
          AND MaKTX   = p_MaKTX;

        -- ==============================
        -- 8. SINH HÓA ĐƠN
        -- ==============================
        SET v_TuNgay = p_NgayBatDau;

        -- BLOCK THEO THÁNG
        IF p_LoaiBlock = 'chẵn tháng' THEN

            WHILE v_TuNgay < p_NgayKetThuc DO
                SET v_DenNgay = LAST_DAY(v_TuNgay);

                IF v_DenNgay > p_NgayKetThuc THEN
                    SET v_DenNgay = p_NgayKetThuc;
                END IF;

                INSERT INTO HOA_DON_TIEN_PHONG (
                    MaHoaDon, NgayBatDau, NgayKetThuc, TrangThaiTT, MaHD
                )
                VALUES (
                    UUID(),
                    v_TuNgay,
                    v_DenNgay,
                    0,
                    v_MaHD
                );

                SET v_TuNgay = DATE_ADD(LAST_DAY(v_TuNgay), INTERVAL 1 DAY);
            END WHILE;

        -- BLOCK THEO NGÀY (VD: 10)
        ELSE
            SET v_BlockNgay = CAST(p_LoaiBlock AS UNSIGNED);

            WHILE v_TuNgay < p_NgayKetThuc DO
                SET v_DenNgay = DATE_ADD(v_TuNgay, INTERVAL v_BlockNgay DAY);

                IF v_DenNgay > p_NgayKetThuc THEN
                    SET v_DenNgay = p_NgayKetThuc;
                END IF;

                INSERT INTO HOA_DON_TIEN_PHONG (
                    MaHoaDon, NgayBatDau,NgayKetThuc, TrangThaiTT, MaHD
                )
                VALUES (
                    UUID(),
                    v_TuNgay,
                    v_DenNgay,
                    0,
                    v_MaHD
                );

                SET v_TuNgay = DATE_ADD(v_TuNgay, INTERVAL v_BlockNgay DAY);
            END WHILE;
        END IF;

        COMMIT;
    END IF;
END$$
DELIMITER ;



-- XEM HOP DONG
DROP PROCEDURE IF EXISTS sp_hd_xem_all;

DELIMITER $$
CREATE PROCEDURE sp_hd_xem_all()
BEGIN
    SELECT 
        hd.MaHD,
        hd.NgayKy,
        hd.NgayBatDau,
        hd.NgayKetThuc,
        hd.LoaiBlock,
        hd.DonGia,

        -- Trạng thái tính động
        CASE
            WHEN hd.NgayKetThuc >= CURDATE() THEN 'Đang hiệu lực'
            ELSE 'Hết hạn'
        END AS TrangThai,

        hd.MSV,
        sv.HoTen,
        hd.MaPhong,
        k.Ten AS TenKTX
    FROM HOP_DONG hd
    JOIN SINH_VIEN sv ON hd.MSV = sv.MSV
    JOIN KTX k ON hd.MaKTX = k.MaKTX
    ORDER BY hd.NgayKy DESC;
END$$
DELIMITER ;


-- UPDATE HOP DONG
DROP PROCEDURE IF EXISTS sp_hd_sua;

DELIMITER $$

CREATE PROCEDURE sp_hd_sua(
    IN p_MaHD CHAR(36),
    IN p_NgayBatDau DATE,
    IN p_NgayKetThuc DATE,
    IN p_LoaiBlock VARCHAR(20),
    IN p_DonGia DECIMAL(18,2)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM HOP_DONG WHERE MaHD = p_MaHD) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Không tìm thấy hợp đồng';
    ELSE
        UPDATE HOP_DONG
        SET
            NgayBatDau = p_NgayBatDau,
            NgayKetThuc = p_NgayKetThuc,
            LoaiBlock = p_LoaiBlock,
            DonGia = p_DonGia
        WHERE MaHD = p_MaHD;
    END IF;
END$$

DELIMITER ;

-- XOA HOP DONG
DROP PROCEDURE IF EXISTS sp_hd_xoa;

DELIMITER $$

CREATE PROCEDURE sp_hd_xoa(
    IN p_MaHD CHAR(36)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM HOP_DONG WHERE MaHD = p_MaHD) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Không tìm thấy hợp đồng để xóa';
    ELSE
        DELETE FROM HOP_DONG
        WHERE MaHD = p_MaHD;
    END IF;
END$$

DELIMITER ;


-- HOA DON DICH VU
DROP PROCEDURE IF EXISTS get_hoa_don_dich_vu;

DELIMITER $$

CREATE PROCEDURE get_hoa_don_dich_vu()
BEGIN
    SELECT
        hd.MaHoaDon,
        DATE_FORMAT(hd.Thang_Nam, '%Y-%m') AS Thang_Nam,
        hd.TrangThaiTT,
        sv.MSV,
        sv.HoTen,
        COALESCE(SUM(
            CASE 
                WHEN vx.TrangThaiTT = FALSE THEN vx.GiaVe
                ELSE 0
            END
        ), 0) AS TongTien
    FROM HOA_DON_DICH_VU hd
    LEFT JOIN SINH_VIEN sv 
        ON SUBSTRING(hd.MaHoaDon, 6) = sv.MSV
    LEFT JOIN VE_XE vx 
        ON hd.MaHoaDon = vx.MaHoaDon
    GROUP BY
        hd.MaHoaDon,
        hd.Thang_Nam,
        hd.TrangThaiTT,
        sv.MSV,
        sv.HoTen
    ORDER BY hd.Thang_Nam DESC;
END$$

DELIMITER ;


-- THEM BANG_GIA
DROP PROCEDURE IF EXISTS sp_add_bang_gia;

DELIMITER $$

CREATE PROCEDURE sp_add_bang_gia(
    IN p_MaLoai CHAR(36),
    IN p_LoaiBlock VARCHAR(20),
    IN p_DonGia DECIMAL(18,2)
)
BEGIN
    -- 1. Validate loại phòng tồn tại
    IF NOT EXISTS (
        SELECT 1 FROM LOAI_PHONG WHERE MaLoai = p_MaLoai
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Loai phong khong ton tai';
    END IF;
    
    -- 3. Validate đơn giá
    IF p_DonGia <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Don gia phai lon hon 0';
    END IF;

    -- 4. Không cho trùng khóa chính
    IF EXISTS (
        SELECT 1 FROM BANG_GIA
        WHERE MaLoai = p_MaLoai
          AND LoaiBlock = p_LoaiBlock
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Bang gia da ton tai';
    END IF;

    -- 5. Insert
    INSERT INTO BANG_GIA(MaLoai, LoaiBlock, DonGia)
    VALUES (p_MaLoai, p_LoaiBlock, p_DonGia);
END $$

DELIMITER ;


-- Get ds bảng giá
DROP PROCEDURE IF EXISTS sp_get_all_bang_gia;

DELIMITER $$

CREATE PROCEDURE sp_get_all_bang_gia()
BEGIN
    SELECT 
        bg.MaLoai,
        lp.TenLoai,
        bg.LoaiBlock,
        bg.DonGia,
        lp.DienTich,
        lp.SoNguoiToiDa
    FROM BANG_GIA bg
    JOIN LOAI_PHONG lp ON bg.MaLoai = lp.MaLoai
    ORDER BY lp.TenLoai, bg.LoaiBlock;
END $$

DELIMITER ;


-- UPDATE BANG_GIA
DROP PROCEDURE IF EXISTS sp_update_bang_gia;

DELIMITER $$

CREATE PROCEDURE sp_update_bang_gia(
    IN p_MaLoai CHAR(36),
    IN p_LoaiBlock INT,
    IN p_DonGia DECIMAL(18,2)
)
BEGIN
    -- 1. Validate bản ghi tồn tại
    IF NOT EXISTS (
        SELECT 1 FROM BANG_GIA
        WHERE MaLoai = p_MaLoai
          AND LoaiBlock = p_LoaiBlock
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Bang gia khong ton tai';
    END IF;

    -- 2. Validate đơn giá
    IF p_DonGia <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Don gia phai lon hon 0';
    END IF;

    -- 3. Update
    UPDATE BANG_GIA
    SET DonGia = p_DonGia
    WHERE MaLoai = p_MaLoai
      AND LoaiBlock = p_LoaiBlock;
END $$

DELIMITER ;

-- XOA BANG_GIA
DROP PROCEDURE IF EXISTS sp_delete_bang_gia;

DELIMITER $$

CREATE PROCEDURE sp_delete_bang_gia(
    IN p_MaLoai CHAR(36),
    IN p_LoaiBlock INT
)
BEGIN
    -- Validate tồn tại
    IF NOT EXISTS (
        SELECT 1 FROM BANG_GIA
        WHERE MaLoai = p_MaLoai
          AND LoaiBlock = p_LoaiBlock
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Bang gia khong ton tai';
    END IF;

    DELETE FROM BANG_GIA
    WHERE MaLoai = p_MaLoai
      AND LoaiBlock = p_LoaiBlock;
END $$

DELIMITER ;


-- -- get_ds_hoa_don_tien_phong
-- DROP PROCEDURE IF EXISTS sp_hd_tien_phong_danhsach;
-- DELIMITER $$

-- CREATE PROCEDURE sp_hd_tien_phong_danhsach()
-- BEGIN
--     SELECT
--         hd.MaHD,
--         sv.MSV,
--         sv.HoTen,
--         hd.MaPhong,
--         ktx.Ten AS TenKTX,
--         hd.NgayBatDau,
--         hd.NgayKetThuc,
--         hd.LoaiBlock,
--         hd.DonGia,

--         /* ===== TÍNH TỔNG TIỀN ===== */
--         CASE
--             -- Block ngày: 10 / 20
--             WHEN hd.LoaiBlock IN ('10', '20') THEN
--                 CEILING(
--                     DATEDIFF(hd.NgayKetThuc, hd.NgayBatDau) * 1.0
--                     / CAST(hd.LoaiBlock AS UNSIGNED)
--                 ) * hd.DonGia

--             -- Block chẵn tháng
--             WHEN hd.LoaiBlock = 'chẵn tháng' THEN
--                 (
--                     TIMESTAMPDIFF(
--                         MONTH,
--                         DATE_FORMAT(hd.NgayBatDau, '%Y-%m-01'),
--                         DATE_FORMAT(hd.NgayKetThuc, '%Y-%m-01')
--                     ) + 1
--                 ) * hd.DonGia

--             ELSE 0
--         END AS TongTien,

--         hdtp.MaHoaDon,
--         hdtp.NgayXuat,
--         hdtp.HanThanhToan,
--         hdtp.TrangThaiTT

--     FROM HOP_DONG hd
--     JOIN HOA_DON_TIEN_PHONG hdtp
--         ON hd.MaHD = hdtp.MaHD
--     JOIN SINH_VIEN sv
--         ON hd.MSV = sv.MSV
--     JOIN PHONG p
--         ON hd.MaPhong = p.MaPhong
--        AND hd.MaKTX   = p.MaKTX
--     JOIN KTX ktx
--         ON p.MaKTX = ktx.MaKTX
--     ORDER BY hdtp.HanThanhToan DESC;
-- END$$

-- DELIMITER ;
DROP PROCEDURE IF EXISTS sp_hd_tien_phong_danhsach;
DELIMITER $$

CREATE PROCEDURE sp_hd_tien_phong_danhsach()
BEGIN
    SELECT
        hd.MaHD,
        sv.MSV,
        sv.HoTen,
        hd.MaPhong,
        ktx.Ten AS TenKTX,
        hdtp.NgayBatDau   AS NgayBatDau,
        hd.NgayKetThuc  AS NgayKetThuc,
        hd.LoaiBlock,
        hd.DonGia,
        hdtp.MaHoaDon,
        hdtp.TrangThaiTT
    FROM HOA_DON_TIEN_PHONG hdtp
    JOIN HOP_DONG hd
        ON hdtp.MaHD = hd.MaHD
    JOIN SINH_VIEN sv
        ON hd.MSV = sv.MSV
    JOIN PHONG p
        ON hd.MaPhong = p.MaPhong
       AND hd.MaKTX   = p.MaKTX
    JOIN KTX ktx
        ON p.MaKTX = ktx.MaKTX;
END$$

DELIMITER ;

-- Sửa hop_don_tien_phong

DROP PROCEDURE IF EXISTS sp_sua_trang_thai_hoa_don;
DELIMITER $$
CREATE PROCEDURE sp_sua_trang_thai_hoa_don(
    IN p_MaHoaDon CHAR(36),
    IN p_TrangThaiTT VARCHAR(50)
)
BEGIN
    UPDATE HOA_DON_TIEN_PHONG
    SET TrangThaiTT = p_TrangThaiTT
    WHERE MaHoaDon = p_MaHoaDon;
END$$
DELIMITER ;




-- THEM SU_DUNG_DICH_VU
DROP PROCEDURE IF EXISTS sp_them_su_dung_dich_vu;
DELIMITER $$

CREATE PROCEDURE sp_them_su_dung_dich_vu(
    IN p_MSV VARCHAR(36),
    IN p_MADV CHAR(36),
    IN p_SoLuong INT,
    IN p_NgaySuDung DATE
)
BEGIN
    DECLARE v_MaHoaDon VARCHAR(50);
    DECLARE v_YYMM VARCHAR(4);

    START TRANSACTION;

    -- Validate
    IF p_SoLuong <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Số lượng phải > 0';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM SINH_VIEN WHERE MSV = p_MSV) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Sinh viên không tồn tại';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM DICH_VU WHERE MADV = p_MADV) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Dịch vụ không tồn tại';
    END IF;

    -- Tạo MaHoaDon: YYMM_MSV
    SET v_YYMM = DATE_FORMAT(p_NgaySuDung, '%y%m');
    SET v_MaHoaDon = CONCAT(v_YYMM, '_', p_MSV);

    -- Nếu chưa có hóa đơn dịch vụ tháng đó → tạo mới
    IF NOT EXISTS (
        SELECT 1 FROM HOA_DON_DICH_VU WHERE MaHoaDon = v_MaHoaDon
    ) THEN
        INSERT INTO HOA_DON_DICH_VU (
            MaHoaDon,
            Thang_Nam,
            TrangThaiTT
        )
        VALUES (
            v_MaHoaDon,
            DATE_FORMAT(p_NgaySuDung, '%Y-%m-01'),
            0
        );
    END IF;

    -- Thêm sử dụng dịch vụ
    INSERT INTO SU_DUNG_DICH_VU (
        MASD, SoLuong, MSV, MADV, MaHoaDon
    )
    VALUES (
        UUID(), p_SoLuong, p_MSV, p_MADV, v_MaHoaDon
    );

    COMMIT;
END$$

DELIMITER ;


-- SỬA SU_DUNG_DICH_VU
DROP PROCEDURE IF EXISTS sp_sua_su_dung_dich_vu;
DELIMITER $$

CREATE PROCEDURE sp_sua_su_dung_dich_vu(
    IN p_MASD CHAR(36),
    IN p_SoLuong INT
)
BEGIN
    IF p_SoLuong <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Số lượng phải > 0';
    END IF;

    UPDATE SU_DUNG_DICH_VU
    SET SoLuong = p_SoLuong
    WHERE MASD = p_MASD;
END$$

DELIMITER ;

-- XOA SU_DUNG_DICH_VU
DROP PROCEDURE IF EXISTS sp_xoa_su_dung_dich_vu;
DELIMITER $$

CREATE PROCEDURE sp_xoa_su_dung_dich_vu(
    IN p_MASD CHAR(36)
)
BEGIN
    DECLARE v_MaHoaDon VARCHAR(50);

    SELECT MaHoaDon
    INTO v_MaHoaDon
    FROM SU_DUNG_DICH_VU
    WHERE MASD = p_MASD;

    DELETE FROM SU_DUNG_DICH_VU WHERE MASD = p_MASD;

    -- Nếu hóa đơn không còn dịch vụ nào → xoá luôn
    IF NOT EXISTS (
        SELECT 1 FROM SU_DUNG_DICH_VU WHERE MaHoaDon = v_MaHoaDon
    ) THEN
        DELETE FROM HOA_DON_DICH_VU WHERE MaHoaDon = v_MaHoaDon;
    END IF;
END$$

DELIMITER ;


-- XEM SU_DUNG_DICH_VU
DROP PROCEDURE IF EXISTS sp_ds_su_dung_dich_vu;
DELIMITER $$

CREATE PROCEDURE sp_ds_su_dung_dich_vu()
BEGIN
    SELECT
        sd.MASD,
        sv.MSV,
        sv.HoTen,
        dv.TenDV,
        sd.SoLuong,
        dv.DonGia,
        (sd.SoLuong * dv.DonGia) AS ThanhTien,
        sd.MaHoaDon,
        hddv.Thang_Nam,
        hddv.TrangThaiTT
    FROM SU_DUNG_DICH_VU sd
    JOIN SINH_VIEN sv ON sd.MSV = sv.MSV
    JOIN DICH_VU dv ON sd.MADV = dv.MADV
    JOIN HOA_DON_DICH_VU hddv ON sd.MaHoaDon = hddv.MaHoaDon
    ORDER BY hddv.Thang_Nam DESC;
END$$

DELIMITER ;

-- TONG HOA DON THEO THANG 
DROP PROCEDURE IF EXISTS sp_tong_hoa_don_chua_tt_theo_thang_all_sv;
DELIMITER $$

CREATE PROCEDURE sp_tong_hoa_don_chua_tt_theo_thang_all_sv ()
BEGIN
    SELECT
        MSV,
        HoTen,
        ThangNam,
        SUM(TienPhong)  AS TongTienPhong,
        SUM(TienDichVu) AS TongTienDichVu,
        SUM(TienPhong + TienDichVu) AS TongTienPhaiTra
    FROM (

        /* ================= TIỀN PHÒNG ================= */
        SELECT
            sv.MSV,
            sv.HoTen,
            DATE_FORMAT(hdp.NgayKetThuc, '%m%Y') AS ThangNam,
            hd.DonGia AS TienPhong,
            0 AS TienDichVu
        FROM HOA_DON_TIEN_PHONG hdp
        JOIN HOP_DONG hd ON hdp.MaHD = hd.MaHD
        JOIN SINH_VIEN sv ON hd.MSV = sv.MSV
        WHERE hdp.TrangThaiTT = FALSE

        UNION ALL

        /* ========== DỊCH VỤ THƯỜNG ========== */
        SELECT
            sv.MSV,
            sv.HoTen,
            DATE_FORMAT(hddv.Thang_Nam, '%m%Y') AS ThangNam,
            0 AS TienPhong,
            SUM(sddv.SoLuong * dv.DonGia) AS TienDichVu
        FROM HOA_DON_DICH_VU hddv
        JOIN SU_DUNG_DICH_VU sddv
             ON hddv.MaHoaDon = sddv.MaHoaDon
        JOIN DICH_VU dv
             ON sddv.MADV = dv.MADV
        JOIN SINH_VIEN sv
             ON sv.MSV = sddv.MSV
        WHERE hddv.TrangThaiTT = FALSE
        GROUP BY sv.MSV, sv.HoTen, hddv.Thang_Nam

        UNION ALL

        /* ========== VÉ XE (CHƯA THANH TOÁN) ========== */
        SELECT
            sv.MSV,
            sv.HoTen,
            DATE_FORMAT(hddv.Thang_Nam, '%m%Y') AS ThangNam,
            0 AS TienPhong,
            SUM(vx.GiaVe) AS TienDichVu
        FROM HOA_DON_DICH_VU hddv
        JOIN VE_XE vx
             ON hddv.MaHoaDon = vx.MaHoaDon
            AND vx.TrangThaiTT = FALSE   
        JOIN SINH_VIEN sv
             ON sv.MSV = SUBSTRING_INDEX(hddv.MaHoaDon, '_', -1)
        WHERE hddv.TrangThaiTT = FALSE
        GROUP BY sv.MSV, sv.HoTen, hddv.Thang_Nam

    ) T
    GROUP BY MSV, HoTen, ThangNam
    ORDER BY STR_TO_DATE(ThangNam, '%m%Y'), MSV;
END $$

DELIMITER ;



-- HOA DON_CHI TIET THEO THANG CUA TUNG SINH VIEN
DROP PROCEDURE IF EXISTS sp_chi_tiet_hoa_don_chua_tt;
DELIMITER $$

CREATE PROCEDURE sp_chi_tiet_hoa_don_chua_tt (
    IN p_MSV VARCHAR(36),
    IN p_ThangNam VARCHAR(6)   -- MMYYYY (VD: 022026)
)
BEGIN
    /* ============================
       1. TIỀN PHÒNG
       ============================ */
    SELECT
        'TIEN_PHONG'           AS LoaiHoaDon,
        'Tiền phòng'           AS MoTa,
        hdp.NgayBatDau         AS TuNgay,
        hdp.NgayKetThuc        AS DenNgay,
        hd.DonGia              AS SoTien
    FROM HOA_DON_TIEN_PHONG hdp
    JOIN HOP_DONG hd ON hdp.MaHD = hd.MaHD
    WHERE
        hd.MSV = p_MSV
        AND hdp.TrangThaiTT = FALSE
        AND DATE_FORMAT(hdp.NgayKetThuc, '%m%Y') = p_ThangNam

    UNION ALL

    /* ============================
       2. DỊCH VỤ THƯỜNG
       ============================ */
    SELECT
        'DICH_VU'                                  AS LoaiHoaDon,
        dv.TenDV                                  AS MoTa,
        NULL                                      AS TuNgay,
        NULL                                      AS DenNgay,
        SUM(sddv.SoLuong * dv.DonGia)             AS SoTien
    FROM HOA_DON_DICH_VU hddv
    JOIN SU_DUNG_DICH_VU sddv ON hddv.MaHoaDon = sddv.MaHoaDon
    JOIN DICH_VU dv ON sddv.MADV = dv.MADV
    WHERE
        hddv.TrangThaiTT = FALSE
        AND sddv.MSV = p_MSV
        AND DATE_FORMAT(hddv.Thang_Nam, '%m%Y') = p_ThangNam
    GROUP BY dv.TenDV

    UNION ALL

    /* ============================
       3. VÉ THÁNG
       ============================ */
    SELECT
        'VE_XE_THANG'                        AS LoaiHoaDon,
        CONCAT('Vé tháng ', vt.Thang, '/', vt.Nam) AS MoTa,
        NULL                                 AS TuNgay,
        NULL                                 AS DenNgay,
        vx.GiaVe                             AS SoTien
    FROM HOA_DON_DICH_VU hddv
    JOIN VE_XE vx ON hddv.MaHoaDon = vx.MaHoaDon
    JOIN VE_THANG vt ON vx.MaVe = vt.MaVe
    WHERE
        hddv.TrangThaiTT = FALSE
        AND vx.TrangThaiTT = FALSE
        AND vt.MSV = p_MSV
        AND LPAD(vt.Thang, 2, '0') = LEFT(p_ThangNam, 2)
        AND vt.Nam = RIGHT(p_ThangNam, 4)

    UNION ALL

    /* ============================
       4. VÉ LƯỢT
       ============================ */
    SELECT
        'VE_XE_LUOT'                        AS LoaiHoaDon,
        'Vé lượt'                           AS MoTa,
        vl.ThoiGianVao                      AS TuNgay,
        vl.ThoiGianRa                       AS DenNgay,
        vx.GiaVe                            AS SoTien
    FROM HOA_DON_DICH_VU hddv
    JOIN VE_XE vx ON hddv.MaHoaDon = vx.MaHoaDon
    JOIN VE_LUOT vl ON vx.MaVe = vl.MaVe
    WHERE
        hddv.TrangThaiTT = FALSE
        AND vx.TrangThaiTT = FALSE
        AND vl.MSV = p_MSV
        AND vl.ThoiGianRa IS NOT NULL
        AND DATE_FORMAT(vl.ThoiGianRa, '%m%Y') = p_ThangNam

    ORDER BY LoaiHoaDon, MoTa;
END$$
DELIMITER ;
