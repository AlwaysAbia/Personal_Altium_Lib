# (lib, current name) -> (designator prefix, new name, description, flag)
R = {}
def a(lib, old, des, name, desc, flag=""):
    R[(lib, old)] = dict(des=des, name=name, desc=desc, flag=flag)

B = "Buttons_and_Switches"
a(B, "Push_Button", "SW", "TS-101-S26", "Tactile Switch SPST-NO 260gf, SMD 6.1x3.5mm")

C = "Communication"
a(C, "EC200AEUHA-N06-SNASA", "U", "EC200AEUHA-N06-SNASA", "LTE Cat 1 Module (EU)", "Old description was antenna specs; replaced with module type.")
a(C, "EG21-G", "U", "EG21-G", "LTE Cat 1 Module (Global), LGA 29x32mm")
a(C, "EG915NEUAG-N06-SGNSA", "U", "EG915NEUAG-N06-SGNSA", "LTE Cat 1 Module (EU)")
a(C, "LAN8720AI-CP-TR", "U", "LAN8720AI-CP-TR", "Ethernet PHY 10/100 RMII, Auto-MDIX, QFN-24 (4x4)")
a(C, "U.FL-Antenna", "J", "BWU.FL-IPEX1", "RF Connector U.FL (IPEX1) Receptacle 50Ohm, SMD")

N = "Connectors"
a(N, "A-SMA-KWE-15.1A", "J", "A-SMA-KWE-15.1A", "RF Connector SMA Jack, Right Angle, 50Ohm 6GHz, THT")
a(N, "BH-18650-A5BJ001-2D", "BT", "BH-18650-A5BJ001-2D", "Battery Holder 1x18650, THT")
for p in (2, 3, 4, 6, 7, 8, 9):
    old = {4: "CONGREEN_1x4_.3.81"}.get(p, f"CONGREEN_1x{p}_3.81")
    a(N, old, "J", f"CON_TB_1x{p}_3.81mm_RA", f"Pluggable Terminal Block 1x{p}P 3.81mm, Right Angle, THT",
      "Fixed the '.3.81' typo in the old name." if p == 4 else "")
a(N, "CONGREEN_1x2_5.08", "J", "CON_TB_1x2_5.08mm_RA", "Pluggable Terminal Block 1x2P 5.08mm, Right Angle, THT")
a(N, "CONGREEN_1x8_3.81_straight", "J", "CON_TB_1x8_3.81mm_ST", "Pluggable Terminal Block 1x8P 3.81mm, Straight, THT")
a(N, "CONSMA003.042-L-G", "J", "CON_SMA_EdgeMount", "RF Connector SMA Jack, Edge Mount, 50Ohm")
a(N, "CON_1Pin", "TP", "CON_1x1_THT", "Single Pad, THT")
for p in (2, 3, 4, 5, 6, 7, 8, 14):
    a(N, f"CON_1x{p}_2.54mm_THT", "J", f"CON_1x{p}_2.54mm_THT", f"Header 1x{p} 2.54mm, THT")
a(N, "CON_1x2_2.54mm_THT_ALT", "J", "CON_1x2_2.54mm_THT_ALT", "Header 1x2 2.54mm, THT (alternate symbol)")
a(N, "CON_1x14_2.54mm_THT_Bot_Entry", "J", "CON_1x14_2.54mm_THT_BotEntry", "Female Header 1x14 2.54mm, THT, Bottom Entry")
a(N, "CON_1x4_2.54mm_THT_Bottom_Entry", "J", "CON_1x4_2.54mm_THT_BotEntry", "Female Header 1x4 2.54mm, THT, Bottom Entry")
for p in (10, 12):
    a(N, f"CON_2x{p}_4.2mm_THT_F", "J", f"CON_2x{p}_4.20mm_THT_F", f"Connector 2x{p} 4.20mm (5557/5569-style), THT, Straight")
a(N, "CON_2x13_2.54mm_THT", "J", "CON_2x13_2.54mm_THT", "Header 2x13 2.54mm, THT")
a(N, "CON_2x13_2.54mm_THT_Long", "J", "CON_2x13_2.54mm_THT_Long", "Header 2x13 2.54mm, THT, 20mm Long Pins")
for p in (3, 4, 5, 15):
    for g, gn in (("F", "Female"), ("M", "Male")):
        pegs = ", Positioning Pegs" if p != 3 else ""
        a(N, f"CON_2x{p}_1.27mm_SMD_{g}", "J", f"CON_2x{p}_1.27mm_SMD_{g}", f"{gn} Header 2x{p} 1.27mm, SMD{pegs}",
          "Old description said 2x4." if p == 3 else "")
