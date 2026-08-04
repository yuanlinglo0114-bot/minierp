-- =====================================================================
-- 01_create_lalala.sql
-- Clone of [biz00] named [lalala], WITHOUT foreign key constraints.
-- Keeps: PRIMARY KEY, CHECK, DEFAULT constraints, data.
-- Purpose: practice database for adding the missing FOREIGN KEY
--          constraints yourself (see 02_add_foreign_keys.sql for the
--          answer key / script).
-- =====================================================================

CREATE DATABASE lalala;
GO

USE lalala;
GO

CREATE TABLE dbo.Employee (
    EmployeeId   nvarchar(20)  NOT NULL,
    EmployeeName nvarchar(50)  NOT NULL,
    Email        nvarchar(255) NULL,
    CONSTRAINT PK_Employee PRIMARY KEY (EmployeeId),
    CONSTRAINT CK_Employee_EmployeeName_NotBlank CHECK (len(ltrim(rtrim(EmployeeName))) > 0),
    CONSTRAINT CK_Employee_Email_Format CHECK (Email IS NULL OR Email LIKE N'%_@_%._%')
);

CREATE TABLE dbo.Product (
    ProductId    nvarchar(20)  NOT NULL,
    ProductName  nvarchar(100) NOT NULL,
    StockBalance decimal(18,3) NOT NULL CONSTRAINT DF_Product_StockBalance DEFAULT (0),
    CONSTRAINT PK_Product PRIMARY KEY (ProductId),
    CONSTRAINT CK_Product_ProductName_NotBlank CHECK (len(ltrim(rtrim(ProductName))) > 0),
    CONSTRAINT CK_Product_StockBalance_NonNegative CHECK (StockBalance >= 0)
);

CREATE TABLE dbo.InboundHeader (
    InboundId  nvarchar(20) NOT NULL,
    InboundDate date NOT NULL CONSTRAINT DF_InboundHeader_InboundDate DEFAULT (CONVERT(date, SYSDATETIME())),
    EmployeeId nvarchar(20) NOT NULL,
    CONSTRAINT PK_InboundHeader PRIMARY KEY (InboundId)
    -- FK to Employee intentionally omitted; see 02_add_foreign_keys.sql
);

CREATE TABLE dbo.InboundDetail (
    InboundId   nvarchar(20)  NOT NULL,
    LineNum     smallint      NOT NULL,
    ProductId   nvarchar(20)  NOT NULL,
    ProductName nvarchar(100) NOT NULL,
    Quantity    decimal(18,3) NOT NULL,
    CONSTRAINT PK_InboundDetail PRIMARY KEY (InboundId, LineNum),
    CONSTRAINT CK_InboundDetail_LineNum_Positive CHECK (LineNum > 0),
    CONSTRAINT CK_InboundDetail_Quantity_Positive CHECK (Quantity > 0)
    -- FKs to InboundHeader and Product intentionally omitted
);

CREATE TABLE dbo.OutboundHeader (
    OutboundId   nvarchar(20) NOT NULL,
    OutboundDate date NOT NULL CONSTRAINT DF_OutboundHeader_OutboundDate DEFAULT (CONVERT(date, SYSDATETIME())),
    EmployeeId   nvarchar(20) NOT NULL,
    CONSTRAINT PK_OutboundHeader PRIMARY KEY (OutboundId)
    -- FK to Employee intentionally omitted
);

CREATE TABLE dbo.OutboundDetail (
    OutboundId  nvarchar(20)  NOT NULL,
    LineNum     smallint      NOT NULL,
    ProductId   nvarchar(20)  NOT NULL,
    ProductName nvarchar(100) NOT NULL,
    Quantity    decimal(18,3) NOT NULL,
    CONSTRAINT PK_OutboundDetail PRIMARY KEY (OutboundId, LineNum),
    CONSTRAINT CK_OutboundDetail_LineNum_Positive CHECK (LineNum > 0),
    CONSTRAINT CK_OutboundDetail_Quantity_Positive CHECK (Quantity > 0)
    -- FKs to OutboundHeader and Product intentionally omitted
);

CREATE TABLE dbo.InventoryDailyClosing (
    ClosingDate      date          NOT NULL,
    ProductId        nvarchar(20)  NOT NULL,
    OpeningQuantity  decimal(18,3) NOT NULL CONSTRAINT DF_IDC_Opening  DEFAULT (0),
    InboundQuantity  decimal(18,3) NOT NULL CONSTRAINT DF_IDC_Inbound  DEFAULT (0),
    OutboundQuantity decimal(18,3) NOT NULL CONSTRAINT DF_IDC_Outbound DEFAULT (0),
    ClosingQuantity  decimal(18,3) NOT NULL CONSTRAINT DF_IDC_Closing  DEFAULT (0),
    CONSTRAINT PK_InventoryDailyClosing PRIMARY KEY (ClosingDate, ProductId),
    CONSTRAINT CK_InventoryDailyClosing_Balance
        CHECK (ClosingQuantity = OpeningQuantity + InboundQuantity - OutboundQuantity)
    -- FK to Product intentionally omitted
);
GO

-- Copy data from biz00 (same server)
INSERT INTO lalala.dbo.Employee              SELECT * FROM biz00.dbo.Employee;
INSERT INTO lalala.dbo.Product                SELECT * FROM biz00.dbo.Product;
INSERT INTO lalala.dbo.InboundHeader          SELECT * FROM biz00.dbo.InboundHeader;
INSERT INTO lalala.dbo.InboundDetail          SELECT * FROM biz00.dbo.InboundDetail;
INSERT INTO lalala.dbo.OutboundHeader         SELECT * FROM biz00.dbo.OutboundHeader;
INSERT INTO lalala.dbo.OutboundDetail         SELECT * FROM biz00.dbo.OutboundDetail;
INSERT INTO lalala.dbo.InventoryDailyClosing  SELECT * FROM biz00.dbo.InventoryDailyClosing;
GO
