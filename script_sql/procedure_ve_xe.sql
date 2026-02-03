use BTL_CSDL;

DROP PROCEDURE IF EXISTS sp_dang_ky_ve_thang;

DELIMITER $$
CREATE PROCEDURE sp_dang_ky_ve_thang(
    IN p_MSV VARCHAR(36),
    IN p_BienSo VARCHAR(15),
    IN p_Thang INT,
    IN p_Nam INT
)
BEGIN
    DECLARE v_count_sv INT;
    DECLARE v_count_xe INT;
    DECLARE v_MaVe CHAR(36);
    DECLARE v_MaHoaDon VARCHAR(50);
    DECLARE v_count_hd INT;

    -- 1. Kiểm tra xe đã có vé tháng chưa
    SELECT COUNT(*)
    INTO v_count_xe
    FROM VE_THANG
    WHERE BienSo = p_BienSo
      AND Thang = p_Thang
      AND NAM = p_Nam;

    IF v_count_xe > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Xe đã được đăng ký vé tháng';
    END IF;

    -- 2. Kiểm tra số vé tháng của sinh viên
    SELECT COUNT(*)
    INTO v_count_sv
    FROM VE_THANG
    WHERE MSV = p_MSV
      AND Thang = p_Thang
      AND NAM = p_Nam;

    IF v_count_sv >= 2 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Mỗi sinh viên chỉ được đăng ký tối đa 2 vé tháng';
    END IF;

    -- 3. Tạo mã hóa đơn (theo tháng hiện tại)
    SET v_MaHoaDon = CONCAT(DATE_FORMAT(NOW(), '%y%m'), '_', p_MSV);

    -- 4. Nếu chưa có hóa đơn thì tạo
    SELECT COUNT(*)
    INTO v_count_hd
    FROM HOA_DON_DICH_VU
    WHERE MaHoaDon = v_MaHoaDon;

    IF v_count_hd = 0 THEN
        INSERT INTO HOA_DON_DICH_VU (
            MaHoaDon,
            Thang_Nam,
            TrangThaiTT
        )
        VALUES (
            v_MaHoaDon,
            DATE_FORMAT(NOW(), '%Y-%m-01'),
            FALSE
        );
    END IF;

    -- 5. Tạo vé xe
    SET v_MaVe = UUID();
    INSERT INTO VE_XE(MaVe, GiaVe, TrangThaiTT, MaHoaDon)
    VALUES (v_MaVe, 100000, FALSE, v_MaHoaDon);

    -- 6. Tạo vé tháng
    INSERT INTO VE_THANG(MaVe, Thang, NAM, BienSo, MSV)
    VALUES (v_MaVe, p_Thang, p_Nam, p_BienSo, p_MSV);

    -- 7. Trả kết quả
    SELECT 
        v_MaVe AS MaVe,
        v_MaHoaDon AS MaHoaDon,
        'Đăng ký vé tháng thành công' AS ThongBao,
        100000 AS GiaVe;
END$$
DELIMITER ;


-- DANH SACH VE THANG
DROP PROCEDURE IF EXISTS sp_danh_sach_ve_thang;

DELIMITER $$

CREATE PROCEDURE sp_danh_sach_ve_thang()
BEGIN
    SELECT 
        vt.MaVe,
        vt.Thang,
        vt.Nam,
        vt.BienSo,
        sv.MSV,
        sv.HoTen,
        vx.GiaVe,
        CASE 
            WHEN vx.TrangThaiTT = 1 THEN 'Đã thanh toán'
            ELSE 'Chưa thanh toán'
        END AS TrangThai
    FROM VE_THANG vt
    JOIN VE_XE vx ON vt.MaVe = vx.MaVe
    JOIN SINH_VIEN sv ON vt.MSV = sv.MSV
    ORDER BY vt.Nam DESC, vt.Thang DESC;
END$$

DELIMITER ;


-- VELUOT
-- =====================================================
-- XÓA PROCEDURE NẾU ĐÃ TỒN TẠI
-- =====================================================
DROP PROCEDURE IF EXISTS sp_tao_ve_luot;

DELIMITER $$

