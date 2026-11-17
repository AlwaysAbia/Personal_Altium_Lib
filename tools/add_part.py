"""Add a vendor-downloaded part (e.g. Ultra Librarian SchLib + PcbLib) to the library, standardized.

Edit PART below, then:
  add_part.py <src.SchLib> <src.PcbLib> <dst.SchLib> <dst.PcbLib> <out_dir>

Writes <out_dir>/<dst SchLib name> and <out_dir>/<dst PcbLib name>; the originals are not touched.
SchLib: the component is copied with vendor parameters dropped, the standard parameter set
added, the description / Design Item ID set, fonts remapped to the destination font table,
the footprint model re-pointed (name only) and OwnerIndex recomputed.
PcbLib: the footprint is copied under its standard name together with its embedded 3D model,
and the library footprint list, ComponentParamsTOC and model list are extended.
"""
import sys, os, struct, random, string
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfb, migrate as m
from apply_fp import name_block, read_name_block, kv_stream_get, kv_stream_set

PART = dict(
    src_comp="STM32H562RGT6",
    name="STM32H562RGT6",
    desc="MCU ARM Cortex-M33 250MHz 1MB Flash 640KB RAM, LQFP-64",
    note="Original",
    value="",
    mfr="STMicroelectronics",
    mpn="STM32H562RGT6",
    links=[("LCSC", "https://www.lcsc.com/product-detail/C19711662.html")],
    src_fp="LQFP64-10x10mm_STM",
    fp="LQFP-64_10x10mm_P0.5mm",
    fp_desc="LQFP-64, 10x10mm body, 0.5mm pitch",
)
VENDOR_PARAMS = {b"Copyright", b"Manufacturer_Name", b"Manufacturer_Part_Number", b"Description", b"RefDes", b"Type"}
FONT_KEYS = (b"Size", b"FontName", b"Rotation", b"Bold", b"Italic", b"Underline", b"StrikeOut")
HIDDEN_Y = b"-530"  # parameter location used by the other MCUs in IC_Digital


def fonts(hdr):
    n = int(m.get(hdr, b"FontIdCount"))
    return {i: tuple(m.get(hdr, k + str(i).encode()) for k in FONT_KEYS) for i in range(1, n + 1)}


def uid(used):
    while True:
        u = "".join(random.choice(string.ascii_uppercase) for _ in range(8)).encode()
        if u not in used:
            used.add(u)
            return u


def param(name, text, idx, used, font=b"1"):
    p = [(b"RECORD", b"41")]
    if idx is not None:
        p.append((b"IndexInSheet", str(idx).encode()))
    p += [(b"OwnerPartId", b"-1"), (b"Location.X", b"-5"), (b"Location.Y", HIDDEN_Y), (b"Color", b"8388608"),
          (b"FontID", font), (b"IsHidden", b"T")]
    if text:
        p.append((b"Text", text.encode("cp1252")))
    return p + [(b"Name", name.encode("cp1252")), (b"UniqueID", uid(used))]


