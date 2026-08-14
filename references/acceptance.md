# Acceptance checklist

## Assets and catalog

- Every catalog path exists and uses consistent casing.
- No duplicate track IDs or unintended duplicate audio paths exist.
- Album order and titles are verified.
- High-resolution covers display without stretching or unintended cropping.
- Every shipped asset is referenced or intentionally retained.

## Playback and lyrics

- Audio is audible in Wallpaper Engine, not only in Chrome.
- Play, pause, previous, next, seeking, volume, repeat, and shuffle behave as specified.
- Browsing another artist, creator, collection, or album does not interrupt playback unless designed to do so.
- Rapid switching cannot display lyrics from the previous track.
- Lyrics are checked at the beginning, middle, and end.
- Ordinary imported LRC is not subjected to unrequested bilingual realignment.

## Interface

- Test 16:9, 16:10, 21:9, and at least one small desktop resolution.
- Test mouse, wheel/touchpad, hover transitions, draggable panels, and stacking.
- Menus remain above draggable content.
- Light, dark, and cover-background themes preserve contrast.
- State intended to persist survives wallpaper reload.

## Performance

- Measure idle, pointer interaction, and visualizer-on states.
- Cap render loops and stop hidden effects.
- Provide a low-usage mode when expensive optional effects exist.
- Verify behavior at the Wallpaper Engine default FPS.

## Localization and release

- Wallpaper Engine property labels and in-wallpaper text use the intended languages.
- Missing translations fall back predictably.
- Preview metadata points to an existing file.
- Visible credits include the actual wallpaper author, the OriginalCube reference when the starter/reference design was used, the discreet Skill credit, and material sources.
- Workshop description matches the shipped behavior and attribution.