a(N, "CON_2x30_2MM_F", "J", "CON_2x30_2.00mm_THT_F", "Female Header 2x30 2.00mm, THT",
  "Kept a generic name: the part number (2.0-2*30P) is a vendor catalog code shared by F and M.")
a(N, "CON_2x30_2MM_M", "J", "CON_2x30_2.00mm_THT_M", "Male Header 2x30 2.00mm, THT",
  "Kept a generic name: the part number (2.0-2*30P) is a vendor catalog code shared by F and M.")
for p in (4, 7, 8):
    a(N, f"CON_2x{p}_2.54mm_THT", "J", f"CON_2x{p}_2.54mm_THT", f"Header 2x{p} 2.54mm, THT")
for p in (6, 8, 9, 10):
    a(N, f"CON_BLACK_2x{p}_3.5mm", "J", f"CON_TB_2x{p}_3.50mm_ST", f"Pluggable Terminal Block 2x{p}P 3.50mm, Straight, THT")
a(N, "CON_IDC_2x10_2.00", "J", "CON_IDC_2x10_2.00mm_THT", "IDC Box Header 2x10 2.00mm, THT")
a(N, "CON_IDC_2x13_2.00", "J", "CON_IDC_2x13_2.00mm_THT", "IDC Box Header 2x13 2.00mm, THT")
a(N, "CON_IDC_2x6_2.54", "J", "CON_IDC_2x6_2.54mm", "IDC Cable Connector 2x6 2.54mm",
  "Kept a generic name: the part number (2.54-2*6P) is a vendor catalog code.")
a(N, "Coincell 2032 - BS-2-1", "BT", "BS-2-1", "Coin Cell Holder CR2032")
a(N, "HL2-SMA-KE-15", "J", "HL2-SMA-KE-15", "RF Connector SMA Jack, Straight, 50Ohm, THT")
a(N, "HR911105A", "J", "HR911105A", "RJ45 Jack with Magnetics, 1 Port, Right Angle, Shielded, THT")
for p in (3, 4, 8):
    a(N, f"JST XH2.54mm 1x{p}", "J", f"CON_XH_1x{p}_2.50mm_THT", f"Header XH-style 1x{p} 2.50mm, THT",
      "Kept a generic name: the part number is a vendor catalog code. XH pitch is 2.50mm (old name said 2.54mm).")
a(N, "MICROSIM_Holder_MOLEX", "J", "5039600696", "Micro SIM Card Connector 6+2P, Right Angle, SMD")
a(N, "PCB Grounding Lug", "E", "LUG_6.3mm_THT", "Grounding Lug 6.3mm Quick-Connect Tab, THT",
  "Kept a generic name: Taobao part, DJ6116 is a type code.")
a(N, "RJ45-90Degree-4Port", "J", "HC-RJ45-5JA-4-2", "RJ45 Jack 4 Port, Right Angle, Shielded, THT")
a(N, "RJ45_90Deg", "J", "R-RJ45R10P-B000", "RJ45 Jack 1 Port, Right Angle, Shielded, THT")
a(N, "RJ45_90Deg_HCTL", "J", "HC-RJ45-5JA-1-2", "RJ45 Jack 1 Port, Right Angle, Shielded, THT")
a(N, "TP", "TP", "TP", "Test Point")
a(N, "USB-TypeA", "J", "U-USBAR04P-F001", "USB-A Receptacle, Right Angle, THT")
a(N, "USB-TypeA_Vertical", "J", "USB-226-BRY", "USB-A Receptacle, Vertical, THT")
a(N, "USB-TypeC", "J", "TYPE-C 16PIN 2MD(073)", "USB-C Receptacle 16P, Right Angle, SMD")

