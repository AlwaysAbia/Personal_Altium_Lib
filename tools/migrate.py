"""Apply mapping.json to SchLib files. Usage: migrate.py <out_dir> <lib.SchLib>..."""
import sys, os, json, struct, random, string
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfb

W = os.path.dirname(os.path.abspath(__file__))
MAP = {(r["lib"], r["ref"]): r for r in json.load(open(os.path.join(W, "data", "mapping.json"), encoding="utf-8"))}
DROP = {b"val", b"sample link", b"unit price", b"price", b"datasheet"}
KNOWN = DROP | {b"note", b"Comment"}


def parse(data):
    recs, i = [], 0
    while i < len(data):
        h = struct.unpack_from("<I", data, i)[0]
        ln = h & 0xFFFFFF
        recs.append([h >> 24, data[i + 4:i + 4 + ln]])
        i += 4 + ln
    assert i == len(data)
    return recs


def serialize(recs):
    return b"".join(struct.pack("<I", (t << 24) | len(p)) + p for t, p in recs)


def kv(payload):
    assert payload.endswith(b"\0")
    parts = payload[:-1].split(b"|")
    assert parts[0] == b""
    return [tuple(p.split(b"=", 1)) if b"=" in p else (p, None) for p in parts[1:]]


def unkv(pairs):
    return b"|" + b"|".join(k if v is None else k + b"=" + v for k, v in pairs) + b"\0"


def get(pairs, k):
    for a, b in pairs:
        if a == k:
            return b
    return None


def setkey(pairs, k, v, before=None):
    """set key; v None -> remove. New key inserted before `before` key if given, else appended."""
    out = [(a, b) for a, b in pairs if a != k]
    if v is None:
        return out
    idx = next((i for i, (a, b) in enumerate(pairs) if a == k), None)
    if idx is not None:
        pairs = list(pairs)
        pairs[idx] = (k, v)
        return pairs
    if before:
        j = next((i for i, (a, b) in enumerate(out) if a == before), len(out))
        out.insert(j, (k, v))
    else:
        out.append((k, v))
    return out


def strip_utf8(pairs, key):
    return [(a, b) for a, b in pairs if a != b"%UTF8%" + key]


def uid(used):
    while True:
        u = "".join(random.choice(string.ascii_uppercase) for _ in range(8)).encode()
        if u not in used:
            used.add(u)
            return u


def make_param(template, name, text, used):
    p = [(a, b) for a, b in template if not a.startswith(b"%UTF8%") and a != b"IndexInSheet"]
    p = setkey(p, b"IsHidden", b"T", before=b"Text" if get(p, b"Text") is not None else b"Name")
    p = setkey(p, b"Text", text.encode("cp1252") if text else None, before=b"Name")
    p = setkey(p, b"Name", name.encode("cp1252"))
    p = setkey(p, b"UniqueID", uid(used))
    return p


def migrate_component(lib, recs):
    texts = [(i, kv(p)) for i, (t, p) in enumerate(recs) if t == 0]
    comp = next(pr for i, pr in texts if get(pr, b"RECORD") == b"1")
    ref = (get(comp, b"%UTF8%LibReference") or get(comp, b"LibReference")).decode("utf-8" if get(comp, b"%UTF8%LibReference") else "cp1252")
    r = MAP[(lib, ref)]
    params = [(i, pr) for i, pr in texts if get(pr, b"RECORD") == b"41"]
    names = [get(pr, b"Name") for i, pr in params]
    for n in names:
        assert n in KNOWN or n.startswith(b"ComponentLink"), (ref, n)
    used = {get(pr, b"UniqueID") for i, pr in texts}
    by = {get(pr, b"Name"): (i, pr) for i, pr in params}
    template = (by.get(b"val") or by.get(b"note") or by.get(b"unit price") or params[0])[1]
    url_tmpl = (by.get(b"sample link") or by.get(b"ComponentLink1URL") or (None, template))[1]

    new = [make_param(template, "Value", r["value"], used),
           make_param(template, "Manufacturer", r["mfr"], used),
           make_param(template, "Manufacturer Part Number", r["mpn"], used)]
    for k, (desc, url) in enumerate(r["links"], 1):
        new.append(make_param(template, f"ComponentLink{k}Description", desc, used))
        new.append(make_param(url_tmpl, f"ComponentLink{k}URL", url, used))

    out, inserted, comment_idx = [], False, None
    for i, (t, p) in enumerate(recs):
        if t != 0:
            out.append([t, p]); continue
        pr = kv(p)
        if get(pr, b"RECORD") != b"41":
            out.append([t, p]); continue
        n = get(pr, b"Name")
        if n in DROP or n.startswith(b"ComponentLink"):
            continue
        if n == b"note" and r["note_new"] != r["note_old"]:
            pr = strip_utf8(pr, b"Text")
            pr = setkey(pr, b"Text", r["note_new"].encode("cp1252") if r["note_new"] else None)
        if n == b"Comment":
            for np in new:
                out.append([0, np])
            inserted = True
            pr = strip_utf8(pr, b"Text")
            pr = setkey(pr, b"Text", r["comment_new"].encode())
        out.append([0, pr])
    assert inserted, ref

    # renumber IndexInSheet on parameters (Comment keeps its own)
    k = 0
    for rec in out:
        if rec[0] != 0:
            continue
        pr = rec[1] if isinstance(rec[1], list) else kv(rec[1])
        if get(pr, b"RECORD") == b"41" and get(pr, b"Name") != b"Comment":
            pr = setkey(pr, b"IndexInSheet", str(k).encode() if k else None, before=b"OwnerPartId")
            k += 1
        rec[1] = pr
    return ref, [[t, unkv(p) if isinstance(p, list) else p] for t, p in out]


def migrate_file(src, dst):
    lib = os.path.basename(src)[:-7]
    root = cfb.read_tree(src)
    done = []
    for st in root.children:
        if st.kind != 1:
            continue
        for s in st.children:
            if s.name == "Data":
                ref, recs = migrate_component(lib, parse(s.data))
                s.data = serialize(recs)
                done.append(ref)
    cfb.write_tree(root, dst)
    return done


if __name__ == "__main__":
    out_dir = sys.argv[1]
    for f in sys.argv[2:]:
        d = migrate_file(f, os.path.join(out_dir, os.path.basename(f)))
        print(os.path.basename(f), len(d), "components migrated")
