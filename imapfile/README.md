# imapfile

Extract email attachments from your terminal with rules.

## Configuration

A configuration file should be created in `~/.config/imapfile.yaml`, with the following format:

```yaml
headers:
- - sender@domain1.com
  - invoice
  - bill
  - - pdf
    -jpg
- ...
imap:
- imap.domain.com
- user@domain.com
- password
```

Attachments in `pdf` or `jpg` format from `sender@domain1.com` with subject containing `Invoice` will then be downloaded in the current folder, with filename mask `bill-YYYY-MM-DD-*.ext`.
