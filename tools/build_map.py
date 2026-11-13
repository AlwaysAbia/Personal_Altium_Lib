# Builds the old -> new parameter mapping for every component (no file writes to the libraries).
import json, os, re, sys
from urllib.parse import urlparse, parse_qs, urlencode

W = os.path.dirname(os.path.abspath(__file__))
comps = json.load(open(os.path.join(W, "data", "comps.json"), encoding="utf-8"))
L = {}
for f in os.listdir(os.path.join(W, "data", "lcsc")):
    j = json.load(open(os.path.join(W, "data", "lcsc", f), encoding="utf-8"))["result"]
    L[f[:-5]] = (j.get("brandNameEn"), j.get("productModel"))

MFR_NAMES = {
    "TI": "Texas Instruments", "ST": "STMicroelectronics", "ADI": "Analog Devices",
    "MAXIM": "Analog Devices (Maxim)", "MICROCHIP": "Microchip", "NXP": "NXP",
    "SILICON LABS": "Silicon Labs", "ESPRESSIF": "Espressif", "SEMTECH": "Semtech",
    "DIODES": "Diodes Incorporated", "TOSHIBA": "Toshiba", "VISHAY": "Vishay",
    "MOLEX": "Molex", "muRata": "Murata", "cjiang": "CJiang",
    "BOOMELE(Boom Precision Elec)": "BOOMELE", "HANRUN(Zhongshan HanRun Elec)": "HanRun",
    "YXC Crystal Oscillators": "YXC", "Dongguan Mentech Optical & Magnetic": "Mentech",
    "BAT WIRELESS": "BAT Wireless", "MYOUNG": "MYOUNG", "hanxia": "Hanxia",
    "SHOU HAN": "SHOU HAN", "XUNPU": "XUNPU", "XINGLIGHT": "XINGLIGHT", "ROQANG": "ROQANG",
    "SEHWA": "SEHWA", "KEMET": "KEMET", "Kyocera AVX": "Kyocera AVX", "ROHM": "ROHM",
    "onsemi": "onsemi", "MATSUKI": "MATSUKI", "Songle Relay": "Songle", "Silergy": "Silergy",
    "Huaneng": "Huaneng", "Littelfuse": "Littelfuse", "TECH PUBLIC": "TECH PUBLIC",
    "R+O": "R+O", "GOODWORK": "GOODWORK", "XUMAO": "XUMAO", "AnBon": "AnBon",
    "EVISUN": "EVISUN", "RLT": "RLT", "HCTL": "HCTL", "Ckmtw": "Ckmtw", "JXTCONN": "JXTCONN",
    "MyAntenna": "MyAntenna", "HenryTech": "HenryTech", "TOGNJING": "TOGNJING", "NDK": "NDK",
    "Winbond": "Winbond", "Seiko": "Seiko", "UMW": "UMW", "MaxLinear": "MaxLinear",
    "TDK": "TDK", "MetalLions": "MetalLions", "Worldsemi": "Worldsemi", "Honor Elec": "Honor Elec",
}

