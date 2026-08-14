# Catalog and asset workflow

## Intake

Ask the user to supply or authorize:

- highest-resolution album and single covers for bands, solo singers, producers, composers, or other creators;
- original audio files;
- LRC or other lyric files;
- vector or transparent logos;
- desired author name and source records.

Do not scrape copyrighted audio or lyrics from unauthorized mirrors. Record whether a file was supplied by the user, downloaded from a rights-holder page, recreated, converted, or AI-generated.

## Matching order

Use this order and ask for confirmation when ambiguous:

1. normalized exact base-name match;
2. track number plus album metadata;
3. LRC `ti`, `ar`, and `al` tags;
4. embedded audio metadata;
5. similarity suggestion;
6. manual selection.

Never silently bind two plausible lyric files to one song.

## Quality review

Use `scripts/inventory_media.py` to report raster dimensions, vector status, lyric encoding and timestamp counts, optional audio metadata, and exact duplicate hashes. Treat warnings as review prompts:

- prefer high-resolution covers when legitimate sources provide them;
- verify that a small raster is not being stretched as a full cover;
- distinguish deliberately small logos and icons from insufficient album artwork;
- inspect non-UTF-8 or ambiguous lyric encoding before conversion;
- confirm that an LRC contains usable timestamps;
- compare exact duplicates before removing files.

The inventory tool may report that audio metadata was not inspected when the optional `mutagen` library is unavailable. The Agent can use another safe local metadata tool or ask the user for the missing title, artist, album, and order; this is not a reason to block the project.

## Preferred catalog fields

```json
{
  "id": "stable-track-id",
  "title": "Track title",
  "artist": "Artist",
  "vocalist": "Optional vocalist",
  "producer": "Optional producer or music creator",
  "composer": "Optional composer",
  "collectionId": "artist-or-creator-group",
  "albumId": "album-id",
  "trackNumber": 1,
  "audio": "assets/audio/song.mp3",
  "lyrics": "assets/lyrics/song.lrc",
  "cover": "assets/covers/album.jpg",
  "trackCover": "",
  "accentColor": "#3388bb",
  "sourceId": "material-record-id"
}
```

Use a track-specific cover only when present; otherwise fall back to the album cover.

The Agent may build the catalog directly after reviewing the inventory. It should not pretend uncertain matches are confirmed. When filenames, tags, folders, and track lists disagree, show the alternatives to the user.

## File handling

- Preserve original files outside the project.
- Copy only referenced release assets into the wallpaper project before publishing; Workshop subscribers cannot read the author's unrelated local source folders.
- Normalize unsafe filenames only in the working copy and update catalog paths together.
- Detect text encoding before declaring an LRC corrupted.
- Hash or compare sizes before deleting apparent duplicates.
- Do not infer duplicate songs solely from similar titles; compare metadata and audio when needed.
