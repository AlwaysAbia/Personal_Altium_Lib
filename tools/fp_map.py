# (pcblib, current footprint name) -> dict(name=new name | None to delete, desc, merge=name it is merged into, flag)
F = {}
def a(lib, old, name, desc, flag=""):
    F[(lib, old)] = dict(name=name, desc=desc, merge=None, flag=flag)
def merge(lib, old, into, flag):
    F[(lib, old)] = dict(name=None, desc="", merge=into, flag=flag)
def delete(lib, old, flag="Unused by any schematic component."):
    F[(lib, old)] = dict(name=None, desc="", merge=None, flag=flag)

a("Buttons_and_Switches", "Push_Button", "TS-101-S26", "Tactile switch, 2 pads, SMD, 6.1x3.5mm body")

C = "Communication"
a(C, "QFN24-6X6_MC_MCH", "QFN-24_4x4mm_P0.5mm_EP", "QFN-24, 4x4mm body, 0.5mm pitch, exposed pad",
  "Old name said 6x6; the pads match a 4x4mm body.")
a(C, "U.FL-Antenna", "U.FL_IPEX1", "U.FL (IPEX1) RF receptacle, 3 pads, SMD")
a(C, "XCVR_EC200AEUHA-N06-SNASA", "EC200A", "Quectel EC200A LTE module, 144 pads, LCC, 1.3mm pitch")
a(C, "XCVR_EG21-G", "EG21-G", "Quectel EG21-G LTE module, 132 pads, LGA 29x32mm, 1.3mm pitch")
a(C, "XCVR_EG915NEUAG-N06-SGNSA", "EG915N", "Quectel EG915N LTE module, 126 pads, LGA")

N = "Connectors"
a(N, "A-SMA-KWE-15.1A", "A-SMA-KWE-15.1A", "SMA jack, right angle, 5 pads, THT")
a(N, "BH-18650-THR", "BH-18650-A5BJ001-2D", "18650 battery holder, 2 pads, THT, 72.3mm pin spacing")
for p, old in ((2, "CONGREEN_1x2_3.81"), (3, "CONGREEN_1x3_3.81"), (4, "CONGREEN_1x4_3.81"), (6, "CONGREEN_1x6_3.81"),
               (7, "CONGREEN_1x7_3.81"), (8, "CONGREEN_1X8_3.81"), (9, "CONGREEN_1x9_3.81")):
    a(N, old, f"CON_TB_1x{p}_3.81mm_RA", f"Pluggable terminal block 1x{p}, 3.81mm pitch, right angle, THT")
a(N, "CONGREEN_1X8_3.81 - Straight", "CON_TB_1x8_3.81mm_ST", "Pluggable terminal block 1x8, 3.81mm pitch, straight, THT")
a(N, "CONGREEN_1x2_5.08", "CON_TB_1x2_5.08mm_RA", "Pluggable terminal block 1x2, 5.08mm pitch, right angle, THT")
a(N, "CON_1Pin", "CON_1x1_THT", "Single pad, THT, 1.0mm hole")
for p in (2, 3, 4, 5, 6, 7, 8, 14):
    up = "X" if p == 14 else "x"
    a(N, f"CON_1{up}{p}_2.54MM_THT_F", f"CON_1x{p}_2.54mm_THT_F", f"Female header 1x{p}, 2.54mm pitch, THT")
    a(N, f"CON_1{up}{p}_2.54MM_THT_M", f"CON_1x{p}_2.54mm_THT_M", f"Male header 1x{p}, 2.54mm pitch, THT")
a(N, "CON_1X14_2.54MM_THT_F_Bot_Entry", "CON_1x14_2.54mm_THT_F_BotEntry", "Female header 1x14, 2.54mm pitch, bottom entry, THT")
a(N, "CON_1x4_2.54MM_THT_F_Bot_Entry", "CON_1x4_2.54mm_THT_F_BotEntry", "Female header 1x4, 2.54mm pitch, bottom entry, THT")
for p in (4, 7, 13):
    a(N, f"CON_2x{p}_2.54MM_THT_F", f"CON_2x{p}_2.54mm_THT_F", f"Female header 2x{p}, 2.54mm pitch, THT")
for p in (4, 7, 8, 13):
    a(N, f"CON_2x{p}_2.54MM_THT_M", f"CON_2x{p}_2.54mm_THT_M", f"Male header 2x{p}, 2.54mm pitch, THT")
