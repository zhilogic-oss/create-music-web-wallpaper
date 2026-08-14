(() => {
  "use strict";

  const catalog = window.MUSIC_WALLPAPER_CATALOG || { albums: [], tracks: [], materials: [] };
  const audio = document.getElementById("audio");
  const elements = {
    title: document.getElementById("wallpaperTitle"),
    cover: document.getElementById("cover"),
    artist: document.getElementById("artist"),
    trackTitle: document.getElementById("trackTitle"),
    album: document.getElementById("album"),
    lyrics: document.getElementById("lyrics"),
    albumFilters: document.getElementById("albumFilters"),
    trackList: document.getElementById("trackList"),
    play: document.getElementById("playButton"),
    previous: document.getElementById("previousButton"),
    next: document.getElementById("nextButton"),
    progress: document.getElementById("progress"),
    currentTime: document.getElementById("currentTime"),
    duration: document.getElementById("duration"),
    volume: document.getElementById("volume"),
    theme: document.getElementById("themeButton"),
    credits: document.getElementById("creditsButton"),
    creditsDialog: document.getElementById("creditsDialog"),
    materialCredits: document.getElementById("materialCredits")
  };

  const state = {
    currentTrackId: null,
    selectedAlbumId: "all",
    lyrics: [],
    activeLyricIndex: -1,
    lyricRequest: 0
  };

  function mediaUrl(path) {
    return encodeURI(String(path || "")).replace(/#/g, "%23");
  }

  function formatTime(seconds) {
    if (!Number.isFinite(seconds)) return "0:00";
    const whole = Math.max(0, Math.floor(seconds));
    return `${Math.floor(whole / 60)}:${String(whole % 60).padStart(2, "0")}`;
  }

  function escapeText(value) {
    const node = document.createElement("span");
    node.textContent = String(value ?? "");
    return node.innerHTML;
  }

  function tracksInView() {
    if (state.selectedAlbumId === "all") return catalog.tracks || [];
    return (catalog.tracks || []).filter((track) => track.albumId === state.selectedAlbumId);
  }

  function currentTrack() {
    return (catalog.tracks || []).find((track) => track.id === state.currentTrackId) || null;
  }

  function albumFor(track) {
    return (catalog.albums || []).find((album) => album.id === track?.albumId) || null;
  }

  function renderAlbumFilters() {
    const albums = [{ id: "all", title: "All" }, ...(catalog.albums || [])];
    elements.albumFilters.replaceChildren(...albums.map((album) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `album-filter${album.id === state.selectedAlbumId ? " active" : ""}`;
      button.textContent = album.title;
      button.addEventListener("click", () => {
        state.selectedAlbumId = album.id;
        renderAlbumFilters();
        renderTrackList();
      });
      return button;
    }));
  }

  function renderTrackList() {
    const tracks = tracksInView();
    if (!tracks.length) {
      const empty = document.createElement("li");
      empty.className = "empty-state";
      empty.innerHTML = "Edit <code>static/js/catalog.js</code> to add authorized music.";
      elements.trackList.replaceChildren(empty);
      return;
    }

    elements.trackList.replaceChildren(...tracks.map((track, index) => {
      const item = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.className = `track-button${track.id === state.currentTrackId ? " active" : ""}`;
      button.innerHTML = `
        <span class="track-index">${String(index + 1).padStart(2, "0")}</span>
        <span class="track-copy">
          <span class="track-name">${escapeText(track.title)}</span>
          <span class="track-artist">${escapeText(track.artist || "Unknown artist")}</span>
        </span>`;
      button.addEventListener("click", () => loadTrack(track.id, true));
      item.append(button);
      return item;
    }));
  }

  function parseLrc(text) {
    const result = [];
    const timestamp = /\[(?:(\d{1,2}):)?(\d{1,3}):(\d{1,2})(?:[.:](\d{1,3}))?\]/g;
    for (const rawLine of text.replace(/^\uFEFF/, "").split(/\r?\n/)) {
      const content = rawLine.replace(timestamp, "").trim();
      if (!content) continue;
      timestamp.lastIndex = 0;
      let match;
      while ((match = timestamp.exec(rawLine)) !== null) {
        const fraction = match[4] ? Number(`0.${match[4].padEnd(3, "0").slice(0, 3)}`) : 0;
        result.push({
          time: Number(match[1] || 0) * 3600 + Number(match[2]) * 60 + Number(match[3]) + fraction,
          text: content
        });
      }
    }
    return result.sort((a, b) => a.time - b.time);
  }

  function renderLyrics() {
    if (!state.lyrics.length) {
      const line = document.createElement("p");
      line.className = "lyric-line active";
      line.textContent = currentTrack()?.lyrics ? "Lyrics could not be loaded." : "No lyrics";
      elements.lyrics.replaceChildren(line);
      return;
    }
    elements.lyrics.replaceChildren(...state.lyrics.map((line, index) => {
      const paragraph = document.createElement("p");
      paragraph.className = `lyric-line${index === state.activeLyricIndex ? " active" : ""}`;
      paragraph.textContent = line.text;
      return paragraph;
    }));
  }

  async function loadLyrics(track) {
    const request = ++state.lyricRequest;
    state.lyrics = [];
    state.activeLyricIndex = -1;
    renderLyrics();
    if (!track.lyrics) return;
    try {
      const response = await fetch(mediaUrl(track.lyrics), { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const lyrics = parseLrc(await response.text());
      if (request !== state.lyricRequest || track.id !== state.currentTrackId) return;
      state.lyrics = lyrics;
      renderLyrics();
    } catch (error) {
      if (request !== state.lyricRequest) return;
      console.warn("Lyrics failed to load", track.lyrics, error);
      renderLyrics();
    }
  }

  async function loadTrack(trackId, autoplay) {
    const track = (catalog.tracks || []).find((item) => item.id === trackId);
    if (!track) return;
    state.currentTrackId = track.id;
    state.activeLyricIndex = -1;
    const album = albumFor(track);
    elements.trackTitle.textContent = track.title || "Untitled";
    elements.artist.textContent = track.artist || "Unknown artist";
    elements.album.textContent = album?.title || track.album || "Single";
    elements.cover.src = mediaUrl(track.cover || album?.cover || "assets/covers/placeholder.svg");
    elements.cover.alt = `${track.title || "Current track"} cover`;
    audio.src = mediaUrl(track.audio);
    renderTrackList();
    loadLyrics(track);
    if (autoplay) {
      try {
        await audio.play();
      } catch (error) {
        console.warn("Playback requires a user gesture or Wallpaper Engine audio permission", error);
      }
    }
  }

  function moveTrack(delta) {
    const tracks = catalog.tracks || [];
    if (!tracks.length) return;
    const currentIndex = Math.max(0, tracks.findIndex((track) => track.id === state.currentTrackId));
    const nextIndex = (currentIndex + delta + tracks.length) % tracks.length;
    loadTrack(tracks[nextIndex].id, true);
  }

  function syncLyrics() {
    if (!state.lyrics.length) return;
    let nextIndex = -1;
    for (let index = 0; index < state.lyrics.length; index += 1) {
      if (state.lyrics[index].time <= audio.currentTime + 0.04) nextIndex = index;
      else break;
    }
    if (nextIndex === state.activeLyricIndex) return;
    state.activeLyricIndex = nextIndex;
    const lines = elements.lyrics.querySelectorAll(".lyric-line");
    lines.forEach((line, index) => line.classList.toggle("active", index === nextIndex));
    lines[nextIndex]?.scrollIntoView({ block: "center", behavior: "smooth" });
  }

  function renderMaterials() {
    const materials = catalog.materials || [];
    if (!materials.length) {
      elements.materialCredits.textContent = "No material entries yet. Add every source before publishing.";
      return;
    }
    elements.materialCredits.replaceChildren(...materials.map((material) => {
      const card = document.createElement("article");
      card.className = "material-card";
      const title = document.createElement("strong");
      title.textContent = material.name || material.id || "Material";
      const details = document.createElement("p");
      details.textContent = [
        material.creator && `Creator / rights holder: ${material.creator}`,
        material.source && `Source: ${material.source}`,
        material.license && `License / permission: ${material.license}`,
        material.modifications && `Modifications: ${material.modifications}`
      ].filter(Boolean).join(" · ");
      card.append(title, details);
      return card;
    }));
  }

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("musicWallpaperTheme", theme);
    elements.theme.textContent = theme === "light" ? "Dark theme" : "Light theme";
  }

  elements.play.addEventListener("click", async () => {
    if (!audio.src) {
      const first = (catalog.tracks || [])[0];
      if (first) await loadTrack(first.id, true);
      return;
    }
    if (audio.paused) await audio.play();
    else audio.pause();
  });
  elements.previous.addEventListener("click", () => moveTrack(-1));
  elements.next.addEventListener("click", () => moveTrack(1));
  elements.progress.addEventListener("input", () => {
    if (Number.isFinite(audio.duration)) audio.currentTime = (Number(elements.progress.value) / 1000) * audio.duration;
  });
  elements.volume.addEventListener("input", () => { audio.volume = Number(elements.volume.value); });
  elements.theme.addEventListener("click", () => applyTheme(document.documentElement.dataset.theme === "light" ? "dark" : "light"));
  elements.credits.addEventListener("click", () => elements.creditsDialog.showModal());

  audio.addEventListener("play", () => { elements.play.textContent = "Pause"; elements.play.ariaLabel = "Pause"; });
  audio.addEventListener("pause", () => { elements.play.textContent = "Play"; elements.play.ariaLabel = "Play"; });
  audio.addEventListener("ended", () => moveTrack(1));
  audio.addEventListener("loadedmetadata", () => { elements.duration.textContent = formatTime(audio.duration); });
  audio.addEventListener("timeupdate", () => {
    elements.currentTime.textContent = formatTime(audio.currentTime);
    elements.duration.textContent = formatTime(audio.duration);
    elements.progress.value = Number.isFinite(audio.duration) && audio.duration > 0 ? String(Math.round((audio.currentTime / audio.duration) * 1000)) : "0";
    syncLyrics();
  });

  window.wallpaperPropertyListener = {
    applyUserProperties(properties) {
      if (properties.volume) {
        const value = Math.max(0, Math.min(1, Number(properties.volume.value) / 100));
        audio.volume = value;
        elements.volume.value = String(value);
      }
    }
  };

  elements.title.textContent = catalog.title || "Music Wallpaper";
  audio.volume = Number(elements.volume.value);
  applyTheme(localStorage.getItem("musicWallpaperTheme") === "light" ? "light" : "dark");
  renderAlbumFilters();
  renderTrackList();
  renderMaterials();
  const firstTrack = (catalog.tracks || [])[0];
  if (firstTrack) loadTrack(firstTrack.id, false);
})();
