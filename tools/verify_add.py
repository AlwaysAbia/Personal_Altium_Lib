"""Check add_part.py output against the destination libraries it was built from.
Usage: verify_add.py <src.SchLib> <src.PcbLib> <dst.SchLib> <dst.PcbLib> <out_dir>"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import olefile, cfb, migrate as m, pcbparse
from add_part import PART
from apply_fp import read_name_block

ss, sp, ds, dp, out = sys.argv[1:6]
os_, op = os.path.join(out, os.path.basename(ds)), os.path.join(out, os.path.basename(dp))
for f in (os_, op):
    olefile.OleFileIO(f).close()

# ---- SchLib
a, b = cfb.flat(cfb.read_tree(ds)), cfb.flat(cfb.read_tree(os_))
new = "/" + PART["name"]
extra = {k for k in b if k not in a}
assert extra == {new, new + "/Data"}, extra
for k in a:
    if k != "/FileHeader":
        assert a[k] == b[k], k
recs = m.parse(b[new + "/Data"][2])
txt = [m.kv(p) if t == 0 else None for t, p in recs]
comp = txt[0]
assert m.get(comp, b"LibReference") == PART["name"].encode() == m.get(comp, b"DesignItemId")
params = {m.get(pr, b"Name"): m.get(pr, b"Text") for pr in txt if pr and m.get(pr, b"RECORD") == b"41"}
want = {b"note", b"Value", b"Manufacturer", b"Manufacturer Part Number", b"Comment"}
want |= {f"ComponentLink{i}{s}".encode() for i in range(1, len(PART["links"]) + 1) for s in ("Description", "URL")}
assert set(params) == want, params
assert params[b"Comment"] == b"=Manufacturer Part Number"
for i, pr in enumerate(txt):
    if pr and m.get(pr, b"OwnerIndex") is not None:
        owner = txt[int(m.get(pr, b"OwnerIndex"))]
        exp = {b"45": b"44", b"46": b"45", b"48": b"45"}[m.get(pr, b"RECORD")]
        assert m.get(owner, b"RECORD") == exp, i
model = next(pr for pr in txt if pr and m.get(pr, b"RECORD") == b"45")
assert m.get(model, b"ModelName") == m.get(model, b"ModelDatafileEntity0") == PART["fp"].encode()
assert m.get(model, b"ModelDatafile0") is None
nf = int(m.get(m.kv(m.parse(b["/FileHeader"][2])[0][1]), b"FontIdCount"))
assert all(1 <= int(m.get(pr, b"FontID")) <= nf for pr in txt if pr and m.get(pr, b"FontID"))
# pins unchanged from the vendor file
src_pins = [p for t, p in m.parse(cfb.flat(cfb.read_tree(ss))["/" + PART["src_comp"] + "/Data"][2]) if t]
assert src_pins == [p for t, p in recs if t]
fh = m.kv(m.parse(b["/FileHeader"][2])[0][1])
n = int(m.get(fh, b"CompCount"))
libs = {m.get(fh, b"LibRef%d" % i).decode("cp1252").replace("/", "_")[:31] for i in range(n)}
assert libs == {k[1:] for k in b if k.count("/") == 1 and k[1:] not in ("FileHeader", "Storage")}, libs
print("SchLib OK:", n, "components,", len(src_pins), "pins,", "params", sorted(x.decode() for x in params))

# ---- PcbLib
a, b = cfb.flat(cfb.read_tree(dp)), cfb.flat(cfb.read_tree(op))
src = cfb.flat(cfb.read_tree(sp))
fp = "/" + PART["fp"]
nmod = struct.unpack("<I", a["/Library/Models/Header"][2])[0]
changed = {"/Library/Data", "/Library/ComponentParamsTOC/Data", "/Library/Models/Data", "/Library/Models/Header"}
for k in a:
    if k not in changed:
        assert a[k] == b[k], k
extra = {k for k in b if k not in a}
src_fp = {k[len("/" + PART["src_fp"]):] for k in src if k.startswith("/" + PART["src_fp"])}
s_n = struct.unpack("<I", src["/Library/Models/Header"][2])[0]
assert extra == {fp + k for k in src_fp} | {f"/Library/Models/{nmod + i}" for i in range(s_n)}, extra
for i in range(s_n):
    assert b[f"/Library/Models/{nmod + i}"][2] == src[f"/Library/Models/{i}"][2]
for k in src_fp - {"/Data", "/Parameters"}:
    assert b[fp + k] == src["/" + PART["src_fp"] + k], k
name, prims = pcbparse.walk(b[fp + "/Data"][2])
assert name == PART["fp"]
_, sprims = pcbparse.walk(src["/" + PART["src_fp"] + "/Data"][2])
assert prims == sprims
pr = m.kv(m.parse(b[fp + "/Parameters"][2])[0][1])
assert m.get(pr, b"PATTERN") == PART["fp"].encode() and m.get(pr, b"DESCRIPTION") == PART["fp_desc"].encode()
d = b["/Library/Data"][2]
hl = struct.unpack_from("<I", d)[0] & 0xFFFFFF
assert d[:4 + hl] == a["/Library/Data"][2][:4 + hl]
i = 4 + hl
cnt = struct.unpack_from("<I", d, i)[0]; i += 4
names = []
for _ in range(cnt):
    nm, i = read_name_block(d, i); names.append(nm)
assert i == len(d)
storages = {k[1:] for k in b if k.count("/") == 1 and k[1:] not in ("Library", "FileHeader", "FileVersionInfo")}
assert sorted(names) == sorted(storages), (names, storages)
toc = m.parse(b["/Library/ComponentParamsTOC/Data"][2])[0][1][:-3].split(b"\r\n")
assert sorted(ln.split(b"|")[0][5:].decode() for ln in toc) == sorted(names)
assert any(ln.startswith(b"Name=" + PART["fp"].encode() + b"|") and PART["fp_desc"].encode() in ln for ln in toc)
models = m.parse(b["/Library/Models/Data"][2])
assert len(models) == struct.unpack("<I", b["/Library/Models/Header"][2])[0] == nmod + s_n
print("PcbLib OK:", cnt, "footprints,", len(models), "embedded models,", len(prims), "primitives in", PART["fp"])