# Per-component decisions. Keys: mpn, mfr, value, flag. Anything not given falls back to LCSC data.
O = {
    # --- parts where the stored val disagrees with the linked LCSC part: keep val, flag it
    "MC146_32.768KHz": dict(mpn="MC-146 32.7680KA-A0:ROHS", mfr="Epson", value="32.768kHz",
        flag="LCSC link points to a different part (Seiko SSP-T7-F). Kept the Epson MC-146 from val."),
    "W25Q128FVSIG": dict(mpn="W25Q128FVSIG", mfr="Winbond",
        flag="LCSC link is W25Q128JVSIQ (newer JV variant), not the FV in val. Kept val."),
    "MIC29302WU": dict(mpn="MIC29302WU", mfr="Microchip",
        flag="LCSC link is a UMW clone (MIC29302WU(UMW)). Kept Microchip as manufacturer."),
    "MIC39100_SOT223": dict(mpn="MIC39100-3.3WS", mfr="Microchip",
        flag="LCSC link is a different part (MaxLinear SPX3940AM3-L-3-3/TR). Kept val."),
    "ACM2012-201-2P-T002": dict(mpn="ACM2012-201-2P-T002", mfr="TDK", value="200Ohm@100MHz 350mA",
        flag="LCSC link is ACM2012-900 (90 Ohm), not -201. Kept val."),
    "ADM3202ARNZ": dict(mpn="ADM3202ARNZ", mfr="Analog Devices"),
    "TLP291-4GB-TP,ET": dict(mpn="TLP291-4(GB-TP,E)", mfr="Toshiba",
        flag="val had a typo 'TLP291-4(GB-TP,E(T'; used LCSC's spelling."),
    # --- non-LCSC parts whose val is a real part number
    "EC200AEUHA-N06-SNASA": dict(mpn="EC200AEUHA-N06-SNASA", mfr="Quectel"),
    "EG21-G": dict(mpn="EG21-G", mfr="Quectel"),
    "EG915NEUAG-N06-SGNSA": dict(mpn="EG915NEUAG-N06-SGNSA", mfr="Quectel",
        flag="val was 'EG915N-EU'; used the full ordering code from the component name."),
    "HLK-7688A": dict(mpn="HLK-7688A", mfr="Hi-Link"),
    "Relay_SRS": dict(mpn="SRS-05VDC-SL", mfr="Songle"),
    "LIC1620Q3R8257": dict(mpn="LIC1620Q3R8257", mfr="", value="250F 3.8V"),
    "Coincell 2032 - BS-2-1": dict(mpn="BS-2-1", mfr="", flag="Taobao part; BS-2-1 kept as part number, manufacturer unknown."),
    "PCB Grounding Lug": dict(mpn="DJ6116-6.3*0.8", mfr="", flag="Taobao part; kept DJ6116 type code as part number, manufacturer unknown."),
    # --- generics (no part number); cleaned-up description goes to Value
    "CONGREEN_1x2_3.81": dict(mpn="", mfr="", value="KF2EDGV 1x2P 3.81mm 90deg"),
    "CONGREEN_1x2_5.08": dict(mpn="", mfr="", value="KF2EDGV 1x2P 5.08mm 90deg"),
    "CONGREEN_1x3_3.81": dict(mpn="", mfr="", value="KF2EDGV 1x3P 3.81mm 90deg"),
    "CONGREEN_1x4_.3.81": dict(mpn="", mfr="", value="KF2EDGV 1x4P 3.81mm 90deg"),
    "CONGREEN_1x6_3.81": dict(mpn="", mfr="", value="KF2EDGV 1x6P 3.81mm 90deg"),
    "CONGREEN_1x7_3.81": dict(mpn="", mfr="", value="KF2EDGV 1x7P 3.81mm 90deg"),
    "CONGREEN_1x8_3.81": dict(mpn="", mfr="", value="KF2EDGV 1x8P 3.81mm 90deg"),
    "CONGREEN_1x8_3.81_straight": dict(mpn="", mfr="", value="KF2EDGV 1x8P 3.81mm Straight"),
    "CONGREEN_1x9_3.81": dict(mpn="", mfr="", value="KF2EDGV 1x9P 3.81mm 90deg"),
    "CONSMA003.042-L-G": dict(mpn="", mfr="", value="SMA-KE Edge Mount"),
    "CON_1Pin": dict(mpn="", mfr="", value=""),
    "CON_1x14_2.54mm_THT": dict(mpn="", mfr="", value="1x14 2.54mm"),
    "CON_1x14_2.54mm_THT_Bot_Entry": dict(mpn="", mfr="", value="1x14 2.54mm Bottom Entry"),
    "CON_1x2_2.54mm_THT": dict(mpn="", mfr="", value="1x2 2.54mm"),
    "CON_1x2_2.54mm_THT_ALT": dict(mpn="", mfr="", value="1x2 2.54mm"),
    "CON_1x3_2.54mm_THT": dict(mpn="", mfr="", value="1x3 2.54mm"),
    "CON_1x4_2.54mm_THT": dict(mpn="", mfr="", value="1x4 2.54mm"),
    "CON_1x4_2.54mm_THT_Bottom_Entry": dict(mpn="", mfr="", value="1x4 2.54mm Bottom Entry"),
    "CON_1x5_2.54mm_THT": dict(mpn="", mfr="", value="1x5 2.54mm"),
    "CON_1x6_2.54mm_THT": dict(mpn="", mfr="", value="1x6 2.54mm"),
    "CON_1x7_2.54mm_THT": dict(mpn="", mfr="", value="1x7 2.54mm"),
    "CON_1x8_2.54mm_THT": dict(mpn="", mfr="", value="1x8 2.54mm"),
    "CON_2x10_4.2mm_THT_F": dict(mpn="", mfr="", value="2x10 4.2mm 5569-style F"),
    "CON_2x12_4.2mm_THT_F": dict(mpn="", mfr="", value="2x12 4.2mm 5569-style F"),
    "CON_2x13_2.54mm_THT": dict(mpn="", mfr="", value="2x13 2.54mm",
        flag="val said 2mm ('CON_2x13_2mm_THT') but the component is 2.54mm."),
    "CON_2x13_2.54mm_THT_Long": dict(mpn="", mfr="", value="2x13 2.54mm Long Pins",
        flag="val said 2mm ('CON_2x13_2mm_THT') but the component is 2.54mm."),
    "CON_2x15_1.27mm_SMD_F": dict(mpn="", mfr="", value="2x15 1.27mm SMD F"),
    "CON_2x15_1.27mm_SMD_M": dict(mpn="", mfr="", value="2x15 1.27mm SMD M"),
    "CON_2x30_2MM_F": dict(flag="LCSC gives the same part number (2.0-2*30P) for both F and M."),
    "CON_2x30_2MM_M": dict(flag="LCSC gives the same part number (2.0-2*30P) for both F and M."),
    "CON_2x3_1.27mm_SMD_F": dict(mpn="", mfr="", value="2x3 1.27mm SMD F"),
    "CON_2x3_1.27mm_SMD_M": dict(mpn="", mfr="", value="2x3 1.27mm SMD M",
        flag="val held a Taobao URL (a different listing than the link); dropped it."),
    "CON_2x4_1.27mm_SMD_F": dict(mpn="", mfr="", value="2x4 1.27mm SMD F"),
    "CON_2x4_1.27mm_SMD_M": dict(mpn="", mfr="", value="2x4 1.27mm SMD M"),
    "CON_2x4_2.54mm_THT": dict(mpn="", mfr="", value="2x4 2.54mm"),
    "CON_2x5_1.27mm_SMD_F": dict(mpn="", mfr="", value="2x5 1.27mm SMD F"),
    "CON_2x5_1.27mm_SMD_M": dict(mpn="", mfr="", value="2x5 1.27mm SMD M"),
    "CON_2x7_2.54mm_THT": dict(mpn="", mfr="", value="2x7 2.54mm"),
    "CON_2x8_2.54mm_THT": dict(mpn="", mfr="", value="2x8 2.54mm"),
    "CON_BLACK_2x10_3.5mm": dict(mpn="", mfr="", value="KF2EDGSV 2x10P 3.5mm",
        flag="val said 2*8P for every size; used the size from the component name."),
    "CON_BLACK_2x6_3.5mm": dict(mpn="", mfr="", value="KF2EDGSV 2x6P 3.5mm",
        flag="val said 2*8P for every size; used the size from the component name."),
    "CON_BLACK_2x8_3.5mm": dict(mpn="", mfr="", value="KF2EDGSV 2x8P 3.5mm"),
    "CON_BLACK_2x9_3.5mm": dict(mpn="", mfr="", value="KF2EDGSV 2x9P 3.5mm",
        flag="val said 2*8P for every size; used the size from the component name."),
    "CON_IDC_2x10_2.00": dict(mpn="", mfr="", value="2x10 2.00mm IDC"),
    "CON_IDC_2x13_2.00": dict(mpn="", mfr="", value="2x13 2.00mm IDC"),
    "RJ45_90Deg": dict(flag="val was a description; part number taken from the LCSC link."),
    "Push_Button": dict(flag="val was a description; part number taken from the LCSC link."),
    "TP": dict(mpn="", mfr="", value=""),
    "CDA CBSV - Coin Supercap": dict(mpn="", mfr="CDA", value="0.22F 3.6V",
        flag="Taobao part; CBSV series, exact part number unknown."),
    "Fuse_1206": dict(mpn="", mfr="", value="", flag="Taobao URL was in note; moved to a link and cleared note."),
    # --- values for specific parts
    "Crystal Oscillators X50322712MSB2GI": dict(value="27.12MHz"),
    "NDK NX2016SA-25MHZ-STD-CZS-2": dict(value="25MHz"),
    "TOGNJING XTF32032768JT00351011": dict(value="32.768kHz"),
    "IND_1008_SMD_1UF_3.3A": dict(value="1uH 3.3A"),
    "IND_1210_Choke": dict(value="10uH", flag="Current rating not in the description; Value has inductance only."),
    "IND_FXL06": dict(value="8.2uH", flag="Current rating not in the description; Value has inductance only."),
    "MetalLions MNR5020T2R2MT": dict(value="2.2uH 2.9A"),
    "NLV32T-1R0J-EF": dict(value="1uH 400mA"),
    "NLV32T-R47J-PF": dict(value="470nH 450mA"),
    "cjiang FXL0530-2R2-M": dict(value="2.2uH 7A"),
    "DLM0NSN900HY2D": dict(value="90Ohm@100MHz 100mA"),
    "CAP_CAN_D10mm": dict(value="47uF 100V"),
    "CAP_CAN_D5mm": dict(value="10uF 16V", flag="val said '10uf' with no voltage; 16V taken from the linked RVT1C part."),
    "CAP_CAN_D6.3mm": dict(value="470uF 16V", flag="val said 10V but the linked RVT1C471 part is 16V. Please confirm."),
    "Kyocera AVX TAJE477K010RNJ": dict(value="470uF 10V"),
    "T520A107M006ATE070": dict(value="100uF 6.3V"),
    "TZC3P200A110R00": dict(value="5.8-20pF 100V"),
}

