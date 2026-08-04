-- =====================================================================
-- 02_add_foreign_keys.sql
-- Adds the FOREIGN KEY constraints that [lalala] was created WITHOUT.
--
-- These 7 relationships were inferred by reading the table schema of
-- biz00 (column names/types, which columns participate in each table's
-- PRIMARY KEY, and NOT NULL-ness) — cross-checked against biz00's own
-- FK constraints, which happen to already define exactly this same set:
--
--   Employee (1) ---< InboundHeader   (EmployeeId)   non-identifying, mandatory
--   Employee (1) ---< OutboundHeader  (EmployeeId)   non-identifying, mandatory
--   InboundHeader  (1) ---< InboundDetail  (InboundId)   IDENTIFYING (part of child PK)
--   OutboundHeader (1) ---< OutboundDetail (OutboundId)  IDENTIFYING (part of child PK)
--   Product (1) ---< InboundDetail   (ProductId)  non-identifying, mandatory
--   Product (1) ---< OutboundDetail  (ProductId)  non-identifying, mandatory
--   Product (1) ---< InventoryDailyClosing (ProductId)  IDENTIFYING (part of child PK)
-- =====================================================================

USE lalala;
GO

ALTER TABLE dbo.InboundHeader WITH CHECK
    ADD CONSTRAINT FK_InboundHeader_Employee
    FOREIGN KEY (EmployeeId) REFERENCES dbo.Employee (EmployeeId);
ALTER TABLE dbo.InboundHeader CHECK CONSTRAINT FK_InboundHeader_Employee;

ALTER TABLE dbo.OutboundHeader WITH CHECK
    ADD CONSTRAINT FK_OutboundHeader_Employee
    FOREIGN KEY (EmployeeId) REFERENCES dbo.Employee (EmployeeId);
ALTER TABLE dbo.OutboundHeader CHECK CONSTRAINT FK_OutboundHeader_Employee;

ALTER TABLE dbo.InboundDetail WITH CHECK
    ADD CONSTRAINT FK_InboundDetail_InboundHeader
    FOREIGN KEY (InboundId) REFERENCES dbo.InboundHeader (InboundId);
ALTER TABLE dbo.InboundDetail CHECK CONSTRAINT FK_InboundDetail_InboundHeader;

ALTER TABLE dbo.InboundDetail WITH CHECK
    ADD CONSTRAINT FK_InboundDetail_Product
    FOREIGN KEY (ProductId) REFERENCES dbo.Product (ProductId);
ALTER TABLE dbo.InboundDetail CHECK CONSTRAINT FK_InboundDetail_Product;

ALTER TABLE dbo.OutboundDetail WITH CHECK
    ADD CONSTRAINT FK_OutboundDetail_OutboundHeader
    FOREIGN KEY (OutboundId) REFERENCES dbo.OutboundHeader (OutboundId);
ALTER TABLE dbo.OutboundDetail CHECK CONSTRAINT FK_OutboundDetail_OutboundHeader;

ALTER TABLE dbo.OutboundDetail WITH CHECK
    ADD CONSTRAINT FK_OutboundDetail_Product
    FOREIGN KEY (ProductId) REFERENCES dbo.Product (ProductId);
ALTER TABLE dbo.OutboundDetail CHECK CONSTRAINT FK_OutboundDetail_Product;

ALTER TABLE dbo.InventoryDailyClosing WITH CHECK
    ADD CONSTRAINT FK_InventoryDailyClosing_Product
    FOREIGN KEY (ProductId) REFERENCES dbo.Product (ProductId);
ALTER TABLE dbo.InventoryDailyClosing CHECK CONSTRAINT FK_InventoryDailyClosing_Product;
GO
