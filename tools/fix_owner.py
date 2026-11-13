"""Recompute OwnerIndex of model records: 45 -> preceding 44, 46/47/48 -> preceding 45. Usage: fix_owner.py <out_dir> files..."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfb, migrate as m
def fix_recs(recs):
    last = {}
    for i, rec in enumerate(recs):
        if rec[0] != 0: continue
        pr = m.kv(rec[1]); t = m.get(pr, b"RECORD")
        owner = {b"45": b"44", b"46": b"45", b"47": b"45", b"48": b"45"}.get(t)
        if owner:
            assert m.get(pr, b"OwnerIndex") is not None and owner in last
            rec[1] = m.unkv(m.setkey(pr, b"OwnerIndex", str(last[owner]).encode()))
        last[t] = i
    return recs
if __name__ == "__main__":
    for f in sys.argv[2:]:
        root = cfb.read_tree(f)
        for st in root.children:
            if st.kind == 1:
                d = next(s for s in st.children if s.name == "Data")
                d.data = m.serialize(fix_recs(m.parse(d.data)))
        cfb.write_tree(root, os.path.join(sys.argv[1], os.path.basename(f)))
        print(os.path.basename(f), "fixed")