Y = "Crystals"
a(Y, "Crystal Oscillators X50322712MSB2GI", "Y", "X50322712MSB2GI", "Crystal 27.12MHz ±10ppm 20pF, SMD-5032")
a(Y, "MC146_32.768KHz", "Y", "MC-146 32.7680KA-A0", "Crystal 32.768kHz, MC-146",
  "Name drops the ':ROHS' suffix (':' is not allowed in internal names). Part number keeps it.")
a(Y, "NDK NX2016SA-25MHZ-STD-CZS-2", "Y", "NX2016SA-25MHZ-STD-CZS-2", "Crystal 25MHz ±15ppm 8pF, SMD-2016")
a(Y, "TOGNJING XTF32032768JT00351011", "Y", "XTF32032768JT00351011", "Crystal 32.768kHz ±20ppm 12.5pF, SMD-3215")

D = "Diodes"
a(D, "ESD5Z5.0T1G", "D", "ESD5Z5.0", "ESD Protection Diode 5V, 18.6V Clamp, SOD-523",
  "Old name was the onsemi part (ESD5Z5.0T1G); the part number on file is AnBon ESD5Z5.0.")
a(D, "ESDA6V1-5W6", "D", "ESDA6V1-5W6-TP", "ESD Protection Array 5-Line 6.1V, SOT-363")
a(D, "ESDA6V1-5W6_1", "D", "ESDA6V1-5W6", "ESD Protection Array 5-Line 6.1V, SOT-323-6")
a(D, "RCLAMP0502B.TCT", "D", "RCLAMP0502B.TCT", "TVS Diode Array 2-Line 5V, 18V Clamp, SC-75")
a(D, "SLVU2.8-4BTG", "D", "SLVU2.8-4BTG", "TVS Diode Array 4-Line 2.8V, 15V Clamp, SOIC-8")
a(D, "SMBJ58A-13-F", "D", "SMBJ58A-13-F", "TVS Diode Unidirectional 58V, 93.6V Clamp, SMB")
a(D, "SMF5.0CA", "D", "SMF5.0CA", "TVS Diode Bidirectional 5V, 9.2V Clamp, SOD-123FL")
a(D, "SS16", "D", "SS16", "Schottky Diode 60V 1A, SMA (DO-214AC)")
a(D, "SS510F", "D", "SS510F", "Schottky Diode 100V 5A, SMAF")

I = "IC_Digital"
a(I, "ADM3202ARNZ", "U", "ADM3202ARNZ", "RS-232 Transceiver 2-Channel 3.3V, SOIC-16")
a(I, "CLRC66303HNE", "U", "CLRC66303HNE", "NFC/RFID Reader ISO14443A/B MIFARE, I2C/SPI/UART, HVQFN-32 (5x5)")
a(I, "CP2102N-A02-GQFN28R", "U", "CP2102N-A02-GQFN28R", "USB to UART Bridge, QFN-28 (5x5)")
a(I, "ESP32-S3-WROOM-1-N16R2", "U", "ESP32-S3-WROOM-1-N16R2", "Wi-Fi/BLE Module ESP32-S3, 16MB Flash 2MB PSRAM, PCB Antenna")
a(I, "HLK-7688A", "U", "HLK-7688A", "Wi-Fi Module MT7688AN, SMD 32.8x18mm")
a(I, "ISO7721DR", "U", "ISO7721DR", "Digital Isolator 2-Channel, SOIC-8")
a(I, "LAN Transformer", "T", "H1601CE", "LAN Transformer 10/100Base-T 1CT:1CT 350uH, SMD-16",
  "Used T (transformer) as the designator. It wasn't in the agreed list; was U.")
a(I, "STM32F103CBT6", "U", "STM32F103CBT6", "MCU ARM Cortex-M3 72MHz 128KB Flash, LQFP-48")
a(I, "STM32H562VGT6", "U", "STM32H562VGT6", "MCU ARM Cortex-M33 250MHz 1MB Flash 640KB RAM, LQFP-100")
a(I, "STM32H573VIT6", "U", "STM32H573VIT6", "MCU ARM Cortex-M33 250MHz 2MB Flash 640KB RAM, LQFP-100",
  "Old description was copied from the H562 and said 1MB; the H573VI has 2MB.")
