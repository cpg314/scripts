# flickrupload

Recursively upload a folder of photos to [Flickr](https://flickr.com/), with the option to export albums from [Shotwell](https://wiki.gnome.org/Apps/Shotwell), the GNOME photo manager.

## Usage

```bash
Usage:
  flickrupload [options] <folder> <key> <secret>

  --shotwell=<library>       Export photo sets from Shotwell library
  --check-duplicates         Check for duplicates remotely before uploading
  --resize=<size>            Resize pictures to a maximum of size x size pixels
```

### Arguments
An API and secret key can be obtained [here](https://www.flickr.com/services/apps/create/apply/).
