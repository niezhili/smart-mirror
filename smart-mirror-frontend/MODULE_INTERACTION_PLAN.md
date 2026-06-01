# Module Interaction Plan

## Goal
Make multiple modules behave as a shared interactive layer instead of isolated widgets.

The first target modules are:
- Weather
- News
- Calendar (default calendar module)
- Language switch
- Quote
- MMM-CustomClock

When the user clicks one of these modules:
1. The clicked module expands.
2. The expanded module moves to the center of the screen.
3. Every other page element becomes blurred or visually de-emphasized.
4. The clicked module stays sharp and readable.
5. Clicking outside the expanded module closes the view and restores the normal layout.

Additional module-specific interactions:
- Language switch module: single click changes the current language.
- Language switch module: press and hold, or touch and hold, opens a language list so the user can choose a language.
- Quote module: swipe left or right with a finger to switch to the next or previous quote.
- MMM-CustomClock module: click to change the text color.


## Desired User Experience

### Default State
- Modules render in their normal positions.
- All modules are interactive but compact.
- No blur or modal overlay is active.

### Expanded State
- The clicked module becomes the focus of the page.
- It animates into a centered panel.
- A fullscreen overlay appears behind it.
- All non-focused modules are blurred or dimmed.
- The focused module remains fully clear.

### Exit State
- Clicking the overlay closes the expanded view.
- Pressing Escape closes the expanded view.
- The page returns to the original layout without losing module state.

## Interaction Rules

- Only one module can be expanded at a time.
- A module should not expand if it is already open.
- The expansion behavior should be reusable across modules.
- The blur effect should apply globally, not module by module.
- The centered panel should use the same interaction pattern for weather, news, and calendar so the UI feels consistent.

## Implementation Plan

### Phase 1: Shared interaction controller
- Create a shared controller or helper for expand/collapse state.
- Track the active module id.
- Add open and close events that other modules can reuse.

### Phase 2: Shared overlay and focus handling
- Render one fullscreen overlay.
- Move the active module into a centered container when expanded.
- Blur or dim all non-active module containers while the overlay is visible.
- Keep keyboard and click-to-dismiss behavior consistent.

### Phase 3: Module integration
- Update weather to use the shared controller instead of only local expansion logic.
- Add the same click behavior to news.
- Add the same click behavior to the default calendar module.
- Add language switch tap and hold interactions.
- Add quote swipe interactions.
- Add MMM-CustomClock color-change behavior.

- Make sure each module can supply its own expanded content without duplicating the overlay logic.

### Phase 4: Styling and motion
- Add transitions for scale, opacity, and position changes.
- Tune the blur strength so background modules remain recognizable but clearly inactive.
- Keep the centered panel readable on desktop and smaller screens.

### Phase 5: Validation
- Verify weather expands, centers, and closes correctly.
- Verify news uses the same behavior.
- Verify calendar uses the same behavior.
- Verify language switch changes language on tap and opens the language list on long press or long touch.
- Verify quote changes when swiping left or right.
- Verify MMM-CustomClock changes color when clicked.

- Verify only the active module stays sharp while the rest blur.
- Verify Escape and outside clicks restore the default layout.

## Acceptance Criteria

- Clicking weather opens a centered expanded view.
- Clicking news opens a centered expanded view.
- Clicking the default calendar module opens a centered expanded view.
- Clicking language switch changes language, and long press or long touch opens the language list.
- Swiping quote left or right changes the displayed quote.
- Clicking MMM-CustomClock changes its color.

- Non-active modules blur while one module is expanded.
- The page returns to normal after closing the expanded view.
- The behavior is consistent across modules and does not require separate one-off implementations.

## Open Questions

- Should the blur affect only modules, or also the background and headers?
- Should expansion open a modal-like layer or physically reflow the module into the center?
- Should expanded views share one common design, or allow each module to define its own layout?