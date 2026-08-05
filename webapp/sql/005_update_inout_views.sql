-- Recreate v_inoutheader/v_inoutdetail with the new DocTypeId/WarehouseId/
-- VendorId/CustomerId columns. The views' existing literal `DocType` column
-- (the string 'Inbound'/'Outbound' discriminator) is untouched -- the new
-- sub-classification column is deliberately named DocTypeId to avoid
-- colliding with it.

IF OBJECT_ID('dbo.v_inoutheader', 'V') IS NOT NULL
    DROP VIEW dbo.v_inoutheader;
GO
CREATE VIEW dbo.v_inoutheader AS
    SELECT 'Inbound' AS DocType, InboundId AS DocId, InboundDate AS DocDate, EmployeeId,
           DocTypeId, WarehouseId, VendorId, CAST(NULL AS nvarchar(20)) AS CustomerId
    FROM dbo.InboundHeader
    UNION ALL
    SELECT 'Outbound' AS DocType, OutboundId AS DocId, OutboundDate AS DocDate, EmployeeId,
           DocTypeId, WarehouseId, CAST(NULL AS nvarchar(20)) AS VendorId, CustomerId
    FROM dbo.OutboundHeader;
GO

-- v_inoutdetail now also joins back to its own header to expose
-- DocTypeId/WarehouseId for report filtering -- a new dependency this view
-- didn't have before, added deliberately for this feature.
IF OBJECT_ID('dbo.v_inoutdetail', 'V') IS NOT NULL
    DROP VIEW dbo.v_inoutdetail;
GO
CREATE VIEW dbo.v_inoutdetail AS
    SELECT 'Inbound' AS DocType, d.InboundId AS DocId, d.LineNum, d.ProductId, d.ProductName, d.Quantity,
           h.DocTypeId, h.WarehouseId
    FROM dbo.InboundDetail d
    JOIN dbo.InboundHeader h ON h.InboundId = d.InboundId
    UNION ALL
    SELECT 'Outbound' AS DocType, d.OutboundId AS DocId, d.LineNum, d.ProductId, d.ProductName, d.Quantity,
           h.DocTypeId, h.WarehouseId
    FROM dbo.OutboundDetail d
    JOIN dbo.OutboundHeader h ON h.OutboundId = d.OutboundId;
GO
