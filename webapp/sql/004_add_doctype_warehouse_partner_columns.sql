-- InboundHeader: add VendorId (external trading partner), DocTypeId (單別),
-- WarehouseId (倉別). Employee stays as-is (internal handler) -- both
-- required, per confirmed decision. Existing rows backfill to the "normal
-- inbound" doctype and default warehouse as part of the ALTER TABLE DDL
-- itself (WITH VALUES), which is what makes step 5's regression check exact.
ALTER TABLE dbo.InboundHeader ADD
    VendorId    nvarchar(20) NOT NULL CONSTRAINT DF_InboundHeader_VendorId    DEFAULT ('V001') WITH VALUES,
    DocTypeId   nvarchar(20) NOT NULL CONSTRAINT DF_InboundHeader_DocTypeId   DEFAULT ('D001') WITH VALUES,
    WarehouseId nvarchar(20) NOT NULL CONSTRAINT DF_InboundHeader_WarehouseId DEFAULT ('W001') WITH VALUES;

-- OutboundHeader: mirror with CustomerId instead of VendorId.
ALTER TABLE dbo.OutboundHeader ADD
    CustomerId  nvarchar(20) NOT NULL CONSTRAINT DF_OutboundHeader_CustomerId  DEFAULT ('C001') WITH VALUES,
    DocTypeId   nvarchar(20) NOT NULL CONSTRAINT DF_OutboundHeader_DocTypeId   DEFAULT ('D003') WITH VALUES,
    WarehouseId nvarchar(20) NOT NULL CONSTRAINT DF_OutboundHeader_WarehouseId DEFAULT ('W001') WITH VALUES;
GO

-- InventoryDailyClosing: add WarehouseId and widen the PK to include it.
ALTER TABLE dbo.InventoryDailyClosing ADD
    WarehouseId nvarchar(20) NOT NULL CONSTRAINT DF_IDC_WarehouseId DEFAULT ('W001') WITH VALUES;
GO

ALTER TABLE dbo.InventoryDailyClosing DROP CONSTRAINT PK_InventoryDailyClosing;
ALTER TABLE dbo.InventoryDailyClosing ADD CONSTRAINT PK_InventoryDailyClosing PRIMARY KEY (ClosingDate, ProductId, WarehouseId);
GO

-- Backfill ProductWarehouseStock from the current global StockBalance,
-- attributing all pre-migration stock to the default warehouse W001.
-- This is genuine DML (file content only) -- review before running; not
-- executed automatically as part of writing this migration file.
INSERT INTO dbo.ProductWarehouseStock (ProductId, WarehouseId, StockBalance)
SELECT ProductId, 'W001', StockBalance FROM dbo.Product;
GO
