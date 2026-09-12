# Video Generator — poster

Poster for the Video Generator site (`SA-Ark/ark-videogen-showcase`,
live at ark-videogen.chakrakali.com).

| File | What it is |
|---|---|
| `Main.dc.html` | The poster. A3 at 96 px/inch (1123×1587). |
| `canvas.json` | Canvas layout. |

## Brand

Values are lifted from `ark-videogen-showcase/public/theme.css`, not invented:

| Token | Value |
|---|---|
| `--bg` / `--surface` / `--surface-2` | `#0a0a0f` / `#14141f` / `#191926` |
| `--fg` / `--muted` / `--muted-2` | `#ececf4` / `#a2a2b6` / `#8f8fa6` |
| `--border` / `--border-2` | `#232338` / `#33334d` |
| brand arc (135deg) | `#f472b6` → `#a78bfa` → `#818cf8` |
| `--p-accent` | `#c4b5fd` |
| `--radius` / button / `.btn-lg` | 14px / 11px / 12px |

Type is Inter — h1 at weight 800, `letter-spacing: -.022em`, `line-height: 1.12`,
matching theme.css. The gradient-clipped hero keyword follows theme.css's
`.grad-text` rule of one keyword only, never a whole heading. The three fixed
radial gradients behind the page reproduce its `body::before` wash.

## Copy

Headline, lede, the three steps, the format list and the closing line are the
site's own words. `0:30 · 1080p · real voiceover` is the spec the homepage
states.

The example prompt ("A 30-second welcome video for our dental practice…") and
the caption inside the film frame are **sample text written for the poster** —
not a real customer or a real generated video.
