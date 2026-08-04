-- v_inoutheader: unified in/out document header, used for
--   1) 員工管理 detail drill-down (filter WHERE EmployeeId = ...)
--   2) 報表查詢 > 入出單據 (no filter)
IF OBJECT_ID('dbo.v_inoutheader', 'V') IS NOT NULL
    DROP VIEW dbo.v_inoutheader;
GO
CREATE VIEW dbo.v_inoutheader AS
    SELECT 'Inbound' AS DocType, InboundId AS DocId, InboundDate AS DocDate, EmployeeId
    FROM dbo.InboundHeader
    UNION ALL
    SELECT 'Outbound' AS DocType, OutboundId AS DocId, OutboundDate AS DocDate, EmployeeId
    FROM dbo.OutboundHeader;
GO

-- v_inoutdetail: unified in/out document detail lines, used for
--   1) 物料管理 detail drill-down (filter WHERE ProductId = ...)
--   2) 報表查詢 > 入出明細 (no filter)
IF OBJECT_ID('dbo.v_inoutdetail', 'V') IS NOT NULL
    DROP VIEW dbo.v_inoutdetail;
GO
CREATE VIEW dbo.v_inoutdetail AS
    SELECT 'Inbound' AS DocType, InboundId AS DocId, LineNum, ProductId, ProductName, Quantity
    FROM dbo.InboundDetail
    UNION ALL
    SELECT 'Outbound' AS DocType, OutboundId AS DocId, LineNum, ProductId, ProductName, Quantity
    FROM dbo.OutboundDetail;
GO