def add_schlib(src, dst, out):
    st = cfb.read_tree(src)
    dt = cfb.read_tree(dst)
    s_fh = m.kv(m.parse(next(c for c in st.children if c.name == "FileHeader").data)[0][1])
    d_fh_node = next(c for c in dt.children if c.name == "FileHeader")
    d_recs = m.parse(d_fh_node.data)
    assert len(d_recs) == 1
    d_fh = m.kv(d_recs[0][1])

    comp = next(c for c in st.children if c.name == PART["src_comp"])
    assert not any(c.name == PART["name"] for c in dt.children), "component already exists"
    data = next(c for c in comp.children if c.name == "Data")
    recs = m.parse(data.data)
    kept = [m.kv(p) for t, p in recs if t == 0]
    kept = [pr for pr in kept if not (m.get(pr, b"RECORD") == b"41" and m.get(pr, b"Name") in VENDOR_PARAMS)]
    used_fonts = {int(m.get(pr, b"FontID")) for pr in kept if m.get(pr, b"FontID") is not None}

    # font remap: reuse an identical destination font, else append one (only fonts still in use).
    # The added parameters use destination fonts 1 / 2 directly, like the other parts in the library.
    dfonts = fonts(d_fh)
    fmap = {}
    for i, f in fonts(s_fh).items():
        if i not in used_fonts:
            continue
        hit = next((j for j, g in dfonts.items() if g == f), None)
        if hit is None:
            hit = len(dfonts) + 1
            dfonts[hit] = f
            for k, v in zip(FONT_KEYS, f):
                if v is not None:
                    d_fh = m.setkey(d_fh, k + str(hit).encode(), v, before=b"UseMBCS")
            d_fh = m.setkey(d_fh, b"FontIdCount", str(hit).encode())
        fmap[str(i).encode()] = str(hit).encode()

    used ={m.get(m.kv(p), b"UniqueID") for t, p in recs if t == 0}

    out_recs, old2new = [], {}
    for i, (t, p) in enumerate(recs):
        if t != 0:
            old2new[i] = len(out_recs)
            out_recs.append([t, p])
            continue
        pr = m.kv(p)
        rec = m.get(pr, b"RECORD")
        if rec == b"41" and m.get(pr, b"Name") in VENDOR_PARAMS:
            continue
        if m.get(pr, b"FontID") is not None:
            pr = m.setkey(pr, b"FontID", fmap[m.get(pr, b"FontID")])
        if rec == b"1":
            assert m.get(pr, b"LibReference") == PART["src_comp"].encode()
            pr = [(k, v) for k, v in pr if not k.startswith(b"%UTF8%")]
            pr = m.setkey(pr, b"LibReference", PART["name"].encode("cp1252"))
            pr = m.setkey(pr, b"ComponentDescription", PART["desc"].encode("cp1252"))
            pr = m.setkey(pr, b"DesignItemId", PART["name"].encode("cp1252"))
            old2new[i] = len(out_recs)
            out_recs.append([0, pr])
            if PART["note"] is not None:  # note sits right after the component record, as in the other parts
                out_recs.append([0, param("note", PART["note"], None, used)])
            continue
        if rec == b"41" and m.get(pr, b"Name") == b"Comment":
            k = 1
            new = [("Value", PART["value"]), ("Manufacturer", PART["mfr"]), ("Manufacturer Part Number", PART["mpn"])]
            for n, (d, u) in enumerate(PART["links"], 1):
                new += [(f"ComponentLink{n}Description", d), (f"ComponentLink{n}URL", u)]
            for name, text in new:
                out_recs.append([0, param(name, text, k, used, b"2" if name.endswith("URL") else b"1")])
                k += 1
            pr = [(a, b) for a, b in pr if a != b"%UTF8%Text"]
            pr = m.setkey(pr, b"Text", b"=Manufacturer Part Number")
        if rec == b"45":
            assert m.get(pr, b"ModelName") == PART["src_fp"].encode() and m.get(pr, b"DatafileCount") == b"1"
            pr = [(a, b) for a, b in pr if a not in (b"ModelDatafile0", b"%UTF8%Description")]
            pr = m.setkey(pr, b"Description", PART["fp_desc"].encode("cp1252"), before=b"ModelName")
            pr = m.setkey(pr, b"ModelName", PART["fp"].encode("cp1252"))
            pr = m.setkey(pr, b"ModelDatafileEntity0", PART["fp"].encode("cp1252"))
            pr = m.setkey(pr, b"ModelDatafileKind0", b"PCBLib")
            pr = m.setkey(pr, b"IsCurrent", b"T", before=b"UniqueID")
        old2new[i] = len(out_recs)
        out_recs.append([0, pr])

    for r in out_recs:
        if r[0] == 0:
            oi = m.get(r[1], b"OwnerIndex")
            if oi is not None:
                r[1] = m.setkey(r[1], b"OwnerIndex", str(old2new[int(oi)]).encode())
            r[1] = m.unkv(r[1])
    data.data = m.serialize(out_recs)
    comp.name = PART["name"].replace("/", "_")[:31]
    assert len(PART["name"]) < 31
    comp.children = [c for c in comp.children if c.name in ("Data", "PinTextData", "PinFrac")]
    dt.children.append(comp)

    n = int(m.get(d_fh, b"CompCount"))
    d_fh = m.setkey(d_fh, b"CompCount", str(n + 1).encode())
    d_fh += [(b"LibRef%d" % n, PART["name"].encode("cp1252")), (b"CompDescr%d" % n, PART["desc"].encode("cp1252")),
             (b"PartCount%d" % n, m.get(s_fh, b"PartCount0"))]
    d_fh = m.setkey(d_fh, b"Weight", str(int(m.get(d_fh, b"Weight")) + len(out_recs)).encode())
    d_recs[0][1] = m.unkv(d_fh)
    d_fh_node.data = m.serialize(d_recs)
    cfb.write_tree(dt, os.path.join(out, os.path.basename(dst)))
    return fmap, len(recs), len(out_recs)


