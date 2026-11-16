"""Apply rename_map.R (name, Design Item ID, designator, description). Usage: apply_names.py <out_dir> <lib.SchLib>..."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfb, migrate as m
from rename_map import R


def text_fields(pairs, key, value, before=None):
    """Set key (and %UTF8%key when non-ASCII) to value; drops any stale %UTF8% copy."""
    uk = b"%UTF8%" + key
    pairs = [(a, b) for a, b in pairs if a != uk]
    pairs = m.setkey(pairs, key, value.encode("cp1252") if value else None, before=before)
    if value and not value.isascii():
        j = next(i for i, (a, b) in enumerate(pairs) if a == key)
        pairs.insert(j, (uk, value.encode("utf-8")))
    return pairs


def storage_name(name):
    return name.replace("/", "_").replace("\\", "_")[:31]


def apply_file(src, dst):
    lib = os.path.basename(src)[:-7]
    root = cfb.read_tree(src)
    renames = {}
    for st in root.children:
        if st.kind != 1:
            continue
        data = next(s for s in st.children if s.name == "Data")
        recs = m.parse(data.data)
        comp = m.kv(recs[0][1])
        assert m.get(comp, b"RECORD") == b"1"
        u = m.get(comp, b"%UTF8%LibReference")
        old = u.decode() if u else m.get(comp, b"LibReference").decode("cp1252")
        n = R[(lib, old)]
        comp = text_fields(comp, b"LibReference", n["name"])
        comp = text_fields(comp, b"ComponentDescription", n["desc"], before=b"PartCount")
        comp = m.setkey(comp, b"DesignItemId", n["name"].encode("cp1252"))
        recs[0][1] = m.unkv(comp)
        ndes = 0
        for rec in recs:
            if rec[0] == 0:
                pr = m.kv(rec[1])
                if m.get(pr, b"RECORD") == b"34":
                    rec[1] = m.unkv(text_fields(pr, b"Text", n["des"] + "?"))
                    ndes += 1
        assert ndes == 1, (old, ndes)
        data.data = m.serialize(recs)
        st.name = storage_name(n["name"])
        renames[old] = n
    names = [st.name.upper() for st in root.children if st.kind == 1]
    assert len(names) == len(set(names)), "storage name collision"

    # FileHeader: LibRefN / CompDescrN
    fh = next(c for c in root.children if c.name == "FileHeader")
    recs = m.parse(fh.data)
    pr = m.kv(recs[0][1])
    count = int(m.get(pr, b"CompCount"))
    for i in range(count):
        k = f"LibRef{i}".encode()
        u = m.get(pr, b"%UTF8%" + k)
        old = u.decode() if u else m.get(pr, k).decode("cp1252")
        n = renames.pop(old)
        pr = text_fields(pr, k, n["name"])
        pr = text_fields(pr, f"CompDescr{i}".encode(), n["desc"], before=f"PartCount{i}".encode())
    assert not renames, renames
    recs[0][1] = m.unkv(pr)
    fh.data = m.serialize(recs)

    # SectionKeys: only needed for names of 31+ characters
    long_names = [n["name"] for n in R.values() if False]
    long_names = [st for st in root.children if st.kind == 1 and len(st.name) >= 31]
    assert not long_names
    root.children = [c for c in root.children if c.name != "SectionKeys"]
    cfb.write_tree(root, dst)
    return count


if __name__ == "__main__":
    for f in sys.argv[2:]:
        print(os.path.basename(f), apply_file(f, os.path.join(sys.argv[1], os.path.basename(f))))
