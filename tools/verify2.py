import sys, os, glob, olefile
W=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,W)
import cfb, migrate as m
from rename_map import R
def t(pr,k):
    u=m.get(pr,b"%UTF8%"+k); return u.decode() if u is not None else (m.get(pr,k) or b"").decode("cp1252")
errs=[]; n=0
for g in sorted(glob.glob(sys.argv[2]+"/*.SchLib")):
    f=os.path.join(sys.argv[1],os.path.basename(g)); lib=os.path.basename(g)[:-7]
    olefile.OleFileIO(g).close()
    A,B=cfb.read_tree(f),cfb.read_tree(g)
    sa={c.name:c for c in A.children}; sb={c.name:c for c in B.children}
    for nm in ("Storage",): 
        if sa[nm].data!=sb[nm].data: errs.append((lib,"Storage changed"))
    # FileHeader: only LibRef/CompDescr keys may differ
    fa=m.kv(m.parse(sa["FileHeader"].data)[0][1]); fb=m.kv(m.parse(sb["FileHeader"].data)[0][1])
    strip=lambda p:[x for x in p if not x[0].lstrip(b"%UTF8%").startswith((b"LibRef",b"CompDescr"))]
    if strip(fa)!=strip(fb): errs.append((lib,"FileHeader other keys changed"))
    ca=[c for c in A.children if c.kind==1]; cb=[c for c in B.children if c.kind==1]
    if len(ca)!=len(cb): errs.append((lib,"component count"))
    fhnames=[t(fb,f"LibRef{i}".encode()) for i in range(int(m.get(fb,b"CompCount")))]
    def ref(st):
        c=m.kv(m.parse([s for s in st.children if s.name=="Data"][0].data)[0][1]); return t(c,b"LibReference")
    rev={(l,v["name"]):o for (l,o),v in R.items()}
    byold={ref(x):x for x in ca}
    pairs=[(byold[rev[(lib,ref(y))]],y) for y in cb]
    if len(set(id(p[0]) for p in pairs))!=len(ca): errs.append((lib,"pairing"))
    for x,y in pairs:
        n+=1
        da={s.name:s.data for s in x.children}; db={s.name:s.data for s in y.children}
        if da.keys()!=db.keys(): errs.append((lib,x.name,"substreams")); continue
        for k in da:
            if k!="Data" and da[k]!=db[k]: errs.append((lib,x.name,"stream",k))
        ra,rb=m.parse(da["Data"]),m.parse(db["Data"])
        keep=lambda rs:[r for r in rs[1:] if not (r[0]==0 and m.get(m.kv(r[1]),b"RECORD")==b"34")]
        if keep(ra)!=keep(rb): errs.append((lib,x.name,"other records changed"))
        c0,c1=m.kv(ra[0][1]),m.kv(rb[0][1])
        old=t(c0,b"LibReference"); e=R[(lib,old)]
        ign=(b"LibReference",b"%UTF8%LibReference",b"ComponentDescription",b"%UTF8%ComponentDescription",b"DesignItemId")
        if [p for p in c0 if p[0] not in ign]!=[p for p in c1 if p[0] not in ign]: errs.append((lib,old,"other comp keys changed"))
        got=(t(c1,b"LibReference"),t(c1,b"DesignItemId"),t(c1,b"ComponentDescription"),
             [t(m.kv(r[1]),b"Text") for r in rb if r[0]==0 and m.get(m.kv(r[1]),b"RECORD")==b"34"], y.name)
        exp=(e["name"],e["name"],e["desc"],[e["des"]+"?"],e["name"].replace("/","_")[:31])
        if got!=exp: errs.append((lib,old,got,exp))
        if e["name"] not in fhnames: errs.append((lib,old,"not in FileHeader"))
print(n,"components checked;",len(errs),"problems")
for x in errs[:20]: print(x)
