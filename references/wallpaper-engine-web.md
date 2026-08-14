# Wallpaper Engine Web wallpaper notes

Read the current official documentation before relying on platform behavior:

- Web overview: https://docs.wallpaperengine.io/en/web/overview.html
- Creating a Web wallpaper: https://docs.wallpaperengine.io/en/web/first/gettingstarted.html
- Web user properties: https://docs.wallpaperengine.io/en/web/customization/properties.html
- Audio visualizer: https://docs.wallpaperengine.io/en/web/audio/visualizer.html
- FPS control: https://docs.wallpaperengine.io/en/web/performance/fps.html
- CEF debugging: https://docs.wallpaperengine.io/en/web/debug/debug.html

## Architecture rules

- Package required HTML, CSS, JavaScript, images, fonts, audio, and lyrics locally.
- Use relative paths and URL-encode paths containing spaces, non-ASCII characters, or `#`.
- Register `window.wallpaperPropertyListener` globally and early.
- Treat `applyUserProperties` as partial updates after the initial callback.
- Keep Wallpaper Engine property keys and values stable when localizing display labels.
- Use `window.wallpaperRegisterAudioListener` once for system-audio visualization.
- Respect the configured FPS and independently limit expensive visualizer or pointer loops.
- Use CEF DevTools for audio, media state, callback, and rendering diagnosis.

## Important boundaries

- Web and Scene wallpapers are different project types; there is no automatic conversion.
- Web file/directory user properties officially target image and video imports, not arbitrary MP3/LRC libraries.
- A Web wallpaper cannot change Wallpaper Engine's global fullscreen or pause policy.
- A Web wallpaper must not assume it can launch the default browser or arbitrary executables.
- Workshop updates can replace files inside a subscribed wallpaper directory; never store user-created libraries there.

Verify undocumented browser APIs in Wallpaper Engine CEF before committing the product design to them.