def lcsc_code(u):
    m = re.search(r"lcsc\.com/product-detail/(?:[^?]*_)?(C\d+)\.html", u)
    return m.group(1) if m else None

def clean_url(u):
    u = u.strip()
    code = lcsc_code(u)
    if code:
        return "LCSC", f"https://www.lcsc.com/product-detail/{code}.html"
    p = urlparse(u)
    host = p.netloc.lower()
    if "taobao.com" in host or "tmall.com" in host:
        q = parse_qs(p.query)
        keep = {k: q[k][0] for k in ("id", "skuId", "sku_properties") if k in q}
        name = "Tmall" if "tmall" in host else "Taobao"
        return name, f"{p.scheme}://{p.netloc}{p.path}?{urlencode(keep, safe=':')}"
    if "quectel.com" in host:
        return "Quectel", u
    if "analog.com" in host:
        return "Datasheet", u
    return host, u

def split_val(val, mpn):
    """If val is '<Manufacturer> <MPN>', return the manufacturer prefix."""
    if mpn and val.endswith(mpn) and val != mpn:
        return val[: -len(mpn)].strip()
    return ""

rows = []
for c in comps:
    p = c["params"]
    ref = c["ref"]
    o = O.get(ref, {})
    val = (p.get("val") or "").strip()
    links = []
    for k in ("sample link", "note"):
        u = p.get(k, "")
        if u.startswith("http") and clean_url(u) not in links:
            links.append(clean_url(u))
    code = next((lcsc_code(p.get(k, "")) for k in ("sample link", "note") if lcsc_code(p.get(k, ""))), None)
    lm, lp = L.get(code, (None, None)) if code else (None, None)

    if "mpn" in o:
        mpn = o["mpn"]
    elif lp:
        mpn = lp
    else:
        mpn = val if val not in ("", "*") else ""
    if "mfr" in o:
        mfr = o["mfr"]
    elif lm:
        mfr = MFR_NAMES.get(lm, lm)
    else:
        pre = split_val(val, mpn)
        mfr = MFR_NAMES.get(pre, pre)
    value = o.get("value", "")
    note = p.get("note")
    if note is not None and note.startswith("http"):
        note = ""
    comment_old = p.get("Comment", "")
    comment_new = "=Manufacturer Part Number" if mpn else "=Value"
    rows.append(dict(lib=c["lib"], ref=ref, desc=c["desc"], old_val=p.get("val"), mpn=mpn, mfr=mfr,
                     value=value, note_old=p.get("note"), note_new=note, links=links,
                     dropped=[k for k in ("unit price", "price", "datasheet", "sample link") if k in p],
                     comment_old=comment_old, comment_new=comment_new, flag=o.get("flag", "")))

unknown = [r["ref"] for r in rows if r["ref"] not in O and not (r["mpn"])]
missing_o = [k for k in O if k not in {r["ref"] for r in rows}]
json.dump(rows, open(os.path.join(W, "data", "mapping.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(rows), "rows; overrides not matched:", missing_o)
print("no MPN and no override:", unknown)
for r in rows:
    if r["mpn"] and not r["mfr"]:
        print("MPN without manufacturer:", r["ref"], r["mpn"])
