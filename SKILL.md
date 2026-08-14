---
name: create-music-web-wallpaper
description: Create, rebuild, or refine interactive music and album-player wallpapers for Wallpaper Engine using HTML, CSS, and JavaScript. Use when an agent needs to turn user-provided or authorized music by bands, solo singers, vocalists, producers, composers, or other creators—together with album covers, audio, LRC lyrics, logos, and visual direction—into a Web wallpaper; build library navigation, synchronized lyrics, themes, optional motion, settings, localization, performance modes, and credits; or iterate on the interface through user feedback and Wallpaper Engine testing. Prefer Web wallpapers over Scene wallpapers for full music-player behavior, seeking, dynamic playlists, and lyric parsing.
---

# Create Music Web Wallpaper

Build a Wallpaper Engine **Web wallpaper** as a staged collaboration with the user. Preserve source assets, make attribution visible, and validate playback inside Wallpaper Engine rather than assuming ordinary-browser behavior is sufficient.

## Load only the references needed

- Read [references/wallpaper-engine-web.md](references/wallpaper-engine-web.md) before creating or changing a Wallpaper Engine project.
- Read [references/catalog-and-assets.md](references/catalog-and-assets.md) when collecting, naming, matching, or importing covers, audio, logos, and lyrics.
- Read [references/lyrics.md](references/lyrics.md) before implementing lyric parsing or synchronization.
- Read [references/credits-and-rights.md](references/credits-and-rights.md) before adding third-party material or preparing a release.
- Read [references/acceptance.md](references/acceptance.md) before handing off a build or claiming completion.

## 1. Begin with an intake conversation

Do not start a large build until the user has confirmed the direction. Ask only the questions that materially change the result:

- wallpaper title, bands, solo singers, vocalists, producers, composers, other music creators, albums, and desired grouping;
- paths to user-provided audio, covers, lyrics, logos, and fonts;
- desired visual mood, colors, reference screenshots, and target resolutions;
- lyric languages and whether the files are ordinary single-language LRC, same-timestamp bilingual LRC, or separately timed translations;
- wallpaper author name and any additional credits;
- minimum feature set and performance preference.

Recommend collecting the highest-resolution legitimate album covers available. Ask for lossless logos when possible. Never silently replace user assets with approximate search results.

If online research is needed, use current official Wallpaper Engine documentation for platform behavior and authoritative or rights-holder sources for metadata. Do not download copyrighted audio or lyrics from unauthorized sources. Prefer user-supplied files.

## 2. Choose Web wallpaper architecture

Use HTML, CSS, and JavaScript when the requested wallpaper includes a music player, progress seeking, dynamic playlists, LRC parsing, draggable panels, multilingual UI, or user-imported libraries. Do not propose an automatic Web-to-Scene conversion.

Keep these concerns separate:

- catalog and source metadata;
- audio playback state;
- lyrics parsing and display;
- visualizer rendering;
- themes and layout;
- Wallpaper Engine property bridge;
- localization;
- persistent user state.

For an empty project, initialize the bundled starter:

```powershell
python scripts/init_wallpaper.py <target-directory> --title "Wallpaper title" --author "Wallpaper author"
```

When Python is not on `PATH`, locate an available Python runtime instead of rewriting the scaffold by hand. Treat `assets/starter/` as boilerplate: adapt it rather than forcing its design on the user.

## 3. Inventory and organize assets

Run the inventory tool on user-provided material:

```powershell
python scripts/inventory_media.py <material-directory> --output <material-directory>/media-inventory.json --hash
```

Review duplicate hashes, unmatched audio/LRC pairs, lyric encoding and timestamps, raster-image dimensions, available audio metadata, and ambiguous names with the user. A warning is a prompt for review, not proof that an asset is unusable: small logos and intentional non-square artwork may be valid. Preserve originals outside the working copy. Use stable relative paths and never overwrite a source file merely to fix runtime behavior.

Use the inventory as evidence, then perform the library matching with the Agent. Match normalized filenames, LRC metadata, embedded audio metadata when accessible, album folders, and user-provided track lists. Present ambiguous matches for confirmation; do not require or build a separate automatic importer merely to use this Skill.

Copy every media file selected for a publishable wallpaper into the wallpaper project. A subscriber cannot access the original creator's unrelated local folders. Keep the original source library outside the project as a backup, but make all catalog paths project-relative.

Create or update a catalog that records at least:

- stable track ID;
- title, performing artist or group, optional vocalist/producer/composer credits, collection, album, and track order;
- audio path and optional lyric path;
- album cover and optional track-specific cover;
- accent/background colors;
- visible source and rights metadata.

Do not infer an exact album track order from memory when it can be verified.

## 4. Treat lyrics conservatively

Default to standard LRC behavior: parse timestamps, sort lines, and display the text attached to each timestamp.

