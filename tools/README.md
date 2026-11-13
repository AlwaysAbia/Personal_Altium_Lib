# Library tools

Python scripts used to bulk-edit the `.SchLib` and `.PcbLib` files directly, without Altium. Needs Python 3 and `olefile` (`pip install olefile`).

Always close the libraries in Altium first, write output to a separate folder, run the matching verify script, and only then copy the files over the originals.

## Core modules

| File | What it does |
|---|---|
| `cfb.py` | Reads an OLE compound file (the container format of SchLib/PcbLib) into a tree, and writes a tree back out. Round-trips every library in this repo with identical content. |
| `migrate.py` | SchLib record helpers (`parse`, `serialize`, `kv`, `unkv`, `get`, `setkey`) plus the parameter migration. |
| `pcbparse.py` | Walks a PcbLib footprint's primitives and decodes pads (position, size, hole, layer). |

## One-off steps (already applied, kept for reference and reuse)

| Step | Map / data | Apply | Verify |
|---|---|---|---|
| Parameters: Value, Manufacturer, Manufacturer Part Number, links | `build_map.py` → `data/mapping.json` (uses `data/comps.json`, `data/lcsc/`) | `migrate.py <out_dir> <libs>` | `verify.py <src_dir> <out_dir>` |
| Footprint link pointer fix (OwnerIndex) | n/a | `fix_owner.py <out_dir> <libs>` | n/a |
| Schematic names, designators, descriptions | `rename_map.py` | `apply_names.py <out_dir> <libs>` | `verify2.py <src_dir> <out_dir>` |
| Footprint names, descriptions, merges, re-tie | `fp_map.py` (pad data in `data/fp_geom.json`) | `apply_fp.py <pcb_src> <sch_src> <pcb_out> <sch_out>` | `verify_fp.py <pcb_src> <sch_src> <pcb_out> <sch_out>` |

The verify scripts check the result against the given source folder, so they only pass for the step they belong to. To re-run one, first restore the source files from the commit before that step.

`extract.py <out.json>` (run from the repo root) dumps every component's parameters to JSON.

## File format notes

- **SchLib:** each component is a storage whose `Data` stream is a list of records. Each record is a 4-byte header (low 24 bits = length, high byte = type: 0 = `|KEY=VALUE|` text, 1 = binary pin) followed by the payload. Non-ASCII text is stored twice: `KEY` in cp1252 and `%UTF8%KEY` in UTF-8.
- **OwnerIndex is an absolute record position.** Footprint model records (44 → 45 → 46/48) point to their parent this way. Inserting or removing any record before them breaks the links unless OwnerIndex is recomputed (`fix_owner.py`).
- **Storage names** are the component or footprint name with `/` replaced by `_`, cut to 31 characters. Names of 31+ characters need a `SectionKeys` entry; every current name is shorter.
- **SchLib FileHeader** holds `LibRefN` / `CompDescrN` for each component and must match the components.
- **PcbLib:** a footprint's name is stored in its storage name, at the start of its `Data` stream (length-prefixed), in `Parameters` (`PATTERN`, `DESCRIPTION`), in the `Library/Data` footprint list and in `Library/ComponentParamsTOC`. 3D bodies reference embedded STEP models by ID; the `MODEL.NAME` filenames don't need to match the footprint.
