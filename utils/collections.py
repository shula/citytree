def muldict(pairs):
    d = {}
    for k, v in pairs:
        if d.has_key(k): d[k].append(v)
        else: d[k] = [v]
    return d

