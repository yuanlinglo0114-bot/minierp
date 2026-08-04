def next_id_for_date(existing_ids, prefix, width=3):
    """Given existing ids sharing `prefix` (e.g. 'P', 'IN20260601'), return the
    next sequential id: max numeric suffix + 1, zero-padded to `width`.
    """
    max_n = 0
    for eid in existing_ids:
        suffix = eid[len(prefix):]
        if suffix.isdigit():
            max_n = max(max_n, int(suffix))
    return f"{prefix}{str(max_n + 1).zfill(width)}"
