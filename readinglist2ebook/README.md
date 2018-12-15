# readinglist2ebook

Export [Pocket](https://getpocket.com) or [Wallabag](https://www.wallabag.org/) reading lists to an epub/mobi ebook, with images.

## Usage

```bash
$ readinglist2ebook login <server> <user> <token>
$ readinglist2ebook export [--mobi] [--limit=<n>]
$ readinglist2ebook toKindle
```

For Pocket, the `server` argument to the login command should be `pocket`.

The images are cached in the `~/readinglist2ebook` folder, and cleaned on the next run when an article is marked as read.

To use the `mobi` conversion, you will need the [kindlegen command line tool](https://www.amazon.com/gp/feature.html?docId=1000765211).

The `toKindle` command copies the resulting `mobi` file to your Kindle.
