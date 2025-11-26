# SVG Rotator

A Python tool to **rotate SVG graphics** around their center point while preserving structure.  
It works by parsing and transforming SVG elements (`path`, `polygon`, `circle`, `ellipse`, `rect`, `line`, etc.) instead of applying a global transform, producing a clean, rotated output SVG.

---

## ✨ Features
- Rotates SVGs by any angle (in degrees).
- Supports:
  - `path` elements (with full parsing of SVG path commands).
  - `polygon` and `polyline`.
  - `circle` and `ellipse`.
  - `rect` (rotated around center, dimensions preserved).
  - `line`.
- Preserves namespaces and structure in the output file.
- Requires the SVG to have a `viewBox` attribute (used to compute rotation center).

---

## 🖥️ Usage

Run the script with:

```bash
python rotate_svg.py input.svg output.svg 45
```

Arguments:
1. `input.svg` – Path to your source SVG file.  
2. `output.svg` – Path to save the rotated result.  
3. `45` – Rotation angle in degrees (positive = clockwise).

Example:

```bash
python rotate_svg.py logo.svg logo_rotated.svg 90
```

This rotates `logo.svg` by **90° clockwise** and saves it as `logo_rotated.svg`.

---

## ⚠️ Notes
- The script **requires `viewBox`** on the root `<svg>` element to determine the center for rotation.  
- Relative and absolute path commands (`M`, `L`, `C`, `Q`, `A`, etc.) are fully supported.  
- Arc commands (`A`) have their endpoint rotated and their rotation adjusted properly.  