a(N, "CON_2x13_2.54MM_THT_M_LONG", "CON_2x13_2.54mm_THT_M_Long", "Male header 2x13, 2.54mm pitch, long pins, THT")
for p in (10, 12):
    a(N, f"CON_2x{p}_4.2mm_THT_F", f"CON_2x{p}_4.20mm_THT_F", f"Connector 2x{p}, 4.20mm pitch (5569-style), THT")
for p in (3, 4, 5, 15):
    pegs = "" if p == 3 else ", positioning pegs"
    a(N, f"CON_2x{p}_1.27mm_SMD_F", f"CON_2x{p}_1.27mm_SMD_F", f"Female header 2x{p}, 1.27mm pitch, SMD{pegs}")
    a(N, f"CON_2x{p}_1.27mm_SMD_M", f"CON_2x{p}_1.27mm_SMD_M", f"Male header 2x{p}, 1.27mm pitch, SMD{pegs}")
a(N, "CON_2x30_2MM_F", "CON_2x30_2.00mm_THT_F", "Female header 2x30, 2.00mm pitch, THT")
a(N, "CON_2x30_2MM_M", "CON_2x30_2.00mm_THT_M", "Male header 2x30, 2.00mm pitch, THT")
for p, old in ((6, "CON_BLACK_2X6_3.5MM"), (8, "CON_BLACK_2x8_3.5mm"), (9, "CON_BLACK_2x9_3.5mm"), (10, "CON_BLACK_2x10_3.5mm")):
    a(N, old, f"CON_TB_2x{p}_3.50mm_ST", f"Pluggable terminal block 2x{p}, 3.50mm pitch, straight, THT")
a(N, "CON_IDC_2x10_2.00", "CON_IDC_2x10_2.00mm_THT", "IDC box header 2x10, 2.00mm pitch, THT")
a(N, "CON_IDC_2x13_2.00", "CON_IDC_2x13_2.00mm_THT", "IDC box header 2x13, 2.00mm pitch, THT")
a(N, "CON_IDC_2x6_2.54", "CON_IDC_2x6_2.54mm_THT", "IDC connector 2x6, 2.54mm pitch, THT")
a(N, "Coincell_2032", "BS-2-1", "CR2032 coin cell holder, 2 pads, THT, 20mm pin spacing")
a(N, "HANRUN_HR911105A", "HR911105A", "RJ45 jack with magnetics, 1 port, right angle, THT")
a(N, "HL2-SMA-KE-15", "HL2-SMA-KE-15", "SMA jack, straight, 5 pads, THT")
a(N, "HRO_TYPE-C-31-M-12", "TYPE-C-31-M-12", "USB-C receptacle 16P, SMD with THT shell, 0.5mm pitch",
  "Land pattern is the HRO TYPE-C-31-M-12, used by the SHOU HAN TYPE-C 16PIN part. Name keeps the HRO part it was drawn from.")
for p in (3, 4, 8):
    a(N, f"JST XH2.54mm 1x{p}", f"CON_XH_1x{p}_2.50mm_THT", f"XH-style header 1x{p}, 2.50mm pitch, THT")
a(N, "MICROSIM_Holder_MOLEX", "5039600696", "Micro SIM card connector 6+2P, right angle, SMD")
a(N, "PCB Grounding Lug", "LUG_6.3mm_THT", "Grounding lug 6.3mm tab, 2 pads, THT")
a(N, "RJ45_90Deg", "R-RJ45R10P-B000", "RJ45 jack, 1 port, right angle, shielded, THT")
a(N, "RJ45_90Deg_4Port", "HC-RJ45-5JA-4-2", "RJ45 jack, 4 ports, right angle, shielded, THT")
a(N, "RJ45_90Deg_HCTL", "HC-RJ45-5JA-1-2", "RJ45 jack, 1 port, right angle, shielded, THT")
a(N, "TE_CONSMA003.042-L-G", "CONSMA003.042-L-G", "SMA jack, edge mount, 5 pads",
  "Land pattern is the TE CONSMA003.042-L-G; name keeps that part number.")
a(N, "TP_D1mm", "TP_SMD_D1.0mm", "Test point, 1.0mm round SMD pad")
a(N, "USB_A_FEMALE_THT", "U-USBAR04P-F001", "USB-A receptacle, right angle, THT")
a(N, "USB_A_FEMALE_THT_Vertical", "USB-226-BRY", "USB-A receptacle, vertical, THT")

