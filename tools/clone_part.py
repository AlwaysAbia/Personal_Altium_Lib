"""Add a part to a SchLib by cloning an existing component of the same library (same symbol, new identity).

Edit PART below, then:
  clone_part.py <src.SchLib> <out_dir>

Writes <out_dir>/<src SchLib name>; the original is not touched. The clone keeps the source symbol
and parameter layout; component name, description, Design Item ID, Manufacturer, Manufacturer Part
Number, note, links and footprint model are replaced, UniqueIDs are regenerated, and pin designators
are remapped (e.g. a 2-pin diode symbol moved onto SOT-23 pads 1 / 3). The record count is unchanged,
so OwnerIndex links stay valid. The footprint is linked by name only and must already exist in a
PcbLib of the project.
"""
import sys, os, random, string
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfb, migrate as m

PART = dict(
    src_comp="SS16",
    name="BAS116,215",
    desc="Switching Diode 85V 215mA Low Leakage, SOT-23",
    note="*",
    mfr="Nexperia",
    mpn="BAS116,215",
    links=[("LCSC", "https://www.lcsc.com/product-detail/C48502.html")],
    fp="SOT-23-3",
    fp_desc="SOT-23-3, 2.9x1.3mm body, 0.95mm pitch",
    # source pin designator -> new designator (pin name follows). SS16: 1 = K, 2 = A.
    # BAS116 SOT-23: pad 1 = A, pad 2 = n.c., pad 3 = K.
    pins={b"1": b"3", b"2": b"1"},
)


def uid(used):
    while True:
        u = "".join(random.choice(string.ascii_uppercase) for _ in range(8)).encode()
        if u not in used:
            used.add(u)
            return u


def remap_pin(p):
    # binary pin record: ... | len | designator-name ... ; SS16 pins carry "\x01<d>\x01<d>" (name, designator)
    for old, new in PART["pins"].items():
        pat = b"\x01" + old + b"\x01" + old + b"\x00"
        if pat in p:
            assert p.count(pat) == 1 and len(old) == len(new)
            return p.replace(pat, b"\x01" + new + b"\x01" + new + b"\x00"), old
    raise ValueError("pin pattern not found: " + p.hex())


def main(src, out):
    t = cfb.read_tree(src)
    assert not any(c.name == PART["name"][:31] for c in t.children), "component already exists"
    fh_node = next(c for c in t.children if c.name == "FileHeader")
    fh_recs = m.parse(fh_node.data)
    assert len(fh_recs) == 1
    fh = m.kv(fh_recs[0][1])

    srcc = next(c for c in t.children if c.name == PART["src_comp"])
    clone = cfb.read_tree(src)  # fresh copy of the source storage
    comp = next(c for c in clone.children if c.name == PART["src_comp"])
    data = next(c for c in comp.children if c.name == "Data")
    recs = m.parse(data.data)
    used = set()
    seen_pins = set()
    out_recs = []
    for ty, p in recs:
        if ty == 1:
            p, old = remap_pin(p)
            seen_pins.add(old)
            out_recs.append([ty, p])
            continue
        pr = m.kv(p)
        pr = [(k, v) for k, v in pr if not k.startswith(b"%UTF8%")]
        rec = m.get(pr, b"RECORD")
        if m.get(pr, b"UniqueID") is not None:
            pr = m.setkey(pr, b"UniqueID", uid(used))
        if rec == b"1":
            pr = m.setkey(pr, b"LibReference", PART["name"].encode("cp1252"))
            pr = m.setkey(pr, b"ComponentDescription", PART["desc"].encode("cp1252"))
            pr = m.setkey(pr, b"DesignItemId", PART["name"].encode("cp1252"))
        elif rec == b"41":
            n = m.get(pr, b"Name")
            links = {}
            for i, (d, u) in enumerate(PART["links"], 1):
                links[f"ComponentLink{i}Description".encode()] = d
                links[f"ComponentLink{i}URL".encode()] = u
            new = {b"note": PART["note"], b"Manufacturer": PART["mfr"],
                   b"Manufacturer Part Number": PART["mpn"], **links}
            if n in new:
                pr = m.setkey(pr, b"Text", new[n].encode("cp1252"), before=b"Name")
            else:
                assert n in (b"Value", b"Comment"), n
        elif rec == b"45":
            pr = m.setkey(pr, b"Description", PART["fp_desc"].encode("cp1252"))
            pr = m.setkey(pr, b"ModelName", PART["fp"].encode("cp1252"))
            pr = m.setkey(pr, b"ModelDatafileEntity0", PART["fp"].encode("cp1252"))
            assert m.get(pr, b"ModelDatafile0") is None
        out_recs.append([0, m.unkv(pr)])
    assert seen_pins == set(PART["pins"]), seen_pins
    assert len(out_recs) == len(recs)
    data.data = m.serialize(out_recs)
    comp.name = PART["name"].replace("/", "_")[:31]
    assert len(PART["name"]) < 31
    t.children.append(comp)

    n = int(m.get(fh, b"CompCount"))
    fh = m.setkey(fh, b"CompCount", str(n + 1).encode())
    fh += [(b"LibRef%d" % n, PART["name"].encode("cp1252")), (b"CompDescr%d" % n, PART["desc"].encode("cp1252")),
           (b"PartCount%d" % n, m.get(fh, b"PartCount%d" % [i for i in range(n) if m.get(fh, b"LibRef%d" % i) == PART["src_comp"].encode()][0]))]
    if m.get(fh, b"Weight") is not None:
        fh = m.setkey(fh, b"Weight", str(int(m.get(fh, b"Weight")) + len(out_recs)).encode())
    fh_recs[0][1] = m.unkv(fh)
    fh_node.data = m.serialize(fh_recs)
    os.makedirs(out, exist_ok=True)
    cfb.write_tree(t, os.path.join(out, os.path.basename(src)))
    print(os.path.basename(src), "added", PART["name"], "cloned from", PART["src_comp"], f"({len(out_recs)} records)")


if __name__ == "__main__":
    main(*sys.argv[1:3])