a(I, "TCA9548APWR", "U", "TCA9548APWR", "I2C Multiplexer 8-Channel, TSSOP-24")
a(I, "TLP291-4GB-TP,ET", "U", "TLP291-4(GB-TP,E)", "Optocoupler 4-Channel Transistor Output, SOP-16")
a(I, "TXB0101DBVR", "U", "TXB0101DBVR", "Level Shifter 1-Bit Bidirectional Auto-Direction, SOT-23-6")
a(I, "TXS0108EPWR", "U", "TXS0108EPWR", "Level Shifter 8-Bit Bidirectional, TSSOP-20")
a(I, "W25Q128FVSIG", "U", "W25Q128FVSIG", "NOR Flash 128Mbit SPI/QPI, SOIC-8 208mil")

P = "IC_Power"
a(P, "B0303S-1WR3", "U", "B0303S-1WR3", "Isolated DC-DC Module 1W 3.3V to 3.3V, SIP-4")
a(P, "B0505S-1W", "U", "B0505S-1W", "Isolated DC-DC Module 1W 5V to 5V, SIP-4")
a(P, "MAX38888ATD+T", "U", "MAX38888ATD+T", "Supercapacitor Backup Regulator, TDFN-14 (3x3)")
a(P, "MCP1700T-3302E/TT", "U", "MCP1700T-3302E/TT", "LDO Regulator 3.3V 250mA, SOT-23")
a(P, "MCP73833-AMI/MF", "U", "MCP73833-AMI/MF", "Li-Ion/Li-Po Charger Linear 1A, DFN-10 (3x3)")
a(P, "MIC29302WU", "U", "MIC29302WU", "LDO Regulator Adjustable 3A, TO-263-5")
a(P, "MIC39100_SOT223", "U", "MIC39100-3.3WS", "LDO Regulator 3.3V 1A, SOT-223")
a(P, "TI LMR16030SDDAR", "U", "LMR16030SDDAR", "Buck Converter 60V 3A Adjustable, SO-8-EP")
a(P, "TI TPS2121RUXR", "U", "TPS2121RUXR", "Power Mux 2.8-22V Priority Switchover, VQFN-12 (2x2.5)")
a(P, "TI TPS23861PWR", "U", "TPS23861PWR", "PoE PSE Controller 4-Port 25.5W, TSSOP-28")
a(P, "TI TPS61023DRLR", "U", "TPS61023DRLR", "Boost Converter 3.7A 0.5V Min Input, SOT-563")
a(P, "TLV62569DBVR", "U", "TLV62569DBVR", "Buck Converter 5.5V 2A Adjustable, SOT-23-5")
a(P, "TPS61088RHLR", "U", "TPS61088RHLR", "Boost Converter 10A Synchronous, VQFN-20 (3.5x4.5)")
a(P, "USB - Load Switch", "U", "SY6288CAAC", "Load Switch 2A Active High, SOT-23-5")

O = "Other"
a(O, "TMB12A05", "BZ", "TMB12A05", "Active Buzzer 5V, THT 12mm")

S = "Passives"
a(S, "5050_RGB_LED_SMD", "D", "XL-5050RGBC", "LED RGB, SMD-5050-6P")
a(S, "ACM2012-201-2P-T002", "FL", "ACM2012-201-2P-T002", "Common Mode Choke 2-Line 200Ohm@100MHz 350mA, 0805")
for sz in ("0402", "0603", "0805", "1206", "1210", "1812", "2512"):
    a(S, f"CAP_{sz}", "C", f"CAP_{sz}", f"Capacitor, {sz}")
for sz in ("0402", "0603", "0805", "1206", "2512"):
    a(S, f"RES_{sz}", "R", f"RES_{sz}", f"Resistor, {sz}")
for sz in ("0402", "0603", "0805"):
    a(S, f"LED_{sz}", "D", f"LED_{sz}", f"LED, {sz}")
a(S, "CAP_CAN_D10mm", "C", "RVT2A470M1010", "Aluminum Electrolytic Capacitor 47uF 100V, SMD D10x10.2mm",
  "Named by part number since it has one. If you use this as a generic can footprint, say so and I'll keep CAP_CAN_D10mm.")
a(S, "CAP_CAN_D5mm", "C", "RVT1C100M0405", "Aluminum Electrolytic Capacitor 10uF 16V, SMD D4x5.4mm",
  "Old name said D5mm but the linked part is D4x5.4mm. Same naming note as the other cans.")