Y = "Crystals"
a(Y, "MC146_Crystal", "XTAL_MC-146", "Crystal MC-146, 4 pads, SMD")
a(Y, "NDK NX2016SA-25MHZ-STD-CZS-2", "XTAL_2016-4P_2.0x1.6mm", "Crystal 2016, 4 pads, SMD, 2.0x1.6mm body")
a(Y, "SMD5032-2P", "XTAL_5032-2P_5.0x3.2mm", "Crystal 5032, 2 pads, SMD, 5.0x3.2mm body")
a(Y, "XTAL_3215", "XTAL_3215-2P_3.2x1.5mm", "Crystal 3215, 2 pads, SMD, 3.2x1.5mm body")

D = "Diodes"
a(D, "DIO_ESDA6V1-5W6", "SOT-363", "SOT-363 (SC-70-6), 6 pins, 2.0x1.25mm body, 0.65mm pitch")
delete(D, "DO-213")
a(D, "DO-214AC", "DO-214AC", "DO-214AC (SMA), 2 pads, 4.3x2.6mm body",
  "Old description was 'SODFL, Body 1.30x2.50mm' (copied from another part).")
a(D, "DO214AA", "DO-214AA", "DO-214AA (SMB), 2 pads, 4.6x3.6mm body",
  "Old description was 'Molded Capacitor' (copied from another part).")
a(D, "SMAF", "SMAF", "SMAF, 2 pads, 4.6x2.8mm body")
a(D, "SOD-123FL", "SOD-123FL", "SOD-123FL, 2 pads, 2.7x1.6mm body")
a(D, "SOD-523_0P9X1P3_ONS", "SOD-523", "SOD-523, 2 pads, 1.2x0.8mm body")
merge(D, "SOIC-8_LTF", "SOIC-8_3.9x4.9mm_P1.27mm",
      "Duplicate SOIC-8. Merged into the IC_Digital SOIC-8 (pad rows 5.40mm apart vs 5.45mm here). SLVU2.8-4BTG re-pointed.")
a(D, "TVS_RCLAMP0502B.TCT", "SOT-523", "SOT-523 (SC-75), 3 pins, 1.6x0.8mm body, 1.0mm pitch")

I = "IC_Digital"
a(I, "16SOIC_N", "SOIC-16_3.9x9.9mm_P1.27mm", "SOIC-16, 3.9x9.9mm body, 1.27mm pitch")
a(I, "8SOIC_208", "SOIC-8_5.3x5.3mm_P1.27mm", "SOIC-8 208mil, 5.3x5.3mm body, 1.27mm pitch")
a(I, "8SOIC_N", "SOIC-8_3.9x4.9mm_P1.27mm", "SOIC-8, 3.9x4.9mm body, 1.27mm pitch",
  "Kept as the single SOIC-8. Same-name copy in Transistors_Relays and the Diodes SOIC-8 are merged into it.")
a(I, "H1601CE", "H1601CE", "LAN transformer, 16 pads, SMD, 12.7x7.1mm body, 1.27mm pitch")
a(I, "HLK-7688A", "HLK-7688A", "Hi-Link HLK-7688A Wi-Fi module, 59 pads, SMD 32.8x18mm")
a(I, "IC_CP2102N-A02-GQFN28R", "QFN-28_5x5mm_P0.5mm_EP", "QFN-28, 5x5mm body, 0.5mm pitch, exposed pad")
a(I, "LQFP-100_STM", "LQFP-100_14x14mm_P0.5mm", "LQFP-100, 14x14mm body, 0.5mm pitch")
a(I, "QFN50P500X500X100_HS-33N", "QFN-32_5x5mm_P0.5mm_EP", "QFN-32, 5x5mm body, 0.5mm pitch, exposed pad")
a(I, "QFP50P900X900X160-48N", "LQFP-48_7x7mm_P0.5mm", "LQFP-48, 7x7mm body, 0.5mm pitch")
a(I, "SO16_TOS", "SOP-16_4.4x10.3mm_P1.27mm", "SOP-16, 4.4x10.3mm body, 1.27mm pitch",
  "Body size taken from the Toshiba SO16 package (TLP291-4); confirm.")
a(I, "SOP65P640X120-20N", "TSSOP-20_4.4x6.5mm_P0.65mm", "TSSOP-20, 4.4x6.5mm body, 0.65mm pitch")
a(I, "SOP65P640X120-24N", "TSSOP-24_4.4x7.8mm_P0.65mm", "TSSOP-24, 4.4x7.8mm body, 0.65mm pitch")
a(I, "SOT95P280X145-6N", "SOT-23-6", "SOT-23-6, 2.9x1.6mm body, 0.95mm pitch")
a(I, "XCVR_ESP32-S3-WROOM-1-N16R2", "ESP32-S3-WROOM-1", "Espressif ESP32-S3-WROOM-1 module, SMD 18x25.5mm")

