"""Check fix_links.py output against its source.

Every stream must be identical except SchLib component Data streams, where the only
allowed difference is the removal of ModelDatafile0 / %UTF8%Description / empty keys
from RECORD=45. Afterwards no RECORD=45 may hold those keys, and every ModelName must
exist as a footprint in one of the PcbLibs (except the known missing ones).
Usage: verify_links.py <sch_src> <sch_out> <pcb_dir>
"""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfb
import migrate as m
from fix_links import DROP

KNOWN_MISSING = {"SMD_4.5x3.2mm_Trimmer"}
src_dir, out_dir, pcb_dir = sys.argv[1:4]

fps = set()
for p in glob.glob(os.path.join(pcb_dir, "*.PcbLib")):
    fps |= {c.name for c in cfb.read_tree(p).children if c.kind == 1}

bad, n45 = [], 0
for src in sorted(glob.glob(os.path.join(src_dir, "*.SchLib"))):
    lib = os.path.basename(src)
    a, b = cfb.flat(cfb.read_tree(src)), cfb.flat(cfb.read_tree(os.path.join(out_dir, lib)))
    if a.keys() != b.keys():
        bad.append((lib, "stream set differs"))
        continue
    for path in a:
        if a[path] == b[path]:
            continue
        if not path.endswith("/Data") or path.count("/") != 2:
            bad.append((lib, path, "changed"))
            continue
        ra, rb = m.parse(a[path][2]), m.parse(b[path][2])
        if len(ra) != len(rb):
            bad.append((lib, path, "record count"))
            continue
        for (ta, pa), (tb, pb) in zip(ra, rb):
            if pa == pb:
                continue
            ka = m.kv(pa)
            if ta or m.get(ka, b"RECORD") != b"45" or [x for x in ka if x[0] not in DROP] != m.kv(pb):
                bad.append((lib, path, "unexpected record change"))
    for path, (kind, _, data) in b.items():
        if not path.endswith("/Data") or path.count("/") != 2:
            continue
        for t, p in m.parse(data):
            if t:
                continue
            kv = m.kv(p)
            if m.get(kv, b"RECORD") != b"45":
                continue
            n45 += 1
            if any(k in DROP for k, _ in kv):
                bad.append((lib, path, "key still present"))
            name = m.get(kv, b"ModelName").decode("cp1252")
            if name not in fps and name not in KNOWN_MISSING:
                bad.append((lib, path, "footprint not found: " + name))

print(n45, "footprint models checked")
for x in bad:
    print("FAIL", *x)
print("OK" if not bad else "%d problems" % len(bad))
