#!/usr/bin/env python3
"""Pregled NovaStar konfiguracionih fajlova (.rcfgx, .rcfg, .oscfg).

.rcfgx je ZIP arhiva sa XML fajlom (ScanBoardProperty). .oscfg je ZIP sa
backup/*.rcfgx unutra. Skripta ispisuje kljucna polja za provjeru prije
slanja na receiving karticu. Kad se zada vise fajlova, ispisuje ih jedan
pored drugog i oznacava razlike.

Upotreba:
    python inspect_rcfgx.py fajl.rcfgx [drugi.rcfgx ...]
Samo standardna Python biblioteka, Python 3.8+.
"""
import io
import re
import sys
import zipfile

# (oznaka u XML-u, opis)
FIELDS = [
    ("@xml", "XML unutra (ime)"),
    ("ScanBoardName", "Kartica za koju je pravljen"),
    ("ProgramVersion", "Firmver kartice u fajlu"),
    ("RCFGXVersion", "Napravljen u NovaLCT"),
    ("ChipCode", "Driver cip (interni kod)"),
    ("DecType", "Dekoder"),
    ("ModulePixelCols", "Modul sirina (px)"),
    ("ModulePixelRows", "Modul visina (px)"),
    ("ScanType", "Scan"),
    ("DataGroup", "Data grupe"),
    ("ScreenDriveType", "Tip pogona"),
    ("Width", "Kabinet sirina (px)"),
    ("Height", "Kabinet visina (px)"),
    ("ModuleCols", "Kabinet: modula po sirini"),
    ("ModuleRows", "Kabinet: modula po visini"),
    ("GrayDepth", "Dubina sive (bit)"),
    ("RefNumPerVs", "RefNumPerVs"),
    ("GammaValue", "Gama (x10)"),
]


# ChipCode -> ime cipa kako ga prikazuje NovaLCT. Samo parovi potvrdjeni
# u praksi; dopuni kad potvrdis novi (Load from... pa procitaj tab).
KNOWN_CHIPCODES = {
    "74": "ICN2038A",
    "115": "SM16188B",
}


def first(tag, xml):
    m = re.search(r"<%s>([^<]*)</%s>" % (tag, tag), xml)
    return m.group(1).strip() if m else "-"


def xmls_from_zip(data, label):
    """Vrati listu (oznaka, xml_tekst) iz .rcfgx ili .oscfg sadrzaja."""
    out = []
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        # stari .rcfg moze biti cisti XML
        text = data.decode("utf-8", "replace")
        if "<ScanBoardProperty" in text:
            out.append((label, "(cist XML)", text))
        return out
    for name in z.namelist():
        low = name.lower()
        if low.endswith(".xml"):
            text = z.read(name).decode("utf-8", "replace")
            if "<ScanBoardProperty" in text:
                out.append((label, name, text))
        elif low.endswith(".rcfgx"):  # ugnijezdeno u .oscfg
            out.extend(xmls_from_zip(z.read(name), "%s > %s" % (label, name)))
    return out


def summarize(label, xmlname, xml):
    row = {"@label": label}
    for tag, _ in FIELDS:
        row[tag] = xmlname if tag == "@xml" else first(tag, xml)
    code = row["ChipCode"]
    if code in KNOWN_CHIPCODES:
        row["ChipCode"] = "%s (%s)" % (code, KNOWN_CHIPCODES[code])
    return row


def warnings(row, filename):
    w = []
    nums = re.findall(r"\d{4,5}", filename)
    xmlnums = re.findall(r"\d{4,5}", row["@xml"])
    if nums and xmlnums and set(nums) != set(xmlnums):
        w.append("Brojevi u imenu fajla (%s) i u XML-u (%s) se razlikuju: "
                 "fajl je mozda preimenovan." % ("+".join(nums), "+".join(xmlnums)))
    try:
        if int(row["Width"]) > int(row["ModulePixelCols"]) or \
           int(row["Height"]) > int(row["ModulePixelRows"]):
            w.append("Kabinet (%sx%s) je veci od modula (%sx%s): u Cabinet "
                     "Information upisi stvarnu velicinu prije Send." % (
                         row["Width"], row["Height"],
                         row["ModulePixelCols"], row["ModulePixelRows"]))
    except ValueError:
        pass
    return w


def main(paths):
    rows = []
    for p in paths:
        with open(p, "rb") as f:
            data = f.read()
        found = xmls_from_zip(data, p)
        if not found:
            print("! %s: nije pronadjen ScanBoardProperty XML" % p)
        for label, name, xml in found:
            r = summarize(label, name, xml)
            r["@warn"] = warnings(r, p.replace("\\", "/").split("/")[-1])
            rows.append(r)
    if not rows:
        return 1
    labw = max(len(d) for _, d in FIELDS) + 2
    colw = 30
    for i, r in enumerate(rows, 1):
        print("[%d] %s" % (i, r["@label"]))
    print()
    print("Polje".ljust(labw) + "".join(("[%d]" % i).ljust(colw) for i in range(1, len(rows) + 1)))
    print("-" * (labw + colw * len(rows)))
    for tag, desc in FIELDS:
        vals = [r[tag] for r in rows]
        mark = "  <-- razlika" if len(rows) > 1 and len(set(vals)) > 1 else ""
        print(desc.ljust(labw) + "".join(v[:colw - 2].ljust(colw) for v in vals) + mark)
    for i, r in enumerate(rows, 1):
        for w in r["@warn"]:
            print("UPOZORENJE [%d]: %s" % (i, w))
    print("\nNapomena: ChipCode je NovaStar interni broj; ime cipa (npr. ICN2038A) "
          "pokazuje tab Receiving Card nakon Load from...")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(main(sys.argv[1:]))