P = "IC_Power"
a(P, "B_S-1W", "SIP-4_P2.54mm", "SIP-4, 2.54mm pitch, THT (B0505S/B0303S DC-DC modules)",
  "Old description was 'SOT23, 6-Leads' (copied from another part).")
a(P, "DFN-0-EP(3x3)", "DFN-10_3x3mm_P0.5mm_EP", "DFN-10, 3x3mm body, 0.5mm pitch, exposed pad",
  "Old name said DFN-0; old description said SOT23.")
a(P, "IC_TPS61088RHLR", "VQFN-20_3.5x4.5mm_P0.5mm_EP", "VQFN-20, 3.5x4.5mm body, 0.5mm pitch, exposed pad")
a(P, "MAX38888", "TDFN-14_3x3mm_P0.4mm_EP", "TDFN-14, 3x3mm body, 0.4mm pitch, exposed pad")
a(P, "MIC29302WU", "TO-263-5", "TO-263-5 (D2PAK-5), 1.7mm pitch")
a(P, "SOIC8_T", "SOIC-8_3.9x4.9mm_P1.27mm_EP", "SOIC-8, 3.9x4.9mm body, 1.27mm pitch, exposed pad")
a(P, "SOP65P640X120-28N", "TSSOP-28_4.4x9.7mm_P0.65mm", "TSSOP-28, 4.4x9.7mm body, 0.65mm pitch")
a(P, "SOT223-4", "SOT-223", "SOT-223, 3 pins + tab, 6.5x3.5mm body, 2.3mm pitch")
a(P, "SOT23-3", "SOT-23-3", "SOT-23-3, 2.9x1.3mm body, 0.95mm pitch",
  "Kept as the single SOT-23-3. The Transistors_Relays SOT95P237X111-3N is merged into it.")
a(P, "SOT23-5", "SOT-23-5", "SOT-23-5, 2.9x1.6mm body, 0.95mm pitch",
  "Kept as the single SOT-23-5. SOT95P280X145-5N is merged into it.")
merge(P, "SOT95P280X145-5N", "SOT-23-5",
      "Duplicate SOT-23-5 (pad rows 2.5mm apart vs 2.7mm in the kept one). TLV62569DBVR re-pointed.")
a(P, "SOTFL50P160X60-6N", "SOT-563", "SOT-563, 6 pins, 1.6x1.2mm body, 0.5mm pitch")
a(P, "TPS2121RUXR", "VQFN-HR-12_2x2.5mm_P0.5mm", "VQFN-HR-12 (TI HotRod), 2x2.5mm body, 0.5mm pitch")

a("Other", "TMB12A05", "TMB12A05", "Buzzer 12mm, 2 pads, THT, 7.6mm pin spacing")

S = "Passives"
a(S, "5050_RGB_LED_SMD", "LED_5050-6P", "LED 5050, 6 pads, SMD, 5.0x5.0mm body")
for sz, metric in (("0402", "1005"), ("0603", "1608"), ("0805", "2012"), ("1206", "3216"), ("1210", "3225"), ("1812", "4532"), ("2512", "6332")):
    a(S, f"CAP_{sz}", f"CAP_{sz}", f"Chip capacitor {sz} ({metric} metric), 2 pads, SMD")
for sz, metric in (("0402", "1005"), ("0603", "1608"), ("0805", "2012"), ("1206", "3216"), ("2512", "6332")):
    a(S, f"RES_{sz}", f"RES_{sz}", f"Chip resistor {sz} ({metric} metric), 2 pads, SMD")
for sz, metric in (("0402", "1005"), ("0603", "1608"), ("0805", "2012")):
    a(S, f"LED_{sz}", f"LED_{sz}", f"Chip LED {sz} ({metric} metric), 2 pads, SMD")
a(S, "FUSE_1206", "FUSE_1206", "Chip fuse 1206 (3216 metric), 2 pads, SMD")
a(S, "CAP_CAN_D10mm", "CAP_CAN_D10mm", "Aluminum electrolytic can, 10mm diameter, SMD")
a(S, "CAP_CAN_D5MM", "CAP_CAN_D5mm", "Aluminum electrolytic can, 5mm diameter, SMD",
  "The part using it (RVT1C100M0405) is a 4mm can per LCSC; footprint is drawn for 5mm.")
