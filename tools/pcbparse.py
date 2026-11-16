import struct
BLOCKS={1:1,2:6,3:1,4:1,5:2,6:1,11:1,12:1}
def walk(data):
    i=0; bl=struct.unpack_from("<I",data,0)[0]; name=data[5:4+bl].decode("cp1252"); i=4+bl
    prims=[]
    while i<len(data):
        t=data[i]; i+=1
        if t not in BLOCKS: raise ValueError(f"unknown prim {t} at {i-1}")
        blocks=[]
        for _ in range(BLOCKS[t]):
            ln=struct.unpack_from("<I",data,i)[0]; blocks.append(data[i+4:i+4+ln]); i+=4+ln
        prims.append((t,blocks))
    assert i==len(data)
    return name,prims
def pads(prims):
    out=[]
    for t,b in prims:
        if t!=2: continue
        nm=b[0][1:1+b[0][0]].decode("cp1252","replace"); g=b[4]
        layer=g[0]
        x,y,sx,sy=struct.unpack_from("<iiii",g,13)
        hole=struct.unpack_from("<i",g,45)[0]
        out.append(dict(name=nm,layer=layer,x=x/1e4*0.0254,y=y/1e4*0.0254,sx=sx/1e4*0.0254,sy=sy/1e4*0.0254,hole=hole/1e4*0.0254))
    return out
