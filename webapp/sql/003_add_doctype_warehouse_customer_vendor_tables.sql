-- New master tables for 單別 (DocType), 倉別 (Warehouse), 客戶 (Customer),
-- 供應商 (Vendor), plus per-warehouse stock. ID prefixes chosen to avoid
-- collision with existing P (Product), E (Employee), IN/OUT (document headers):
-- D (DocType), W (Warehouse), C (Customer), V (Vendor).

CREATE TABLE dbo.DocType (
    DocTypeId      nvarchar(20) NOT NULL,
    DocTypeName    nvarchar(50) NOT NULL,
    Category       nvarchar(10) NOT NULL,
    SignMultiplier smallint     NOT NULL,
    CONSTRAINT PK_DocType PRIMARY KEY (DocTypeId),
    CONSTRAINT CK_DocType_DocTypeName_NotBlank CHECK (len(ltrim(rtrim(DocTypeName))) > 0),
    CONSTRAINT CK_DocType_Category CHECK (Category IN ('Inbound','Outbound')),
    CONSTRAINT CK_DocType_SignMultiplier CHECK (SignMultiplier IN (1,-1))
);

CREATE TABLE dbo.Warehouse (
    WarehouseId   nvarchar(20) NOT NULL,
    WarehouseName nvarchar(50) NOT NULL,
    CONSTRAINT PK_Warehouse PRIMARY KEY (WarehouseId),
    CONSTRAINT CK_Warehouse_WarehouseName_NotBlank CHECK (len(ltrim(rtrim(WarehouseName))) > 0)
);

CREATE TABLE dbo.Customer (
    CustomerId   nvarchar(20)  NOT NULL,
    CustomerName nvarchar(100) NOT NULL,
    CONSTRAINT PK_Customer PRIMARY KEY (CustomerId),
    CONSTRAINT CK_Customer_CustomerName_NotBlank CHECK (len(ltrim(rtrim(CustomerName))) > 0)
);

CREATE TABLE dbo.Vendor (
    VendorId   nvarchar(20)  NOT NULL,
    VendorName nvarchar(100) NOT NULL,
    CONSTRAINT PK_Vendor PRIMARY KEY (VendorId),
    CONSTRAINT CK_Vendor_VendorName_NotBlank CHECK (len(ltrim(rtrim(VendorName))) > 0)
);

-- Per-(Product, Warehouse) stock. CK matches Product's own
-- CK_Product_StockBalance_NonNegative for consistency.
CREATE TABLE dbo.ProductWarehouseStock (
    ProductId    nvarchar(20)  NOT NULL,
    WarehouseId  nvarchar(20)  NOT NULL,
    StockBalance decimal(18,3) NOT NULL CONSTRAINT DF_PWS_StockBalance DEFAULT (0),
    CONSTRAINT PK_ProductWarehouseStock PRIMARY KEY (ProductId, WarehouseId),
    CONSTRAINT CK_ProductWarehouseStock_StockBalance_NonNegative CHECK (StockBalance >= 0)
);
GO

-- Seed data (file content only -- run deliberately by a human against the
-- target DB, same convention as sql/01_create_lalala.sql's own INSERTs).
-- D002 (退貨入庫) decreases stock and D004 (退貨出庫) increases stock --
-- confirmed symmetric-reversal semantics, not the category's own default.

INSERT INTO dbo.DocType (DocTypeId, DocTypeName, Category, SignMultiplier) VALUES ('D001', N'一般入庫', 'Inbound', 1);
INSERT INTO dbo.DocType (DocTypeId, DocTypeName, Category, SignMultiplier) VALUES ('D002', N'退貨入庫', 'Inbound', -1);
INSERT INTO dbo.DocType (DocTypeId, DocTypeName, Category, SignMultiplier) VALUES ('D003', N'一般出庫', 'Outbound', -1);
INSERT INTO dbo.DocType (DocTypeId, DocTypeName, Category, SignMultiplier) VALUES ('D004', N'退貨出庫', 'Outbound', 1);

INSERT INTO dbo.Warehouse (WarehouseId, WarehouseName) VALUES ('W001', N'主倉');

INSERT INTO dbo.Customer (CustomerId, CustomerName) VALUES ('C001', N'未指定客戶');
INSERT INTO dbo.Vendor (VendorId, VendorName) VALUES ('V001', N'未指定供應商');
GO
