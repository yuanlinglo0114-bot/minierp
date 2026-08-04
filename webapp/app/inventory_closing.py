def recompute_for_product(cur, product_id):
    """Rebuild InventoryDailyClosing for one product from the ground truth
    (InboundDetail/OutboundDetail joined to their headers' dates), replacing
    whatever rows currently exist.

    This is a full rebuild rather than an incremental patch specifically
    because documents are routinely entered out of date order: backdating an
    inbound/outbound after later dates already exist would otherwise require
    threading opening/closing balances through every later row by hand. A
    full rebuild from the transaction tables is correct regardless of entry
    order, and cheap at this table's scale.

    Must be called with the same cursor used for the header/detail writes
    that triggered it, inside the same db.transaction(), so the closing
    table stays consistent with the transaction data it's commits with.
    """
    cur.execute(
        "SELECT ih.InboundDate AS d, SUM(id.Quantity) AS q "
        "FROM InboundDetail id JOIN InboundHeader ih ON ih.InboundId = id.InboundId "
        "WHERE id.ProductId = %s GROUP BY ih.InboundDate",
        (product_id,),
    )
    inbound_by_date = {row["d"]: row["q"] for row in cur.fetchall()}

    cur.execute(
        "SELECT oh.OutboundDate AS d, SUM(od.Quantity) AS q "
        "FROM OutboundDetail od JOIN OutboundHeader oh ON oh.OutboundId = od.OutboundId "
        "WHERE od.ProductId = %s GROUP BY oh.OutboundDate",
        (product_id,),
    )
    outbound_by_date = {row["d"]: row["q"] for row in cur.fetchall()}

    all_dates = sorted(set(inbound_by_date) | set(outbound_by_date))

    cur.execute("DELETE FROM InventoryDailyClosing WHERE ProductId = %s", (product_id,))

    running_balance = 0
    for closing_date in all_dates:
        in_qty = inbound_by_date.get(closing_date, 0)
        out_qty = outbound_by_date.get(closing_date, 0)
        opening = running_balance
        closing = opening + in_qty - out_qty
        cur.execute(
            "INSERT INTO InventoryDailyClosing "
            "(ClosingDate, ProductId, OpeningQuantity, InboundQuantity, OutboundQuantity, ClosingQuantity) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (closing_date, product_id, opening, in_qty, out_qty, closing),
        )
        running_balance = closing
