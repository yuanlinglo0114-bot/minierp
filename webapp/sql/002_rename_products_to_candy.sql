-- Rebrand Product catalog for 暹羅糖菓 (a fictional Thai-candy retailer).
-- Renames ProductName in Product, and the denormalized ProductName copies in
-- InboundDetail/OutboundDetail, so every screen/report/export stays
-- consistent. ProductId, StockBalance, and all other columns/relationships
-- are untouched.

UPDATE Product SET ProductName = '芒果QQ軟糖'   WHERE ProductId = 'P001';
UPDATE Product SET ProductName = '芒果奶油糖'   WHERE ProductId = 'P002';
UPDATE Product SET ProductName = '椰香牛奶糖'   WHERE ProductId = 'P003';
UPDATE Product SET ProductName = '香蘭葉軟糖'   WHERE ProductId = 'P004';
UPDATE Product SET ProductName = '泰式奶茶硬糖' WHERE ProductId = 'P005';
UPDATE Product SET ProductName = '泰式奶茶棉花糖' WHERE ProductId = 'P006';
UPDATE Product SET ProductName = '檸檬薄荷糖'   WHERE ProductId = 'P007';
UPDATE Product SET ProductName = '青檸夾心糖'   WHERE ProductId = 'P008';
UPDATE Product SET ProductName = '榴槤酥糖'     WHERE ProductId = 'P009';
UPDATE Product SET ProductName = '榴槤牛軋糖'   WHERE ProductId = 'P010';
UPDATE Product SET ProductName = '泰式奶茶太妃糖' WHERE ProductId = 'P011';
UPDATE Product SET ProductName = '焦糖鹹奶茶糖' WHERE ProductId = 'P012';
UPDATE Product SET ProductName = '芝麻花生糖'   WHERE ProductId = 'P013';
UPDATE Product SET ProductName = '花生椰棗糖'   WHERE ProductId = 'P014';
UPDATE Product SET ProductName = '蝶豆花軟糖'   WHERE ProductId = 'P015';
UPDATE Product SET ProductName = '蝶豆花棉花糖' WHERE ProductId = 'P016';
UPDATE Product SET ProductName = '玫瑰荔枝糖漿' WHERE ProductId = 'P017';
UPDATE Product SET ProductName = '香茅糖漿'     WHERE ProductId = 'P018';
UPDATE Product SET ProductName = '芒果乾片'     WHERE ProductId = 'P019';
UPDATE Product SET ProductName = '椰子脆片'     WHERE ProductId = 'P020';

UPDATE id
SET id.ProductName = p.ProductName
FROM InboundDetail id
JOIN Product p ON p.ProductId = id.ProductId;

UPDATE od
SET od.ProductName = p.ProductName
FROM OutboundDetail od
JOIN Product p ON p.ProductId = od.ProductId;
