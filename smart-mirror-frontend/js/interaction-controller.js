/* ==========================================
   Interaction Controller — Shared Singleton
   Manages expand/collapse overlay and gesture utilities.
   Must be loaded after module.js, before loader.js.
   ========================================== */

(function () {
  "use strict";

  const Controller = {
    _registry: new Map(),
    _expandedModuleId: null,
    _overlay: null,
    _cardContainer: null,

    // ==================== Registration ====================

    /**
     * Register a module as expandable.
     * @param {object} module — MM module instance (must have .identifier and .name)
     * @param {object} options
     * @param {Function} options.getExpandedContent — returns an HTMLElement
     * @param {Function} [options.onCleanup] — called when the overlay is dismissed
     */
    register: function (module, options) {
      if (!module || !module.identifier) {
        Log.error("[InteractionController] register: invalid module");
        return;
      }
      if (typeof options.getExpandedContent !== "function") {
        Log.error("[InteractionController] register: getExpandedContent function is required");
        return;
      }
      this._registry.set(module.identifier, {
        module: module,
        options: options
      });
      Log.log("[InteractionController] registered: " + module.name + " (" + module.identifier + ")");
    },

    /** Unregister a module (e.g. on suspend). */
    unregister: function (module) {
      if (this._expandedModuleId === module.identifier) {
        this.dismiss();
      }
      this._registry.delete(module.identifier);
    },

    // ==================== Expand / Dismiss ====================

    /**
     * Expand a registered module into the centered overlay.
     * @param {object} module — the MM module instance to expand
     */
    expand: function (module) {
      // Prevent double-expand of the same module
      if (this._expandedModuleId === module.identifier) return;

      // If another module is open, dismiss it first (no cleanup callback)
      if (this._expandedModuleId !== null) {
        this._doDismiss(false);
      }

      var entry = this._registry.get(module.identifier);
      if (!entry) {
        Log.warn("[InteractionController] expand: module not registered — " + module.name);
        return;
      }

      this._expandedModuleId = module.identifier;

      // 1. Build overlay DOM
      this._createOverlayDOM();

      // 2. Populate the card with the module's expanded content
      var content = entry.options.getExpandedContent();
      if (content) {
        this._cardContainer.appendChild(content);
      }

      // 3. Attach to body
      document.body.appendChild(this._overlay);

      // 4. Mark the source module wrapper as "expanded" so it stays sharp
      var moduleWrapper = document.getElementById(module.identifier);
      if (moduleWrapper) {
        moduleWrapper.classList.add("ic-expanded-module");
      }

      // 5. Blur everything else
      document.body.classList.add("ic-blur-active");

      // 6. Animate in (next frame so CSS transitions fire)
      var self = this;
      requestAnimationFrame(function () {
        self._overlay.classList.add("ic-overlay--visible");
        self._cardContainer.classList.add("ic-card--visible");
      });

      // 7. Keyboard dismiss
      this._escapeHandler = function (e) {
        if (e.key === "Escape") {
          Controller.dismiss();
        }
      };
      document.addEventListener("keydown", this._escapeHandler);

      // 8. Notify via DOM event (so MM or other scripts can react)
      this._broadcastEvent("mm-module-expanded", { moduleId: module.identifier });
    },

    /** Dismiss the currently expanded overlay. */
    dismiss: function () {
      this._doDismiss(true);
    },

    // ==================== Soft Language Switch ====================

    /**
     * Change the global language without a hard page reload.
     * Updates config, localStorage, and forces all MM modules to re-render.
     * @param {string} newLang — e.g. "Zh-cn" or "En-us"
     */
    changeLanguage: function (newLang) {
      var oldLang = config.language;
      if (oldLang === newLang) return;

      // 1. Update global config
      config.language = newLang;
      config.locale = newLang;

      // 2. Persist
      try {
        localStorage.setItem("mm_language", newLang);
      } catch (e) { /* quota exceeded — not critical */ }

      // 3. Reload core translations if the Translator is available
      if (typeof Translator !== "undefined" && Translator.reloadCoreTranslations) {
        var coreLang = newLang === "Zh-cn" ? "zh-cn" : "en";
        Translator.reloadCoreTranslations(coreLang);
      }

      // 4. Broadcast DOM event
      this._broadcastEvent("mm-language-changed", {
        language: newLang,
        oldLanguage: oldLang
      });

      // 5. Force all MM modules to re-render
      if (typeof MM !== "undefined" && MM.getModules) {
        MM.getModules().enumerate(function (mod) {
          if (mod.name !== "MMM-LanguageSwitch") {
            mod.updateDom(0);
          }
        });
      }

      Log.log("[InteractionController] language changed: " + oldLang + " → " + newLang);
    },

    // ==================== Gesture Utilities ====================

    /**
     * Attach tap vs long-press listeners to an element.
     * Works with both mouse and touch events.
     *
     * @param {HTMLElement} el
     * @param {object} handlers
     * @param {Function} handlers.onTap        — called on short press/release
     * @param {Function} handlers.onLongPress  — called after holding ≥ thresholdMs
     * @param {number}   [handlers.thresholdMs=500]
     */
    addTapOrHoldListeners: function (el, handlers) {
      var thresholdMs = handlers.thresholdMs || 500;
      var timer = null;
      var isLongPress = false;
      var startX = 0, startY = 0;

      var onStart = function (e) {
        isLongPress = false;
        var point = (e.touches && e.touches[0]) || e;
        startX = point.clientX;
        startY = point.clientY;
        timer = setTimeout(function () {
          isLongPress = true;
          if (handlers.onLongPress) handlers.onLongPress(e);
        }, thresholdMs);
      };

      var onEnd = function (e) {
        if (timer) { clearTimeout(timer); timer = null; }
        if (!isLongPress && handlers.onTap) handlers.onTap(e);
        isLongPress = false;
      };

      var onMove = function (e) {
        if (!timer) return;
        var point = (e.touches && e.touches[0]) || e;
        if (Math.abs(point.clientX - startX) > 10 || Math.abs(point.clientY - startY) > 10) {
          clearTimeout(timer);
          timer = null;
        }
      };

      var onCancel = function () {
        if (timer) { clearTimeout(timer); timer = null; }
        isLongPress = false;
      };

      // Mouse
      el.addEventListener("mousedown", onStart);
      el.addEventListener("mouseup", onEnd);
      el.addEventListener("mouseleave", onCancel);
      // Touch
      el.addEventListener("touchstart", onStart, { passive: true });
      el.addEventListener("touchend", onEnd);
      el.addEventListener("touchmove", onMove, { passive: true });
      el.addEventListener("touchcancel", onCancel);
    },

    /**
     * Attach swipe-left / swipe-right listeners to an element (touch only).
     *
     * @param {HTMLElement} el
     * @param {object} handlers
     * @param {Function} handlers.onSwipeLeft
     * @param {Function} handlers.onSwipeRight
     * @param {number}   [handlers.threshold=50] — minimum horizontal px delta
     */
    addSwipeListeners: function (el, handlers) {
      var threshold = handlers.threshold || 50;
      var startX = 0, startY = 0;

      el.addEventListener("touchstart", function (e) {
        var touch = e.touches[0];
        startX = touch.clientX;
        startY = touch.clientY;
      }, { passive: true });

      el.addEventListener("touchmove", function (e) {
        if (!startX) return;
        var touch = e.touches[0];
        var dx = touch.clientX - startX;
        var dy = touch.clientY - startY;

        // Only treat as swipe when horizontal movement dominates
        if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > threshold) {
          if (dx > 0 && handlers.onSwipeRight) {
            handlers.onSwipeRight(e);
          } else if (dx < 0 && handlers.onSwipeLeft) {
            handlers.onSwipeLeft(e);
          }
          // Reset so the swipe fires once per gesture
          startX = 0;
          startY = 0;
        }
      }, { passive: true });

      el.addEventListener("touchend", function () {
        startX = 0;
        startY = 0;
      });
    },

    // ==================== Internal Helpers ====================

    /** Build overlay + card + close button DOM (once per expand). */
    _createOverlayDOM: function () {
      var self = this;

      // Backdrop
      this._overlay = document.createElement("div");
      this._overlay.className = "ic-overlay";
      this._overlay.setAttribute("aria-label", "Interaction overlay");
      this._overlay.setAttribute("role", "dialog");
      this._overlay.setAttribute("aria-modal", "true");

      // Card container
      this._cardContainer = document.createElement("div");
      this._cardContainer.className = "ic-card";

      // Universal close button
      var closeBtn = document.createElement("button");
      closeBtn.className = "ic-close-btn";
      closeBtn.innerHTML = "&times;";
      closeBtn.setAttribute("aria-label", "Close");
      closeBtn.addEventListener("click", function (e) {
        e.stopPropagation();
        self.dismiss();
      });
      this._cardContainer.appendChild(closeBtn);

      this._overlay.appendChild(this._cardContainer);

      // Click backdrop → dismiss
      this._overlay.addEventListener("click", function (e) {
        if (e.target === self._overlay) {
          self.dismiss();
        }
      });

      // Stop card clicks from bubbling to backdrop
      this._cardContainer.addEventListener("click", function (e) {
        e.stopPropagation();
      });
    },

    /**
     * Internal dismiss logic.
     * @param {boolean} triggerCleanup — whether to call the registered onCleanup callback
     */
    _doDismiss: function (triggerCleanup) {
      if (!this._expandedModuleId) return;
      var moduleId = this._expandedModuleId;

      // Cleanup callback
      if (triggerCleanup) {
        var entry = this._registry.get(moduleId);
        if (entry && entry.options.onCleanup) {
          try { entry.options.onCleanup(); } catch (e) { Log.error("[InteractionController] cleanup error: " + e); }
        }
      }

      // Remove blur
      document.body.classList.remove("ic-blur-active");

      // Remove expanded marker
      var moduleWrapper = document.getElementById(moduleId);
      if (moduleWrapper) {
        moduleWrapper.classList.remove("ic-expanded-module");
      }

      // Remove keyboard handler
      if (this._escapeHandler) {
        document.removeEventListener("keydown", this._escapeHandler);
        this._escapeHandler = null;
      }

      // Animate out, then remove from DOM
      var overlay = this._overlay;
      if (overlay) {
        overlay.classList.remove("ic-overlay--visible");
        if (this._cardContainer) {
          this._cardContainer.classList.remove("ic-card--visible");
        }

        var onTransitionEnd = function () {
          if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
          overlay.removeEventListener("transitionend", onTransitionEnd);
        };
        overlay.addEventListener("transitionend", onTransitionEnd);

        // Fallback in case transitionend never fires
        setTimeout(function () {
          if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
        }, 500);
      }

      this._overlay = null;
      this._cardContainer = null;
      this._expandedModuleId = null;

      this._broadcastEvent("mm-module-collapsed", { moduleId: moduleId });
    },

    /** Dispatch a custom DOM event for loose coupling. */
    _broadcastEvent: function (name, detail) {
      var event = new CustomEvent(name, { bubbles: true, detail: detail });
      document.dispatchEvent(event);
    }
  };

  // Expose globally
  window.InteractionController = Controller;
  Log.log("[InteractionController] initialized");
})();
