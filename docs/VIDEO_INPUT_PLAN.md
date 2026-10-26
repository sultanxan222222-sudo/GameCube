# Display, Controllers, and Graphics Plan

This file records the requested PS4 GameCube-emulator features. It is a design/implementation checklist, not a claim that these features already work.

## 1. Display sizing and aspect ratio

- Provide output-resolution options supported by the PS4 video path: 720p and 1080p first; expose 1440p/2160p only if the target runtime and display mode actually support them.
- Add scaling modes:
  - **Keep aspect ratio** (recommended default): fit the game's original aspect ratio inside the output, with letterboxing/pillarboxing where necessary.
  - **Fill screen / crop**: fill the display while preserving proportions; crop excess image.
  - **Stretch to screen**: fill the whole display, allowing distortion only when explicitly selected.
  - **Integer scale** where practical, for crisp pixel-art titles.
- Never independently stretch width and height in the default mode. Compute a single scale factor: min(output_width / game_width, output_height / game_height), then center the result.
- Persist settings in the emulator configuration.

## 2. DualShock 4 and two-player support

- Use the PS4 controller API/input layer available in the selected homebrew SDK.
- Map each connected controller independently to GameCube controller ports 1 and 2.
- Support D-pad, left/right sticks, face buttons, shoulders/triggers, Start/Options, and sensible analog dead zones.
- Show connection status and allow controller-to-port assignment/remapping.
- If only one controller is connected, player 1 remains usable; hot-plugging player 2 should not crash or reset the session.
- Test simultaneous input and two-player games; do not claim multiplayer support until tested on hardware.

## 3. Graphics improvements, prioritized for PS4 Pro

1. Internal render scale / resolution multiplier (start at 1x, then 2x when performance allows).
2. Anisotropic texture filtering where supported.
3. Safe texture filtering and optional anti-aliasing, with a performance toggle.
4. Correct widescreen handling only where the game/render path supports it; avoid stretching as a substitute for a widescreen fix.
5. Optional post-processing only after the basic renderer is stable.
6. Frame pacing and shader-cache management to reduce stutter.

## 4. Performance policy

- Default to stable frame pacing and native game timing rather than forcing enhancements.
- Offer presets: **Compatibility**, **Balanced**, and **Enhanced**.
- Enable costly options individually; avoid stacking high render scale, anti-aliasing, and post-processing by default.
- Keep the renderer backend abstracted so the actual PS4-supported graphics API determines which features can be enabled.

## 5. Acceptance tests

- 4:3 and 16:9 games retain correct proportions in Keep aspect ratio mode.
- Fill screen crops rather than distorts; Stretch mode is explicitly labeled.
- Settings survive restart.
- One and two DualShock 4 controllers work independently across repeated launches and hot-plugging.
- Compare frame pacing and speed with enhancements off/on; disable any option that causes persistent slowdown or rendering errors.

## Current status

Specification only. Implementation requires a working PS4 homebrew build environment, an actual emulator port, and runtime/hardware testing. No PKG or functioning emulator build is produced by this document.