a(S, "CAP_CAN_D6.3MM", "CAP_CAN_D6.3mm", "Aluminum electrolytic can, 6.3mm diameter, SMD")
delete(S, "CAP_CAN_D8MM")
delete(S, "LED_COM_ANODE")
a(S, "CDA CBSV - Coin Supercap - V Type", "CAP_COIN_CBSV_V", "Coin supercapacitor CBSV V-type, 2 pads, THT, 5.08mm spacing")
a(S, "FIL_ACM2012-201-2P-T002", "ACM2012", "TDK ACM2012 common mode choke, 4 pads, SMD, 2.0x1.2mm body")
a(S, "FIL_DLM0NSN900HY2D", "DLM0NS", "Murata DLM0NS common mode choke, 4 pads, SMD, 0.65x0.5mm body")
a(S, "IND_1008", "IND_1008", "Chip inductor 1008 (2520 metric), 2 pads, SMD")
a(S, "IND_1210", "IND_1210", "Chip inductor 1210 (3225 metric), 2 pads, SMD",
  "Kept as the single 1210 inductor (pads 2.90mm apart). INDM3225X240N is merged into it.")
merge(S, "INDM3225X240N", "IND_1210",
      "Duplicate 1210 inductor (pads 3.01mm apart vs 2.90mm in the kept one). NLV32T-1R0J-EF re-pointed.")
a(S, "IND_CD53", "IND_CD53", "Power inductor CD53 size, 2 pads, SMD, 5.4x5.2mm body")
a(S, "IND_FXL06", "IND_FXL0630", "Power inductor FXL0630, 2 pads, SMD, 7.0x6.6mm body",
  "Old description was 'Body 4.50x4.00mm' (copied from another part).")
a(S, "SMD,5x5mm", "IND_5x5mm", "Power inductor 5x5mm, 2 pads, SMD")
a(S, "Kyocera AVX TAJE477K010RNJ", "CAP_TANT_7343-43", "Tantalum capacitor 7343-43 (Case E), 2 pads, SMD")
a(S, "T520A107M006ATE070", "CAP_TANT_3216-18", "Tantalum capacitor 3216-18 (Case A), 2 pads, SMD")
a(S, "LIC1620", "CAP_RADIAL_D16mm_P7.5mm", "Radial capacitor 16mm diameter, 7.5mm lead spacing, THT",
  "Diameter inferred from the part code (LIC1620 = 16x20mm); pad spacing measured.")
a(S, "SMD5050 - WS2812B-B", "LED_5050-4P", "LED 5050, 4 pads, SMD, 5.0x5.0mm body")

T = "Transistors_Relays"
merge(T, "8SOIC_N", "SOIC-8_3.9x4.9mm_P1.27mm",
      "Same name and same pads as the IC_Digital copy; removed so the name exists once. ME4925-G keeps pointing at it.")
a(T, "FDMC3612", "PQFN-8_3.3x3.3mm_P0.65mm", "PQFN-8 (onsemi Power33), 3.3x3.3mm body, 0.65mm pitch")
a(T, "Relay_SRS", "SRS-05VDC-SL", "Songle SRS signal relay, 6 pads, THT")
delete(T, "SOT23")
merge(T, "SOT95P237X111-3N", "SOT-23-3",
      "Duplicate SOT-23-3 (pad rows 2.12mm apart vs 2.30mm in the kept one). BSS138LT1G and BSS84LT1G re-pointed.")
a(T, "SOTFL50P160X85-3N", "SOT-416FL", "SOT-416FL (EMT3F), 3 pins, 1.6x0.8mm body, 1.0mm pitch")
a(T, "TE_1-1393210-3", "SLA-05VDC-SL-A", "Songle SLA power relay, 4 pads, THT",
  "Land pattern came from TE 1-1393210-3; named after the Songle part that uses it.")
a(T, "TRANS_2SK3019TL", "SOT-416", "SOT-416 (EMT3), 3 pins, 1.6x0.8mm body, 1.0mm pitch")
a(T, "TRANS_SI7123DN-T1-GE3", "PowerPAK-1212-8", "PowerPAK 1212-8, 3.3x3.3mm body, 0.65mm pitch")

MISSING = {("Passives", "STC3MD20-T1", "SMD,4.5x3.2mm"): "SMD_4.5x3.2mm_Trimmer"}
