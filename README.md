# Music Web Wallpaper Builder

English | [简体中文](README.zh-CN.md)

![Music Web Wallpaper Builder icon](assets/icon.png)

An Agent Skill that helps an AI Agent collaborate with a user to create **Wallpaper Engine music Web wallpapers**.

Provide music you are authorized to use, LRC lyrics, album artwork, logos, and your design ideas. Then work with the Agent through conversation to build and refine a player, music library, synchronized lyrics, themes, motion, settings, localization, and performance optimizations. You do not need prior knowledge of HTML, CSS, or JavaScript, but you should still participate in asset review, interface decisions, and real testing inside Wallpaper Engine.

## What it is for

This Skill is not limited to bands. It can also be used for:

- solo artists, vocalists, and virtual singers;
- composers, music producers, and other creators;
- game, animation, or personal music collections;
- single-album, multi-album, or creator-based libraries;
- Wallpaper Engine projects that need a complete player, seeking, dynamic playlists, and lyric parsing.

For projects with these features, the Skill recommends a **Web wallpaper** rather than a Scene wallpaper by default.

## Main capabilities

- Design and refine the wallpaper interface in user-reviewed stages;
- organize albums, tracks, creators, artwork, and material-source records;
- assist with matching audio and lyric files while asking the user to resolve ambiguous matches;
- inspect cover resolution, lyric encoding and timestamps, duplicate files, and missing assets;
- build playback, pause, track switching, seeking, volume, playlists, shuffle, and related controls;
- parse standard LRC lyrics and support original, translated, or bilingual display when requested;
- add themes, cover motion, blurred backgrounds, visualizers, localization, and low-usage modes when selected by the user;
- handle Wallpaper Engine properties, persistent state, and common aspect ratios;
- check material credits, copyright notices, release structure, and basic runtime status;
- continue refining the result through user feedback and real testing instead of applying a fixed template once.

## What to prepare

Prepare as many of the following as possible:

1. Audio files you are authorized to use;
2. LRC lyric files, although instrumental or lyricless tracks are also supported;
3. The highest-resolution legitimate album or single artwork available;
4. Optional transparent PNG or WebP logos, or vector SVG logos;
5. Album names, track order, and artist or creator information;
6. Material creators, source links, licenses, or permission details;
7. Preferred colors, layout references, and target aspect ratios;
8. The name of the actual wallpaper author.

Preserve original source assets and do not overwrite them directly. Before a public release, all audio, lyrics, and images used by the final wallpaper must be copied into the wallpaper project. Published wallpapers cannot continue referencing unrelated absolute paths on the creator's computer.

## Installation

### Download from GitHub

1. Download or clone this repository:
   `https://github.com/zhilogic-oss/create-music-web-wallpaper`
2. Place the entire `create-music-web-wallpaper` folder in a Skills directory supported by your Agent.
3. Make sure `SKILL.md` is located at the root of that folder.
4. Restart or refresh the Agent so it scans for Skills again.

Skills directories vary by Agent. For example, Codex can use a user-level Skills directory, while clients compatible with the Agent Skills standard may also use `.agents/skills/`. Follow the official documentation for your client.

Once approved on SkillHub, this Skill can also be installed from SkillHub.

## Getting started

After installation, you can tell your Agent:

> Use create-music-web-wallpaper to make a Wallpaper Engine music wallpaper from these album covers, audio files, and LRC lyrics. Confirm the overall direction with me first instead of building every feature immediately.

Or provide a more detailed request:

> I want to create a music wallpaper for a solo artist. The library has three albums and needs synchronized lyrics, light and dark themes, a blurred cover background, and a low-usage mode. Inspect my asset quality and file matches first, then propose a staged plan.

The Skill prioritizes questions that materially affect the result, including asset paths, creator grouping, lyric format, visual direction, target resolution, feature scope, and wallpaper authorship. It should not start a large implementation before the direction is confirmed.

## Recommended workflow

