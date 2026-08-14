# Lyrics behavior

## Default contract

Treat imported lyrics as ordinary LRC unless evidence says otherwise:

1. parse `[mm:ss.xx]` and `[hh:mm:ss.xxx]` timestamps;
2. allow multiple timestamps on one line;
3. preserve all text after the timestamp;
4. sort stably by time;
5. group only lines with the exact same timestamp;
6. show `No lyrics` in the selected interface language when no usable lines exist.

Do not guess which same-timestamp line is a translation. Let the catalog or the user declare language roles.

## Bilingual lyrics

Support these as separate modes:

- original only;
- translation only;
- both lines grouped at identical timestamps.

If original and translation use separate time axes, keep them separate by default. Do not automatically shift, merge, or reorder them.

## Optional realignment

Only implement realignment after a playback sample proves a systematic mismatch. Document:

- the affected files;
- the detection rule;
- the transformed runtime representation;
- the fallback when confidence is low;
- how to disable the correction.

Never overwrite the source LRC. Store corrections as catalog metadata, a derived cache, or a separate generated file.

## Race safety

When switching songs quickly, associate each asynchronous lyric load with a request ID or expected path. Ignore a response if the active track changed before it completed.

Test lyric timing near the beginning, middle, and end of every newly added song, not only whether lines appear.
