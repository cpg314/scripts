# zotexport
Export [Zotero](https://www.zotero.org/) collections to a folder.

## Usage

```bash
$ zotexport login <userID> <key>
$ zotexport list
$ zotexport export <collectionID> [--recursive]
```

You should first login with the `login` command.

The `list` command lists all your collections with their IDs.

The `export` command exports a collection in the current folder. If you add the `--recursive` flag, all subcollections will be included. The folder structure will match the structure of collections and subcollections.
