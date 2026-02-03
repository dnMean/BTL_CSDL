
-- Tạo database
CREATE DATABASE BTL_CSDL
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;



USE BTL_CSDL;

-- Bảng KTX
CREATE TABLE KTX (
    MaKTX INT AUTO_INCREMENT PRIMARY KEY,
    Ten VARCHAR(100),
    DiaChi VARCHAR(255),
    SoTang INT,
    SoPhong INT
);

-- Bảng LOAI_PHONG

CREATE TABLE LOAI_PHONG (
    MaLoai CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    MoTa VARCHAR(255),
    TenLoai VARCHAR(100),
    DienTich DECIMAL(10,2),
    SoNguoiToiDa INT
);

-- BẢNG BANG_GIA

CREATE TABLE BANG_GIA(
	MaLoai CHAR(36),
    LoaiBlock varchar(20),
    DonGia DECIMAL(18,2),
    PRIMARY KEY	(MaLoai, LoaiBlock),
    FOREIGN KEY (MaLoai) REFERENCES LOAI_PHONG(MaLoai)
);

-- BẢNG PHONG

CREATE TABLE PHONG (
    MaPhong VARCHAR(20),
    Tang INT,
    SoNguoiHienTai INT,
    MaLoai CHAR(36),
    MaKTX INT,
    PRIMARY KEY (MaPhong, MaKTX),
    FOREIGN KEY (MaLoai) REFERENCES LOAI_PHONG(MaLoai),
    FOREIGN KEY (MaKTX) REFERENCES KTX(MaKTX)
);

-- BẢNG SINH_VIEN
CREATE TABLE SINH_VIEN (
    MSV VARCHAR(36) PRIMARY KEY,
    HoTen VARCHAR(100),
    NgaySinh DATE,
    GioiTinh VARCHAR(10),
    CCCD VARCHAR(20),
    SDT VARCHAR(15)
);




-- BẢNG HOP_DONG
CREATE TABLE HOP_DONG (
    MaHD CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    NgayKy DATE,
    NgayBatDau DATE,
    NgayKetThuc DATE,
    LoaiBlock VARCHAR(20),
    DonGia DECIMAL(18,2),
    MSV VARCHAR(36),
    MaPhong VARCHAR(20),
    MaKTX INT,
    foreign key(MaPhong, MAKTX) references PHONG(MaPhong, MAKTX),
    FOREIGN KEY (MSV) REFERENCES SINH_VIEN(MSV)
);


-- BẢNG HOA_DON_TIEN_PHONG
CREATE TABLE HOA_DON_TIEN_PHONG (
    MaHoaDon CHAR(36) PRIMARY KEY  DEFAULT (UUID()),
    NgayBatDau DATE,
    NgayKetThuc DATE,
    TrangThaiTT boolean,
    MaHD CHAR(36),
    foreign key (MaHD) references HOP_DONG(MaHD)
);

-- BẢNG DICH VU 

Create Table DICH_VU(
	MADV char(36) default (uuid()) primary key,
    TenDV varchar(50),
    DonGia Decimal(18,2),
    DonVi varchar(20),
    MoTa varchar(50)
);

-- BẢNG  HOA_DON_DICH_VU

Create table HOA_DON_DICH_VU(
	MaHoaDon varchar(50) primary key,  -- trick yymm + msv
    Thang_Nam DATE,
    TrangThaiTT boolean
);

-- BẢNG SU_DUNG_DICH_VU

Create table SU_DUNG_DICH_VU(
	MASD char(36) default (uuid()) primary key,
    SoLuong INT,
    MSV varchar(36),
    MADV char(36),
    MaHoaDon varchar(50),
    foreign key (MSV) references SINH_VIEN(MSV),
    foreign key (MADV) references DICH_VU(MADV),
    foreign key (MaHoaDon) references HOA_DON_DICH_VU(MaHoaDon)
);


-- Bảng XE
Create Table XE(
    BienSo varchar(15) primary key,
    MauXe varchar(15),
    HieuXe varchar(15)
);

-- Bảng VE_XE
Create Table VE_XE(
	MaVe char(36) primary key,
    GiaVe decimal(18,2),
    TrangThaiTT boolean,
    MaHoaDon varchar(50),
    foreign key (MaHoaDon) references HOA_DON_DICH_VU(MaHoaDon)
);

-- Bảng VE_LUOT

Create Table VE_LUOT(
	MaVe char(36) default (uuid()) primary key,
    BienSoXe varchar(15),
    ThoiGianVao datetime,
    ThoiGianRa datetime,
    MSV varchar(36),
    foreign key (MaVe) references VE_XE(MaVe)
);

-- Bảng VE_THANG
Create Table VE_THANG(
	MaVe char(36) default (uuid())  primary key,
    Thang INT,
    NAM INT,
    BienSo char(15),
    MSV varchar(36),
    foreign key (MaVe) references VE_XE(MaVe),
    foreign key(BienSo) references XE(BienSo)
);