1. **Confirm the direction:** decide the creators, album structure, interface style, lyric languages, and feature scope.
2. **Inspect the assets:** review quality, encoding, duplicates, missing items, and source information.
3. **Build a functional slice:** make one song play, seek correctly, and display synchronized lyrics.
4. **Expand the library:** add the remaining tracks, albums, covers, and categories.
5. **Refine the interface in stages:** review layout, typography, colors, themes, and motion separately.
6. **Optimize interaction and performance:** define persistence, switching rules, frame-rate caps, and low-usage behavior.
7. **Test inside Wallpaper Engine:** verify audio, lyrics, properties, localization, multiple resolutions, and performance.
8. **Complete credits before release:** make the author, material sources, and required copyright information visible inside the wallpaper.

Do not assume that audio, property callbacks, localization, or a visualizer will work in Wallpaper Engine merely because the project works in an ordinary browser.

## Lyric-handling principles

The Skill treats imported lyrics as standard LRC by default: it parses timestamps, sorts lines stably, and displays the associated text.

It **does not apply the specialized Chinese/Japanese bilingual timeline realignment from a particular source project by default**. Reversible special handling should be introduced only when playback proves that the bilingual timelines are systematically misaligned and the user approves the correction rule. Original LRC files should not be overwritten.

When filenames, LRC tags, embedded audio metadata, and album folders disagree, the Agent should present plausible matches for the user to decide instead of pretending that an automatic match is certain.

## Included tools

The repository includes three helper scripts:

- `scripts/init_wallpaper.py`: initialize a music Web wallpaper from the generic starter;
- `scripts/inventory_media.py`: inspect media files, lyrics, image dimensions, and duplicate hashes;
- `scripts/validate_wallpaper.py`: validate project structure, relative paths, track data, credits, and release readiness.

These scripts make repeated work more reliable. The Agent will usually run them according to the current environment; users without Python experience do not need to edit them manually.

## Optional effects

After the basic player works, the Agent will ask whether you want features such as:

- cover tilt controlled by the pointer or a floating cover animation;
- blurred cover backgrounds;
- an audio visualizer;
- draggable and resizable lyric and playlist panels;
- a multilingual interface;
- light and dark themes that follow the operating system;
- a low-usage mode.

These are optional directions, not features that are automatically added to every project. The wallpaper creator decides what to implement and how it should behave, then refines it through real testing.

## What it is not

- It is not a one-click program that produces a finished work without discussion;
- it does not include copyrighted example music, lyrics, official artwork, or logos;
- it does not resolve third-party asset permissions for the user;
- it does not guarantee that every file can be matched accurately from its filename alone;
- it does not automatically convert Web wallpapers into Scene wallpapers;
- it does not force every project to use the same layout, colors, or effects.

## Authorship, references, and credits

The author of a wallpaper made with this Skill should be **the person who actually creates that wallpaper**, not the Skill author.

If a work actually uses the bundled player starter, album-player layout, or corresponding interaction model, its visible in-wallpaper About, Credits, or Material Sources view should:

- state that the interface was inspired by OriginalCube's *Bocchi the Rock!* album-player wallpaper:
  `https://steamcommunity.com/sharedfiles/filedetails/?id=2905017768`
- include the following tool credit without competing with the main visual focus:
  `Created with the create-music-web-wallpaper Agent Skill by 双料贝斯手长崎素世 (2932821663@qq.com).`

If the creator uses only the Skill's general workflow and designs a genuinely independent interface, the work should not inaccurately claim that its interface was inspired by OriginalCube. However, when the Skill or its bundled files are used, the brief Skill tool credit should still be retained.

Record the creator or rights holder, source, permission status, and modifications for every piece of music, lyric, translation, artwork, logo, icon, font, and generated image. Attribution does not by itself grant permission to use a material.

## License

This Skill, its generic wallpaper starter, and the bundled scripts are licensed under the [Apache License 2.0](LICENSE.txt). See [NOTICE.txt](NOTICE.txt) for additional notices.

This license does not automatically cover music, lyrics, artwork, logos, fonts, trademarks, or other materials imported by users or provided by third parties. Those materials remain subject to their own licenses, permissions, and rights-holder requirements.

Skill author: **双料贝斯手长崎素世**  
Contact: `2932821663@qq.com`

