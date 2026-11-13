"""Minimal OLE compound file (CFB v3) read-into-tree / write-from-tree, enough for Altium SchLib files."""
import olefile, struct, uuid

FREE, EOC, FATSECT, NOSTREAM = 0xFFFFFFFF, 0xFFFFFFFE, 0xFFFFFFFD, 0xFFFFFFFF
SS, MSS, CUTOFF = 512, 64, 4096


class Node:
    def __init__(self, name, kind, clsid=b"\0" * 16, ctime=0, mtime=0, state=0, data=b""):
        self.name, self.kind, self.clsid, self.ctime, self.mtime, self.state, self.data = name, kind, clsid, ctime, mtime, state, data
        self.children = []  # for storages / root


def read_tree(path):
    o = olefile.OleFileIO(path)

    def conv(d):
        clsid = uuid.UUID(d.clsid).bytes_le if d.clsid else b"\0" * 16
        kind = {olefile.STGTY_ROOT: 5, olefile.STGTY_STORAGE: 1, olefile.STGTY_STREAM: 2}[d.entry_type]
        n = Node(d.name, kind, clsid, d.createTime or 0, d.modifyTime or 0, d.dwUserFlags or 0)
        if kind == 2:
            n.data = o._open(d.isectStart, d.size, force_FAT=False).read() if False else None
        return n

    def walk(d, path_parts):
        n = conv(d)
        if n.kind == 2:
            n.data = o.openstream(path_parts).read()
        for k in d.kids:
            n.children.append(walk(k, path_parts + [k.name]))
        return n

    root = walk(o.root, [])
    o.close()
    return root


def _cmp_key(name):
    return (len(name), name.upper())


def write_tree(root, path):
    sectors = []      # list of bytes (512 each)
    fat = []

    def add_chain(data):
        if not data:
            return EOC
        n = (len(data) + SS - 1) // SS
        start = len(sectors)
        padded = data + b"\0" * (n * SS - len(data))
        for i in range(n):
            sectors.append(padded[i * SS:(i + 1) * SS])
            fat.append(start + i + 1 if i < n - 1 else EOC)
        return start

    ministream = bytearray()
    minifat = []

    def add_mini(data):
        if not data:
            return EOC
        n = (len(data) + MSS - 1) // MSS
        start = len(ministream) // MSS
        ministream.extend(data + b"\0" * (n * MSS - len(data)))
        for i in range(n):
            minifat.append(start + i + 1 if i < n - 1 else EOC)
        return start

    # flatten entries; root is sid 0
    entries = []

    def collect(n):
        n.sid = len(entries)
        entries.append(n)
        for c in n.children:
            collect(c)
    collect(root)

    # stream data placement
    for n in entries:
        n.start, n.size = EOC, 0
        if n.kind == 2:
            n.size = len(n.data)
            n.start = add_mini(n.data) if n.size < CUTOFF else add_chain(n.data)
    root.start = add_chain(bytes(ministream))
    root.size = len(ministream)
    if not ministream:
        root.start = EOC
    mf = b"".join(struct.pack("<I", x) for x in minifat)
    first_minifat = add_chain(mf + b"\xff" * ((-len(mf)) % SS)) if minifat else EOC
    n_minifat = (len(mf) + SS - 1) // SS

    # tree links: balanced BST of each storage's children, all black
    for n in entries:
        n.left = n.right = n.child = NOSTREAM

    def build(kids):
        if not kids:
            return NOSTREAM
        m = len(kids) // 2
        k = kids[m]
        k.left = build(kids[:m])
        k.right = build(kids[m + 1:])
        return k.sid

    for n in entries:
        if n.kind in (1, 5):
            kids = sorted(n.children, key=lambda c: _cmp_key(c.name))
            n.child = build(kids)

    def dir_entry(n):
        nm = n.name.encode("utf-16-le") + b"\0\0"
        assert len(nm) <= 64, n.name
        return (nm.ljust(64, b"\0") + struct.pack("<HBB", len(nm), n.kind, 1) +
                struct.pack("<III", n.left, n.right, n.child) + n.clsid +
                struct.pack("<IQQIII", n.state, n.ctime, n.mtime, n.start, n.size & 0xFFFFFFFF, 0))

    empty = b"\0" * 64 + struct.pack("<HBB", 0, 0, 0) + struct.pack("<III", NOSTREAM, NOSTREAM, NOSTREAM) + b"\0" * 16 + struct.pack("<IQQIII", 0, 0, 0, 0, 0, 0)
    d = b"".join(dir_entry(n) for n in entries)
    while len(d) % SS:
        d += empty
    first_dir = add_chain(d)

    # FAT sectors
    nsec = len(sectors)
    k = 1
    while (nsec + k + 127) // 128 > k:
        k += 1
    assert k <= 109, "file too large for header DIFAT"
    fat_start = nsec
    fat.extend([FATSECT] * k)
    fat.extend([FREE] * (k * 128 - len(fat)))
    fatb = b"".join(struct.pack("<I", x) for x in fat)
    for i in range(k):
        sectors.append(fatb[i * SS:(i + 1) * SS])

    difat = [fat_start + i for i in range(k)] + [FREE] * (109 - k)
    hdr = (b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1" + b"\0" * 16 + struct.pack("<HHHHH", 0x3E, 3, 0xFFFE, 9, 6) + b"\0" * 6 +
           struct.pack("<IIIIIIIII", 0, k, first_dir, 0, CUTOFF, first_minifat, n_minifat, EOC, 0) +
           b"".join(struct.pack("<I", x) for x in difat))
    assert len(hdr) == 512
    with open(path, "wb") as f:
        f.write(hdr)
        for s in sectors:
            f.write(s)


def flat(root):
    """{path: (kind, clsid, data)} for comparisons."""
    out = {}

    def walk(n, p):
        out[p] = (n.kind, n.clsid, n.data if n.kind == 2 else None)
        for c in n.children:
            walk(c, p + "/" + c.name)
    walk(root, "")
    return out
