def recompute_for_product_warehouse(cur, product_id, warehouse_id):
    """Rebuild InventoryDailyClosing for one (product, warehouse) from the ground truth
    (InboundDetail/OutboundDetail joined to their headers' dates and DocType), replacing
    whatever rows currently exist.

    This is a full rebuild rather than an incremental patch specifically because
    documents are routinely entered out of date order: backdating an inbound/outbound
    after later dates already exist would otherwise require threading opening/closing
    balances through every later row by hand. A full rebuild from the transaction
    tables is correct regardless of entry order, and cheap at this table's scale.

    Each detail row's effective stock contribution is Quantity * DocType.SignMultiplier,
    not an unconditional +/- per table -- a return-type DocType can reverse a document's
    normal direction (e.g. a return-outbound increases stock). InboundQuantity/
    OutboundQuantity are stored as signed net contributions (not raw physical volumes)
    so the existing CK_InventoryDailyClosing_Balance CHECK
    (Closing = Opening + Inbound - Outbound) stays valid unmodified.

    Must be called with the same cursor used for the header/detail writes that
    triggered it, inside the same db.transaction(), so the closing table stays
    consistent with the transaction data it commits with.
    """
    cur.execute(
        "SELECT ih.InboundDate AS d, SUM(id.Quantity * dt.SignMultiplier) AS q "
        "FROM InboundDetail id "
        "JOIN InboundHeader ih ON ih.InboundId = id.InboundId "
        "JOIN DocType dt ON dt.DocTypeId = ih.DocTypeId "
        "WHERE id.ProductId = %s AND ih.WarehouseId = %s "
        "GROUP BY ih.InboundDate",
        (product_id, warehouse_id),
    )
    inbound_net_by_date = {row["d"]: row["q"] for row in cur.fetchall()}

    cur.execute(
        "SELECT oh.OutboundDate AS d, SUM(od.Quantity * dt.SignMultiplier) AS q "
        "FROM OutboundDetail od "
        "JOIN OutboundHeader oh ON oh.OutboundId = od.OutboundId "
        "JOIN DocType dt ON dt.DocTypeId = oh.DocTypeId "
        "WHERE od.ProductId = %s AND oh.WarehouseId = %s "
        "GROUP BY oh.OutboundDate",
        (product_id, warehouse_id),
    )
    outbound_net_by_date = {row["d"]: row["q"] for row in cur.fetchall()}

    all_dates = sorted(set(inbound_net_by_date) | set(outbound_net_by_date))

    cur.execute(
        "DELETE FROM InventoryDailyClosing WHERE ProductId = %s AND WarehouseId = %s",
        (product_id, warehouse_id),
    )

    running_balance = 0
    for closing_date in all_dates:
        inbound_qty = inbound_net_by_date.get(closing_date, 0)
        outbound_qty = -outbound_net_by_date.get(closing_date, 0)
        opening = running_balance
        closing = opening + inbound_qty - outbound_qty
        cur.execute(
            "INSERT INTO InventoryDailyClosing "
            "(ClosingDate, ProductId, WarehouseId, OpeningQuantity, InboundQuantity, OutboundQuantity, ClosingQuantity) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (closing_date, product_id, warehouse_id, opening, inbound_qty, outbound_qty, closing),
        )
        running_balance = closing
