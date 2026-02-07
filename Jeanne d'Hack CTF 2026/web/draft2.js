(function(){
  // Small preload module exposing a global `Preload` namespace
  const Preload = {
    audioMap: {},
    resourcesLoading: {
      sounds: new Set(),
      font: false,
      image: false
    },
    hintAudio: null,
    _readyListeners: [],

    onReady(fn) {
      if (typeof fn === 'function') this._readyListeners.push(fn);
    },

    _notifyIfReady() {
      if (this.resourcesLoading.font && this.resourcesLoading.image && this.resourcesLoading.sounds.size === 0) {
        this._readyListeners.forEach(f => { try { f(); } catch(e){ console.error(e); } });
      }
    },

    loadAudio(path) {
      return new Promise((resolve, reject) => {
        const a = new Audio(path);
        a.preload = 'auto';
        function onCan() { cleanup(); resolve(a); }
        function onErr(e) { cleanup(); reject(e); }
        function cleanup() { a.removeEventListener('canplaythrough', onCan); a.removeEventListener('error', onErr); }
        a.addEventListener('canplaythrough', onCan);
        a.addEventListener('error', onErr);
        try { a.load(); } catch(e) { cleanup(); reject(e); }
      });
    },

    preloadFonts() {
      try {
        const zeldaFontLoader = new FontFace('Zelda', 'url(/static/zelda.ttf)');
        const zeldaLightFontLoader = new FontFace('Zelda Light', 'url(/static/zelda_light.ttf)');
        Promise.all([zeldaFontLoader.load(), zeldaLightFontLoader.load()]).then(([zeldaFont, zeldaLightFont]) => {
          document.fonts.add(zeldaFont);
          document.fonts.add(zeldaLightFont);
          this.resourcesLoading.font = true;
          this._notifyIfReady();
        }).catch(err => {
          console.warn('Could not load fonts:', err);
          this.resourcesLoading.font = true; // continue anyway
          this._notifyIfReady();
        });
      } catch (e) {
        console.warn('Font preload failed', e);
        this.resourcesLoading.font = true;
        this._notifyIfReady();
      }
    },

    preloadHint() {
      this.loadAudio('/static/sounds/hint.wav').then(a => { this.hintAudio = a; }).catch(err => {
        console.warn('Could not load hint audio:', err);
      });
    },

    preloadImage() {
      const img = new Image();
      img.src = '/static/ocarina.png';
      img.onload = () => { this.resourcesLoading.image = true; this._notifyIfReady(); };
      img.onerror = (err) => { console.warn('Could not load image:', err); this.resourcesLoading.image = true; this._notifyIfReady(); };
    },

    preloadNotes(notes) {
      // Initialize set
      this.resourcesLoading.sounds = new Set(notes);
      for (const n of notes) {
        this.loadAudio(`/static/sounds/Ocarina_${n}.wav`).then(a => {
          this.audioMap[n] = a;
          this.resourcesLoading.sounds.delete(n);
          this._notifyIfReady();
        }).catch(err => {
          console.warn('Could not load sound for note:', n, err);
          this.resourcesLoading.sounds.delete(n);
          this._notifyIfReady();
        });
      }
    },

    preloadAll() {
      this.preloadFonts();
      this.preloadHint();
      this.preloadImage();
      // notes must be started by caller via preloadNotes(notes)
    }
  };

  // expose globally
  window.Preload = Preload;

  // Auto-start fonts/hint/image preloads (notes are started by game.js)
  Preload.preloadAll();
})();
