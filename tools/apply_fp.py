"""Apply fp_map to PcbLibs and re-tie SchLib model records.
Usage: apply_fp.py <pcb_src_dir> <sch_src_dir> <pcb_out_dir> <sch_out_dir>"""
import sys, os, glob, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfb, migrate as m
from fp_map import F, MISSING

SPECIAL = {"Library", "FileVersionInfo", "FileHeader", "SectionKeys"}


def name_block(name):
    b = name.encode("cp1252")
    return struct.pack("<IB", len(b) + 1, len(b)) + b


def read_name_block(data, i=0):
    bl = struct.unpack_from("<I", data, i)[0]
    return data[i + 5:i + 4 + bl].decode("cp1252"), i + 4 + bl


def kv_stream_get(data):
    recs = m.parse(data)
    assert len(recs) == 1
    return m.kv(recs[0][1])


def kv_stream_set(pairs):
    return m.serialize([[0, m.unkv(pairs)]])


def apply_pcblib(src, dst):
    lib = os.path.basename(src)[:-7]
    root = cfb.read_tree(src)
    kept, removed = [], []
    newchildren = []
    for st in root.children:
        if st.kind != 1 or st.name in SPECIAL:
            newchildren.append(st)
            continue
        sub = {s.name: s for s in st.children}
        pr = kv_stream_get(sub["Parameters"].data)
        old = m.get(pr, b"PATTERN").decode("cp1252")
        v = F[(lib, old)]
        if not v["name"]:
            removed.append(old)
            continue
        nm, end = read_name_block(sub["Data"].data)
        assert nm == old, (nm, old)
        sub["Data"].data = name_block(v["name"]) + sub["Data"].data[end:]
        pr = m.setkey(pr, b"PATTERN", v["name"].encode("cp1252"))
        pr = m.setkey(pr, b"DESCRIPTION", v["desc"].encode("cp1252"))
        sub["Parameters"].data = kv_stream_set(pr)
        st.name = v["name"].replace("/", "_")[:31]
        assert len(v["name"]) < 31
        kept.append((old, v["name"]))
        newchildren.append(st)
    root.children = [c for c in newchildren if c.name != "SectionKeys"]
    ren = dict(kept)

    L = next(c for c in root.children if c.name == "Library")
    d = next(s for s in L.children if s.name == "Data")
    hl = struct.unpack_from("<I", d.data)[0] & 0xFFFFFF
    head, i = d.data[:4 + hl], 4 + hl
    n = struct.unpack_from("<I", d.data, i)[0]; i += 4
    names = []
    for _ in range(n):
        nm, i = read_name_block(d.data, i); names.append(nm)
    assert i == len(d.data)
    assert sorted(names) == sorted(list(ren) + removed), lib
    out = [ren[x] for x in names if x in ren]
    d.data = head + struct.pack("<I", len(out)) + b"".join(name_block(x) for x in out)

    toc = next(s for s in next(c for c in L.children if c.name == "ComponentParamsTOC").children if s.name == "Data")
    recs = m.parse(toc.data); assert len(recs) == 1
    text = recs[0][1]
    assert text.endswith(b"\r\n\x00")
    lines = text[:-3].split(b"\r\n")
    newlines = []
    for ln in lines:
        p = [x.split(b"=", 1) for x in ln.split(b"|")]
        old = p[0][1].decode("cp1252")
        if old not in ren:
            continue
        v = F[(lib, old)]
        p = [[k, v["name"].encode("cp1252")] if k == b"Name" else [k, v["desc"].encode("cp1252")] if k == b"Description" else [k, val] for k, val in p]
        newlines.append(b"|".join(k + b"=" + val for k, val in p))
    assert len(newlines) == len(ren), (lib, len(newlines), len(ren))
    recs[0][1] = b"".join(x + b"\r\n" for x in newlines) + b"\x00"
    toc.data = m.serialize(recs)
    cfb.write_tree(root, dst)
    return len(kept), removed


def fp_target(model):
    hits = {(F[k]["name"] or F[k]["merge"]) for k in F if k[1] == model}
    assert len(hits) <= 1, (model, hits)
    return hits.pop() if hits else None


DESC = {v["name"]: v["desc"] for v in F.values() if v["name"]}


def apply_schlib(src, dst):
    lib = os.path.basename(src)[:-7]
    root = cfb.read_tree(src)
    n = 0
    for st in root.children:
        if st.kind != 1:
            continue
        d = next(s for s in st.children if s.name == "Data")
        recs = m.parse(d.data)
        ref = m.get(m.kv(recs[0][1]), b"LibReference").decode("cp1252")
        for rec in recs:
            if rec[0] != 0:
                continue
            pr = m.kv(rec[1])
            if m.get(pr, b"RECORD") != b"45" or m.get(pr, b"ModelType") != b"PCBLIB":
                continue
            old = m.get(pr, b"ModelName").decode("cp1252")
            new = fp_target(old) or MISSING[(lib, ref, old)]
            assert m.get(pr, b"DatafileCount") == b"1" and m.get(pr, b"ModelDatafileEntity0").decode("cp1252") == old
            pr = m.setkey(pr, b"ModelName", new.encode("cp1252"))
            pr = m.setkey(pr, b"ModelDatafileEntity0", new.encode("cp1252"))
            pr = m.setkey(pr, b"Description", DESC.get(new, "").encode("cp1252") or None, before=b"ModelName")
            rec[1] = m.unkv(pr)
            n += 1
        d.data = m.serialize(recs)
    cfb.write_tree(root, dst)
    return n


if __name__ == "__main__":
    ps, ss, po, so = sys.argv[1:5]
    for f in sorted(glob.glob(ps + "/*.PcbLib")):
        k, rm = apply_pcblib(f, os.path.join(po, os.path.basename(f)))
        print(os.path.basename(f), k, "kept, removed:", rm)
    for f in sorted(glob.glob(ss + "/*.SchLib")):
        print(os.path.basename(f), apply_schlib(f, os.path.join(so, os.path.basename(f))), "model links re-tied")