CREATE PROCEDURE sp_tao_ve_luot(
    IN p_MSV VARCHAR(36),
    IN p_BienSo VARCHAR(15)
)
BEGIN
    DECLARE v_MaHoaDon VARCHAR(50);
    DECLARE v_MaVe CHAR(36);
    DECLARE v_XeDangGui INT DEFAULT 0;

    -- =====================================================
    -- 1. Kiểm tra xe đang gửi hay không
    -- =====================================================
    SELECT COUNT(*)
    INTO v_XeDangGui
    FROM VE_LUOT
    WHERE BienSoXe = p_BienSo
      AND ThoiGianRa IS NULL;

    IF v_XeDangGui > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Xe đang nằm trong bãi gửi xe';
    END IF;

    -- =====================================================
    -- 2. Tạo mã hóa đơn & mã vé
    -- =====================================================
    SET v_MaHoaDon = CONCAT(DATE_FORMAT(NOW(), '%y%m'), '_', p_MSV);
    SET v_MaVe = UUID();

    -- =====================================================
    -- 3. Tạo hóa đơn nếu chưa tồn tại
    -- =====================================================
    IF NOT EXISTS (
        SELECT 1 FROM HOA_DON_DICH_VU
        WHERE MaHoaDon = v_MaHoaDon
    ) THEN
        INSERT INTO HOA_DON_DICH_VU(
            MaHoaDon,
            Thang_Nam,
            TrangThaiTT
        )
        VALUES (
            v_MaHoaDon,
            NOW(),
            FALSE
        );
    END IF;

    -- =====================================================
    -- 4. Insert VE_XE
    -- =====================================================
    INSERT INTO VE_XE(
        MaVe,
        GiaVe,
        TrangThaiTT,
        MaHoaDon
    )
    VALUES (
        v_MaVe,
        0,
        FALSE,
        v_MaHoaDon
    );

    -- =====================================================
    -- 5. Insert VE_LUOT
    -- =====================================================
    INSERT INTO VE_LUOT(
        MaVe,
        BienSoXe,
        ThoiGianVao,
        ThoiGianRa,
        MSV
    )
    VALUES (
        v_MaVe,
        p_BienSo,
        NOW(),
        NULL,
        p_MSV
    );

    -- =====================================================
    -- 6. Trả kết quả
    -- =====================================================
    SELECT 
        v_MaVe AS MaVe,
        v_MaHoaDon AS MaHoaDon;

END$$

DELIMITER ;

-- UPDATE VE_LUOT
DROP PROCEDURE IF EXISTS sp_update_ve_luot;
DELIMITER $$