a(S, "CAP_CAN_D6.3mm", "C", "RVT1C471M0607", "Aluminum Electrolytic Capacitor 470uF 16V, SMD D6.3x7.7mm",
  "Same naming note as the other cans.")
a(S, "CDA CBSV - Coin Supercap", "C", "CAP_COIN_CBSV", "Supercapacitor Coin 0.22F 3.6V, CDA CBSV V-Type")
a(S, "DLM0NSN900HY2D", "FL", "DLM0NSN900HY2D", "Common Mode Choke 2-Line 90Ohm@100MHz 100mA, 0302")
a(S, "Fuse_1206", "F", "FUSE_1206", "Fuse, 1206")
a(S, "IND_1008_SMD_1UF_3.3A", "L", "DFE252012F-1R0M=P2", "Inductor 1uH 3.3A, 1008")
a(S, "IND_1210_Choke", "L", "TFM322512ALMA100MTAA", "Inductor 10uH, 1210")
a(S, "IND_FXL06", "L", "FXL0630-8R2-M", "Inductor 8.2uH, SMD 7x6.6mm")
a(S, "Kyocera AVX TAJE477K010RNJ", "C", "TAJE477K010RNJ", "Tantalum Capacitor 470uF 10V ±10%, 7343-43 (Case E)")
a(S, "LIC1620Q3R8257", "C", "LIC1620Q3R8257", "Lithium-Ion Capacitor 250F 3.8V, Radial Can")
a(S, "MetalLions MNR5020T2R2MT", "L", "MNR5020T2R2MT", "Inductor 2.2uH 2.9A Shielded, SMD 5x5mm")
a(S, "NLV32T-1R0J-EF", "L", "NLV32T-1R0J-EF", "Inductor 1uH 400mA, 1210")
a(S, "NLV32T-R47J-PF", "L", "NLV32T-R47J-PF", "Inductor 470nH 450mA, 1210")
a(S, "T520A107M006ATE070", "C", "T520A107M006ATE070", "Tantalum Polymer Capacitor 100uF 6.3V, 3216-18 (Case A)")
a(S, "TZC3P200A110R00", "C", "STC3MD20-T1", "Trimmer Capacitor 5.8-20pF 100V, SMD 4.5x3.2mm")
a(S, "Worldsemi WS2812B-B/W", "D", "WS2812B-B/W", "LED RGB Addressable, SMD-5050-4P")
a(S, "cjiang FXL0530-2R2-M", "L", "FXL0530-2R2-M", "Inductor 2.2uH 7A, SMD 5.4x5.2mm")

T = "Transistors_Relays"
a(T, "2SC4617TLQ", "Q", "2SC4617TLQ", "BJT NPN 50V 150mA, SOT-416")
a(T, "BSS138LT1G", "Q", "BSS138LT1G", "MOSFET N-CH 50V 200mA, SOT-23")
a(T, "BSS84LT1G", "Q", "BSS84LT1G", "MOSFET P-CH 50V 130mA, SOT-23")
a(T, "DMN3404L-7", "Q", "DMN3404L-7", "MOSFET N-CH 30V 5.8A, SOT-23")
a(T, "DMP3098L-7", "Q", "DMP3098L-7", "MOSFET P-CH 30V 3.8A, SOT-23")
a(T, "DTC043ZEBTL", "Q", "DTC043ZEBTL", "Digital Transistor NPN Pre-Biased 50V 100mA, SOT-416FL")
a(T, "FDMC3612", "Q", "FDMC3612", "MOSFET N-CH 100V 12A, Power33")
a(T, "ME4925-G", "Q", "ME4925-G", "MOSFET P-CH 30V 6.3A, SOP-8")
a(T, "Relay_SRS", "K", "SRS-05VDC-SL", "Relay 5V Coil, THT")
a(T, "SI2333CDS-T1-GE3", "Q", "SI2333CDS-T1-GE3", "MOSFET P-CH 12V 7.1A, SOT-23")
a(T, "SLA-05VDC-SL-A", "K", "SLA-05VDC-SL-A", "Power Relay SPST-NO 30A 5V Coil, THT")
a(T, "VISHAY SI7129DN-T1-GE3", "Q", "SI7129DN-T1-GE3", "MOSFET P-CH 30V 35A, PowerPAK 1212-8")
