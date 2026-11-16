"""Make every SchLib footprint model resolve by name only.

On each RECORD=45 (footprint model) record:
  - remove ModelDatafile0 (an absolute PcbLib path that overrides the name lookup)
  - remove %UTF8%Description and the empty keys after it (a stale copy Altium reads
    in preference to Description)

No records are added or removed, so OwnerIndex values stay valid.
Usage: fix_links.py <out_dir> <lib.SchLib>...
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfb
import migrate as m

DROP = {b"ModelDatafile0", b"%UTF8%Description", b""}


def fix_file(src, dst):
    t = cfb.read_tree(src)
    changes = []
    for c in t.children:
        d = next((x for x in c.children if x.name == "Data"), None) if c.kind == 1 else None
        if not d:
            continue
        recs = m.parse(d.data)
        for r in recs:
            if r[0]:
                continue
            pr = m.kv(r[1])
            if m.get(pr, b"RECORD") != b"45":
                continue
            gone = [k for k, _ in pr if k in DROP]
            if gone:
                r[1] = m.unkv([(k, v) for k, v in pr if k not in DROP])
                changes.append((c.name, m.get(pr, b"ModelName").decode("cp1252"), sorted(set(gone))))
        d.data = m.serialize(recs)
    cfb.write_tree(t, dst)
    return changes


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for src in sys.argv[2:]:
        for comp, model, gone in fix_file(src, os.path.join(out, os.path.basename(src))):
            print(os.path.basename(src), comp, model, [g.decode() or "(empty)" for g in gone])
