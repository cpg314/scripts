# gnucash2hledger

[Gnucash](https://www.gnucash.org/) to [hledger](http://hledger.org/) conversion, handling currencies and timezones correctly.

## Usage

```bash
$ gnucash2ledger <input.gnucash>
$ gnucash2ledger <input.gnucash> [--out <file>]
```

The gnucash file should be in SQLite format (and not xml).
