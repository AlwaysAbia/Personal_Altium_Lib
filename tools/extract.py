import olefile, glob, json, re, sys
def kv(r):
    d={}
    for p in r.split("|"):
        if "=" in p: k,v=p.split("=",1); d[k]=v
    return d
out=[]
for f in sorted(glob.glob("SchLib/*.SchLib")):
    o=olefile.OleFileIO(f)
    for s in o.listdir():
        if s[-1]!="Data": continue
        recs=[kv(r.decode('cp1252','replace')) for r in o.openstream(s).read().split(b"\x00") if b"|RECORD=" in r]
        comp=[r for r in recs if r.get("RECORD")=="1"][0]
        p={}
        for r in recs:
            if r.get("RECORD")=="41": p[r.get("Name")]=r.get("%UTF8%Text",r.get("Text",""))
        out.append(dict(lib=f[7:-7],stream=s[0],ref=comp.get("LibReference"),desc=comp.get("%UTF8%ComponentDescription",comp.get("ComponentDescription","")),params=p))
json.dump(out,open(sys.argv[1],"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(out))
