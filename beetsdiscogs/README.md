# beets-discogs

Export your [beets](http://beets.io/) music library to [Discogs](https://www.discogs.com/) effortlessly.

## Usage

```bash
Usage:
  beets-discogs [options] <library> <token>

  --ask      Ask for releases that cannot be found.
  --verbose
```

### Arguments
The argument `library` is the path to your Beets `.blb` library.

The token can be obtained in your [Discogs setting page](https://www.discogs.com/settings/developers) (button "Generate token").

### Mode of operation

There are three ways used to match new releases:
1. Use the `musicbrainz_id` field stored in the beets database, and a cross-listing between Musicbrainz and Discogs, if present.
2. Do a search on Discogs from the metadata (album, artist, year).
3. Ask to input the release ID manually.

The Discogs release IDs will be stored into the beets database (key `discogs_id`), and will be used on future runs.

Existing releases will not be added twice.
