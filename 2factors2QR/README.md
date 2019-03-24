# 2factors2QR
 
Generate QR codes to quickly add/restore 2 factor authentication codes from a mobile device.

## Usage

```bash
2factors2QR

Usage:
  2factors2QR <label> <username> <secret>
  2factors2QR <filename> [--combine]
```

The second method reads the codes from a CSV file with three colums per line: label, email address, secret key. Use the `--combine` option to combine the codes to a PDF. Otherwise, one PNG image per code is generated.