Do **not** apply bilingual timestamp realignment by default. The specialized Chinese/Japanese repair used by one source project is not a universal rule and can damage ordinary lyrics.

Only introduce bilingual grouping or realignment when:

1. the file format clearly contains multiple languages;
2. an observed playback test proves that the timelines are mismatched; and
3. the user approves the correction rule.

Keep the correction reversible and separate from the original LRC. See [references/lyrics.md](references/lyrics.md).

## 5. Build a functional slice before polishing

Implement and verify one complete path first:

1. one album cover displays;
2. one song loads and produces sound;
3. play, pause, seeking, and volume work;
4. lyrics follow playback;
5. the track appears in the list;
6. its source is visible in the credits view.

Then expand the catalog and add optional features. Avoid changing localization, playback, and visualizer internals in one untested batch.

After the basic player works, briefly ask whether the user wants optional effects such as cover motion, blurred cover backgrounds, an audio visualizer, draggable panels, multilingual controls, system-theme following, or a low-usage mode. Do not add them automatically, bundle an effect installer, or insist that they are required. Implement only the features the user explicitly chooses through the normal Agent editing workflow.

## 6. Iterate on the interface through conversation

Treat design as a sequence of user-reviewed milestones:

1. layout and information hierarchy;
2. album/track navigation;
3. typography and colors;
4. themes and cover/background behavior;
5. motion and visualizer;
6. settings and localization;
7. performance and unusual aspect ratios.

After each milestone, describe the visible result and ask the user to test it in Wallpaper Engine. When screenshots are available, inspect them and change measured spacing, scale, stacking, and interaction behavior instead of guessing.

Preserve accepted behavior while editing a later milestone. Record deferred ideas separately rather than slipping them into the current change.

## 7. Add features with explicit state rules

For each control, define:

- what it changes;
- whether it affects browsing, playback, or both;
- whether the value persists across reloads;
- whether Wallpaper Engine properties override the in-wallpaper value;
- its keyboard, pointer, touchpad, and localization behavior.

Recommended defaults:

- switching album filters or artist views must not interrupt the currently playing song;
- clicking a track or using previous/next may change playback;
- shuffle should avoid repeats within one cycle;
- theme, background mode, panel layout, volume, and performance mode should persist;
- low-usage mode should disable only expensive effects and retain core player information;
- cover motion and visualizer frame rates should be capped independently.

## 8. Make credits visible and accurate

Every generated wallpaper must include an accessible, visible **About / Credits / Material Sources** view. Do not hide attribution only in repository files or the Workshop description.

Keep authorship roles distinct:

- Set the wallpaper author to the person actually making that wallpaper.
- When the bundled starter, album-player layout, or interaction design is actually derived from the reference, credit it as: `Inspired by OriginalCube's Bocchi the Rock! album-player wallpaper` and link to `https://steamcommunity.com/sharedfiles/filedetails/?id=2905017768`.
- When the user creates a genuinely independent interface and uses only the general workflow, do not make the inaccurate claim that its interface was inspired by OriginalCube. Record the catalog credit flag accordingly.
- Add a separate tool credit: `Created with the create-music-web-wallpaper Agent Skill by 双料贝斯手长崎素世 (2932821663@qq.com).`
- Keep the tool credit readable and easy to find in About, Credits, or Material Sources, but visually subordinate to the wallpaper title, actual author, cover, and playback information. Do not place it as a persistent banner, splash screen, or dominant main-interface label.
- Do **not** describe 双料贝斯手长崎素世 as the wallpaper author unless that person actually made the wallpaper.

List every third-party cover, audio file, lyric, translation, logo, icon, font, and generated image with its creator or rights holder, source link or supplied-file note, license/permission status, and modifications. Follow [references/credits-and-rights.md](references/credits-and-rights.md).

## 9. Validate before delivery

Run the included validator:

```powershell
python scripts/validate_wallpaper.py <wallpaper-directory>
```

Run project-specific automated tests, then test the actual Wallpaper Engine build. Ordinary Chrome playback does not prove CEF audio, localization, property callbacks, or visualizer behavior.

Do not claim completion while required assets are missing, audio is silent, attribution is invisible, or only one resolution has been checked. Use [references/acceptance.md](references/acceptance.md).

## 10. Keep release boundaries honest

- Clearly label fan-made and unofficial work.
- Do not claim ownership of music, lyrics, translations, official artwork, or trademarks.
- Do not imply that visible attribution grants a license.
- Do not publish user-provided private files without permission.
- Do not bundle copyrighted examples in this skill or reuse another wallpaper's code/assets without permission.
- Preserve the bundled Apache-2.0 `LICENSE.txt` and `NOTICE.txt` when distributing a wallpaper based on the starter.
- Keep the starter generic; replace every placeholder before publishing.
