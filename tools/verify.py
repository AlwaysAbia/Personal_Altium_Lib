import sys, glob, os, olefile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cfb, migrate as m
M=m.MAP; errs=[]; n=0
def txt(pr):
    u=m.get(pr,b"%UTF8%Text")
    return u.decode("utf-8") if u is not None else (m.get(pr,b"Text") or b"").decode("cp1252")
src_dir,out_dir=sys.argv[1],sys.argv[2]
for g in sorted(glob.glob(out_dir+"/*.SchLib")):
    f=os.path.join(src_dir,os.path.basename(g)); lib=os.path.basename(f)[:-7]
    olefile.OleFileIO(g).close()
    a,b=cfb.flat(cfb.read_tree(f)),cfb.flat(cfb.read_tree(g))
    if a.keys()!=b.keys(): errs.append((lib,"tree differs"))
    for p in a:
        if not p.endswith("/Data"):
            if a[p]!=b[p]: errs.append((lib,"stream changed",p))
            continue
        ra,rb=m.parse(a[p][2]),m.parse(b[p][2])
        isp=lambda r: r[0]==0 and m.get(m.kv(r[1]),b"RECORD")==b"41"
        if [r for r in ra if not isp(r)]!=[r for r in rb if not isp(r)]: errs.append((lib,"non-param records changed",p))
        comp=m.kv(next(r[1] for r in rb if r[0]==0 and b"|RECORD=1|" in r[1]))
        u=m.get(comp,b"%UTF8%LibReference"); ref=u.decode() if u else m.get(comp,b"LibReference").decode("cp1252")
        r=M[(lib,ref)]; n+=1
        old={m.get(m.kv(x[1]),b"Name").decode():txt(m.kv(x[1])) for x in ra if isp(x)}
        got={m.get(m.kv(x[1]),b"Name").decode():txt(m.kv(x[1])) for x in rb if isp(x)}
        exp={"Value":r["value"],"Manufacturer":r["mfr"],"Manufacturer Part Number":r["mpn"],"Comment":r["comment_new"]}
        for i,(d,u) in enumerate(r["links"],1): exp[f"ComponentLink{i}Description"]=d; exp[f"ComponentLink{i}URL"]=u
        if "note" in old: exp["note"]=old["note"] if not old["note"].startswith("http") else ""
        for k,v in exp.items():
            if got.get(k)!=v: errs.append((lib,ref,k,got.get(k),v))
        if set(got)-set(exp): errs.append((lib,ref,"extra",set(got)-set(exp)))
print(n,"components checked;",len(errs),"problems")
for e in errs[:30]: print(e)