CREATE PROCEDURE sp_update_ve_luot(
    IN p_MaVe CHAR(36),
    IN p_TrangThaiTT BOOLEAN
)
BEGIN
    DECLARE v_BienSo VARCHAR(15);
    DECLARE v_GioVao DATETIME;
    DECLARE v_GioRa DATETIME;
    DECLARE v_Gia DECIMAL(18,2) DEFAULT 0;

    DECLARE v_CurDate DATE;
    DECLARE v_Start DATETIME;
    DECLARE v_End DATETIME;

    DECLARE v_IsVeThang INT DEFAULT 0;
    DECLARE v_LuotTrongNgay INT;

    -- Lấy thông tin vé
    SELECT BienSoXe, ThoiGianVao
    INTO v_BienSo, v_GioVao
    FROM VE_LUOT
    WHERE MaVe = p_MaVe;

    SET v_GioRa = NOW();
    SET v_CurDate = DATE(v_GioVao);

    -- =============================
    -- KIỂM TRA VÉ THÁNG
    -- =============================
    SELECT COUNT(*)
    INTO v_IsVeThang
    FROM VE_THANG
    WHERE BienSo = v_BienSo
      AND Thang = MONTH(v_GioRa)
      AND Nam = YEAR(v_GioRa);

    IF v_IsVeThang > 0 THEN
        -- Vé tháng: mỗi ngày >2 lượt thì 3000
        SELECT COUNT(*)
        INTO v_LuotTrongNgay
        FROM VE_LUOT
        WHERE BienSoXe = v_BienSo
          AND DATE(ThoiGianVao) = DATE(v_GioVao);

        IF v_LuotTrongNgay > 2 THEN
            SET v_Gia = 3000;
        ELSE
            SET v_Gia = 0;
        END IF;

    ELSE
        -- =============================
        -- VÉ LƯỢT – TÍNH THEO KHUNG GIỜ
        -- =============================
        WHILE v_CurDate <= DATE(v_GioRa) DO

            -- Ban ngày: 07:00 - 18:00
            SET v_Start = GREATEST(
                v_GioVao,
                CONCAT(v_CurDate, ' 07:00:00')
            );
            SET v_End = LEAST(
                v_GioRa,
                CONCAT(v_CurDate, ' 18:00:00')
            );

            IF v_Start < v_End THEN
                SET v_Gia = v_Gia + 5000;
            END IF;

            -- Ban đêm: 18:00 - 07:00 hôm sau
            SET v_Start = GREATEST(
                v_GioVao,
                CONCAT(v_CurDate, ' 18:00:00')
            );
            SET v_End = LEAST(
                v_GioRa,
                CONCAT(DATE_ADD(v_CurDate, INTERVAL 1 DAY), ' 07:00:00')
            );

            IF v_Start < v_End THEN
                SET v_Gia = v_Gia + 10000;
            END IF;

            SET v_CurDate = DATE_ADD(v_CurDate, INTERVAL 1 DAY);
        END WHILE;
    END IF;

    -- =============================
    -- UPDATE DATABASE
    -- =============================
    UPDATE VE_LUOT
    SET ThoiGianRa = v_GioRa
    WHERE MaVe = p_MaVe;

    UPDATE VE_XE
    SET GiaVe = v_Gia,
        TrangThaiTT = p_TrangThaiTT
    WHERE MaVe = p_MaVe;

    -- =============================
    -- TRẢ KẾT QUẢ
    -- =============================
    SELECT 
        v_Gia AS GiaVe,
        p_TrangThaiTT AS TrangThaiTT;

END$$
DELIMITER ;


-- Get danh sach xe dang gui

DELIMITER $$
DROP PROCEDURE IF EXISTS sp_ds_xe_dang_gui;

CREATE PROCEDURE sp_ds_xe_dang_gui()
BEGIN
    SELECT
        vl.MaVe,
        vl.BienSoXe,
        sv.HoTen,
        vl.ThoiGianVao
    FROM VE_LUOT AS vl
    INNER JOIN SINH_VIEN AS sv 
        ON vl.MSV = sv.MSV
    WHERE vl.ThoiGianRa IS NULL
    ORDER BY vl.ThoiGianVao DESC;
END$$

DELIMITER ;



-- Get danh sach ve xe
DROP PROCEDURE IF EXISTS sp_danh_sach_ve_xe;
DELIMITER $$

CREATE PROCEDURE sp_danh_sach_ve_xe()
BEGIN
    SELECT 
        vl.BienSoXe AS 'Biển Số',
        sv.HoTen AS 'Họ Tên',
        'Xe Máy' AS 'Loại Xe',
        vl.ThoiGianVao AS 'TG Vào',
        vl.ThoiGianRa AS 'TG Ra',
        CASE 
            WHEN vl.ThoiGianRa IS NULL THEN 'Đang gửi'
            ELSE 'Đã lấy'
        END AS 'Trạng Thái',
        CASE 
            WHEN vx.TrangThaiTT = 1 THEN 'Đã thanh toán'
            ELSE 'Chưa thanh toán'
        END AS 'Thanh Toán',
        vx.GiaVe AS 'Giá Vé',
        CASE
            WHEN EXISTS (
                SELECT 1 
                FROM VE_THANG vt 
                WHERE vt.BienSo = vl.BienSoXe
            ) THEN 'Vé tháng'
            ELSE 'Vé lượt'
        END AS 'Mô Tả Giá'
    FROM VE_LUOT vl
    JOIN VE_XE vx ON vl.MaVe = vx.MaVe
    JOIN SINH_VIEN sv ON vl.MSV = sv.MSV
    ORDER BY vl.ThoiGianVao DESC;
END$$

DELIMITER ;