def add_pcblib(src, dst, out):
    st = cfb.read_tree(src)
    dt = cfb.read_tree(dst)
    assert not any(c.name == PART["fp"] for c in dt.children), "footprint already exists"
    fp = next(c for c in st.children if c.name == PART["src_fp"])
    sub = {c.name: c for c in fp.children}
    nm, end = read_name_block(sub["Data"].data)
    assert nm == PART["src_fp"]
    sub["Data"].data = name_block(PART["fp"]) + sub["Data"].data[end:]
    pr = kv_stream_get(sub["Parameters"].data)
    pr = m.setkey(pr, b"PATTERN", PART["fp"].encode("cp1252"))
    pr = m.setkey(pr, b"DESCRIPTION", PART["fp_desc"].encode("cp1252"))
    sub["Parameters"].data = kv_stream_set(pr)
    fp.name = PART["fp"]
    dt.children.append(fp)

    SL = {c.name: c for c in next(c for c in st.children if c.name == "Library").children}
    DL = {c.name: c for c in next(c for c in dt.children if c.name == "Library").children}

    # footprint list
    d = DL["Data"]
    hl = struct.unpack_from("<I", d.data)[0] & 0xFFFFFF
    i = 4 + hl
    n = struct.unpack_from("<I", d.data, i)[0]
    d.data = d.data[:i] + struct.pack("<I", n + 1) + d.data[i + 4:] + name_block(PART["fp"])

    # ComponentParamsTOC: take the source line, rename it
    def toc_lines(L):
        s = next(c for c in L["ComponentParamsTOC"].children if c.name == "Data")
        recs = m.parse(s.data)
        assert len(recs) == 1 and recs[0][1].endswith(b"\r\n\x00")
        return s, recs, recs[0][1][:-3].split(b"\r\n")
    _, _, src_lines = toc_lines(SL)
    line = next(ln for ln in src_lines if ln.startswith(b"Name=" + PART["src_fp"].encode() + b"|"))
    p = [x.split(b"=", 1) for x in line.split(b"|")]
    p = [[k, PART["fp"].encode()] if k == b"Name" else [k, PART["fp_desc"].encode()] if k == b"Description" else [k, v] for k, v in p]
    s, recs, lines = toc_lines(DL)
    lines.append(b"|".join(k + b"=" + v for k, v in p))
    recs[0][1] = b"".join(x + b"\r\n" for x in lines) + b"\x00"
    s.data = m.serialize(recs)

    # embedded 3D models: append every source model (the footprint's 3D body refers to it by ID)
    sm = {c.name: c for c in SL["Models"].children}
    dm = {c.name: c for c in DL["Models"].children}
    s_n = struct.unpack("<I", sm["Header"].data)[0]
    d_n = struct.unpack("<I", dm["Header"].data)[0]
    s_list = m.parse(sm["Data"].data)
    d_list = m.parse(dm["Data"].data)
    assert len(s_list) == s_n and len(d_list) == d_n
    d_ids = {x for _, p in d_list for x in p.split(b"|") if x.startswith(b"ID=")}
    for k in range(s_n):
        assert not ({x for x in s_list[k][1].split(b"|") if x.startswith(b"ID=")} & d_ids), "model ID clash"
        node = sm[str(k)]
        node.name = str(d_n + k)
        DL["Models"].children.append(node)
    dm["Data"].data = m.serialize(d_list + s_list)
    dm["Header"].data = struct.pack("<I", d_n + s_n)
    cfb.write_tree(dt, os.path.join(out, os.path.basename(dst)))
    return n + 1, d_n + s_n


if __name__ == "__main__":
    ss, sp, ds, dp, out = sys.argv[1:6]
    os.makedirs(out, exist_ok=True)
    fmap, a, b = add_schlib(ss, ds, out)
    print(os.path.basename(ds), "added", PART["name"], f"({a} -> {b} records), font map", {k.decode(): v.decode() for k, v in fmap.items()})
    nfp, nmod = add_pcblib(sp, dp, out)
    print(os.path.basename(dp), "added", PART["fp"], f"({nfp} footprints, {nmod} embedded models)")
