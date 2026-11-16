import sys, os, glob, struct, olefile
W=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,W)
import cfb, migrate as m, pcbparse as P
from apply_fp import kv_stream_get, read_name_block, fp_target, SPECIAL
from fp_map import F, MISSING
pb, sb, po, so = sys.argv[1:5]
errs=[]; allfp={}
for f in sorted(glob.glob(po+"/*.PcbLib")):
    lib=os.path.basename(f)[:-7]
    olefile.OleFileIO(f).close()
    A=cfb.read_tree(os.path.join(pb,os.path.basename(f))); B=cfb.read_tree(f)
    def fps(t):
        out={}
        for st in t.children:
            if st.kind==1 and st.name not in SPECIAL:
                sub={s.name:s for s in st.children}
                out[m.get(kv_stream_get(sub["Parameters"].data),b"PATTERN").decode("cp1252")]=(st,sub)
        return out
    fa,fb=fps(A),fps(B)
    exp={F[(lib,o)]["name"]:o for o in fa if F[(lib,o)]["name"]}
    if set(fb)!=set(exp): errs.append((lib,"footprint set",set(fb)^set(exp)))
    for new,(st,sub) in fb.items():
        allfp.setdefault(new,[]).append(lib)
        o=exp[new]; sa=fa[o][1]; v=F[(lib,o)]
        if st.name!=new[:31]: errs.append((lib,new,"storage name"))
        if sa.keys()!=sub.keys(): errs.append((lib,new,"substreams")); continue
        for k in sa:
            if sa[k].kind==2 and k not in ("Data","Parameters") and sa[k].data!=sub[k].data: errs.append((lib,new,"stream",k))
            if sa[k].kind==1 and cfb.flat(sa[k])!=cfb.flat(sub[k]): errs.append((lib,new,"storage",k))
        na,ea=read_name_block(sa["Data"].data); nb,eb=read_name_block(sub["Data"].data)
        if na!=o or nb!=new or sa["Data"].data[ea:]!=sub["Data"].data[eb:]: errs.append((lib,new,"Data body"))
        P.walk(sub["Data"].data)
        pa=kv_stream_get(sa["Parameters"].data); pq=kv_stream_get(sub["Parameters"].data)
        if [x for x in pa if x[0] not in (b"PATTERN",b"DESCRIPTION")]!=[x for x in pq if x[0] not in (b"PATTERN",b"DESCRIPTION")]: errs.append((lib,new,"params"))
        if m.get(pq,b"DESCRIPTION").decode()!=v["desc"]: errs.append((lib,new,"desc"))
    sa={c.name:c for c in A.children}; sbb={c.name:c for c in B.children}
    for k in ("FileHeader","FileVersionInfo"):
        if cfb.flat(sa[k])!=cfb.flat(sbb[k]) if sa[k].kind==1 else sa[k].data!=sbb[k].data: errs.append((lib,k))
    if "SectionKeys" in sbb: errs.append((lib,"SectionKeys left"))
    LA={c.name:c for c in sa["Library"].children}; LB={c.name:c for c in sbb["Library"].children}
    for k in LA:
        if k in ("Data","ComponentParamsTOC"): continue
        if (cfb.flat(LA[k])!=cfb.flat(LB[k])) if LA[k].kind==1 else LA[k].data!=LB[k].data: errs.append((lib,"Library/"+k))
    d=LB["Data"].data; hl=struct.unpack_from("<I",d)[0]&0xffffff
    if d[:4+hl]!=LA["Data"].data[:4+hl]: errs.append((lib,"Library header"))
    i=4+hl; n=struct.unpack_from("<I",d,i)[0]; i+=4; lst=[]
    for _ in range(n): nm,i=read_name_block(d,i); lst.append(nm)
    if i!=len(d) or sorted(lst)!=sorted(fb): errs.append((lib,"Library list"))
    toc=[s for s in LB["ComponentParamsTOC"].children if s.name=="Data"][0].data.decode("cp1252")
    tn=sorted(l.split("|")[0].split("Name=")[1] for l in toc[4:].split("\r\n") if "Name=" in l)
    if tn!=sorted(fb): errs.append((lib,"TOC",set(tn)^set(fb)))
dup=[k for k,v in allfp.items() if len(v)>1]
if dup: errs.append(("duplicate footprint names across libs",dup))
# SchLib side
links=0; trimmer=[]
for g in sorted(glob.glob(so+"/*.SchLib")):
    lib=os.path.basename(g)[:-7]
    A=cfb.read_tree(os.path.join(sb,os.path.basename(g))); B=cfb.read_tree(g)
    if [c.name for c in A.children]!=[c.name for c in B.children]: errs.append((lib,"sch tree"))
    for x,y in zip(A.children,B.children):
        if x.kind!=1:
            if x.data!=y.data: errs.append((lib,x.name)); 
            continue
        da={s.name:s.data for s in x.children}; db={s.name:s.data for s in y.children}
        for k in da:
            if k!="Data" and da[k]!=db[k]: errs.append((lib,x.name,k))
        ra,rb=m.parse(da["Data"]),m.parse(db["Data"])
        ref=m.get(m.kv(ra[0][1]),b"LibReference").decode("cp1252")
        for p,q in zip(ra,rb):
            is45=p[0]==0 and m.get(m.kv(p[1]),b"RECORD")==b"45"
            if not is45:
                if p!=q: errs.append((lib,ref,"non-model record changed"))
                continue
            pa,pq=m.kv(p[1]),m.kv(q[1]); ign=(b"ModelName",b"ModelDatafileEntity0",b"Description")
            if [z for z in pa if z[0] not in ign]!=[z for z in pq if z[0] not in ign]: errs.append((lib,ref,"model other keys"))
            old=m.get(pa,b"ModelName").decode(); new=m.get(pq,b"ModelName").decode(); links+=1
            want=fp_target(old) or MISSING.get((lib,ref,old))
            if new!=want or m.get(pq,b"ModelDatafileEntity0").decode()!=new: errs.append((lib,ref,"model name",old,new,want))
            if new not in allfp:
                if (lib,ref,old) in MISSING: trimmer.append(ref)
                else: errs.append((lib,ref,"link resolves to no footprint",new))
        # OwnerIndex still points at right types
        typ=[m.get(m.kv(p),b"RECORD") if t==0 else None for t,p in rb]
        for t,p in rb:
            if t==0:
                pr=m.kv(p); oi=m.get(pr,b"OwnerIndex")
                if oi is not None and (typ[int(oi)],m.get(pr,b"RECORD")) not in ((b"44",b"45"),(b"45",b"46"),(b"45",b"48")): errs.append((lib,ref,"owner"))
print(len(allfp),"footprints;",links,"schematic links;","unlinked (expected):",trimmer,";",len(errs),"problems")
for e in errs[:25]: print(e)
