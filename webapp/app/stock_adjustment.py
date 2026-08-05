def adjust_stock(cur, product_id, warehouse_id, delta):
    """Apply `delta` (can be negative) to ProductWarehouseStock(product_id, warehouse_id),
    creating the row if this is the first transaction against that combo, and keep
    Product.StockBalance in sync as a rolled-up total across all warehouses.

    Must be called with the same cursor as the header/detail writes that triggered it,
    inside the same db.transaction().
    """
    cur.execute(
        "SELECT StockBalance FROM ProductWarehouseStock WHERE ProductId = %s AND WarehouseId = %s",
        (product_id, warehouse_id),
    )
    row = cur.fetchone()
    if row is None:
        cur.execute(
            "INSERT INTO ProductWarehouseStock (ProductId, WarehouseId, StockBalance) VALUES (%s, %s, %s)",
            (product_id, warehouse_id, delta),
        )
    else:
        cur.execute(
            "UPDATE ProductWarehouseStock SET StockBalance = StockBalance + %s WHERE ProductId = %s AND WarehouseId = %s",
            (delta, product_id, warehouse_id),
        )
    cur.execute(
        "UPDATE Product SET StockBalance = StockBalance + %s WHERE ProductId = %s",
        (delta, product_id),
    )
