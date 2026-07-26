<div align="center">

<!-- ═══════════════════════════════════════════════════════════════════════════
     CONTRIBUTION HEATMAP
     Re-generated daily by GitHub Actions (.github/workflows/update-profile-art.yml)
     ═══════════════════════════════════════════════════════════════════════════ -->

<h3><code>avi@github ~ $ ./contributions.sh</code></h3>

<img src="./contrib-heatmap.svg" width="860" alt="Contribution heatmap" />

<br><br>

<!-- ═══════════════════════════════════════════════════════════════════════════
     ASCII PORTRAIT  +  NEOFETCH INFO CARD
     Static — regenerate with make_ascii_svg.py / make_info_card.py
     when your photo or details change.
     ═══════════════════════════════════════════════════════════════════════════ -->

<h3><code>avi@github ~ $ whoami</code></h3>

<div align="center">
  <p><strong>Live profile visuals generated from this repository:</strong></p>
  <img src="./avi-ascii.svg" width="360" alt="ASCII portrait" />
  <p><em>ASCII portrait — regenerate with <code>python scripts/make_ascii_svg.py</code></em></p>

  <img src="./info-card.svg" width="520" alt="Neofetch info card" />
  <p><em>Info card — regenerate with <code>python scripts/make_info_card.py</code></em></p>
</div>

</div>

---

## 🎨 GitHub Profile Art

This repository generates three SVG assets for a GitHub profile README:

| Asset | Description | Refresh |
|---|---|---|
| `contrib-heatmap.svg` | 53-week animated contribution heatmap with stats footer | ⏰ Daily (GitHub Actions) |
| `avi-ascii.svg` | Self-typing ASCII portrait generated from your photo | 🔧 Manual (when photo changes) |
| `info-card.svg` | Neofetch-style animated info card | 🔧 Manual (when details change) |

---

## 🗂️ Project Structure

```
new_intro/
├── .github/
│   └── workflows/
│       └── update-profile-art.yml   # Daily automation workflow
├── scripts/
│   ├── fetch_contributions.py       # Scrapes GitHub contribution calendar → JSON
│   ├── render_heatmap_svg.py        # Renders contrib-heatmap.svg from JSON
│   ├── make_ascii_svg.py            # Converts prepped photo → self-typing ASCII SVG
│   ├── make_info_card.py            # Generates the neofetch-style info card SVG
│   ├── prep_photo.py                # Removes background & enhances photo for ASCII art
│   └── requirements.txt             # Python dependencies
├── data/
│   └── contributions.json           # Cached contribution data (auto-updated daily)
├── output/
│   ├── contrib-heatmap.svg         # 🤖 Auto-generated — do not edit manually
│   ├── avi-ascii.svg               # 🔧 Manually regenerated when photo changes
│   └── info-card.svg               # 🔧 Manually regenerated when details change
├── photos/                         # Portrait images used by the ASCII workflow
└── README.md                        # This file — the profile page itself
```

---

## ⚙️ Setup

### 1. Fork or rename the repository

Create a GitHub repository named exactly like your GitHub username, such as `yourname/yourname`, so GitHub uses it as your profile README.

### 2. Configure the workflow

The daily workflow reads your username from the GitHub context automatically:

```yaml
env:
  GITHUB_USER: ${{ github.repository_owner }}
```

No secrets or tokens needed — contribution data is scraped from the public HTML calendar.

### 3. Customize the info card

Edit the `ROWS` list in `scripts/make_info_card.py`:

```python
HANDLE = "your-github-username"

ROWS = [
    (ACCENT, "Now",      WHITE,  "What you're building"),
    (ACCENT, "Stack",    GREEN,  "Your · Tech · Stack"),
    (ACCENT, "Contact",  ACCENT, "yoursite.com · hi@you.com"),
    # ... add/remove rows as needed
]
```

Then regenerate:

```bash
python scripts/make_info_card.py
```

### 4. Generate the ASCII portrait (optional)

Install the full image dependencies once:

```bash
pip install pillow numpy opencv-python rembg
```

**Step 2** — Prepare your photo (removes background, boosts contrast):

```bash
python scripts/prep_photo.py your-photo.jpg
# Writes: source-prepped.png
```

**Step 3** — Render the animated ASCII SVG:

```bash
python scripts/make_ascii_svg.py
# Writes: avi-ascii.svg
```

> **Tip:** Add `STATIC=1` to skip animation for a quick local preview:
> ```bash
> STATIC=1 python scripts/make_ascii_svg.py
> ```

### 5. Push your changes

```bash
git add contrib-heatmap.svg avi-ascii.svg info-card.svg README.md
git commit -m "chore: update profile art"
git push
```

The daily workflow will keep the heatmap fresh automatically.

---

## 🔄 How the Daily Automation Works

```
GitHub Actions (06:17 UTC daily)
        │
        ▼
fetch_contributions.py
  └─ Scrapes github.com/users/<you>/contributions (no token needed)
  └─ Parses <td data-date="..."> cells
  └─ Computes: total, current streak, longest streak, best day, monthly totals
  └─ Writes: data/contributions.json
        │
        ▼
render_heatmap_svg.py
  └─ Reads contributions.json
  └─ Builds 53-week × 7-day grid aligned to GitHub's Sunday-start convention
  └─ Applies 6-level green palette (level 0 → dim, level 5 → neon #69f0a0)
  └─ Adds CSS column-by-column diagonal reveal animation
  └─ Adds stats footer: total, streak, best day
  └─ Writes: contrib-heatmap.svg
        │
        ▼
git-auto-commit-action
  └─ Commits with "[skip ci]" to avoid re-triggering the workflow
  └─ Pushes back to main
```

---

## 🐍 Running Scripts Locally

### Fastest path: run everything with one command

```bash
make run
```

This runs the contribution scraper, renders the heatmap, generates the info card, and builds the ASCII portrait from a photo stored in the photos/ folder.

Useful helpers:

```bash
make photo    # regenerate the portrait pipeline only
make clean    # remove generated assets and cached prep state
```

You can also use the underlying script directly:

```bash
python3 scripts/run_profile.py
```

Place a portrait image in the photos/ directory, for example:

```bash
photos/my-photo.jpg
```

Then run:

```bash
python3 scripts/run_profile.py
```

You can also point at a specific image:

```bash
python3 scripts/run_profile.py --photo /path/to/your-photo.jpg
```

### Install runtime dependencies (for the heatmap only)

```bash
pip install requests beautifulsoup4
```

### Install full dependencies (for ASCII portrait generation)

```bash
pip install -r scripts/requirements.txt
```

### Run each script manually

```bash
# 1. Fetch fresh contribution data
python scripts/fetch_contributions.py

# 2. Render the heatmap SVG
python scripts/render_heatmap_svg.py

# 3. (Optional) Prep a photo for ASCII art
python scripts/prep_photo.py your-photo.jpg

# 4. (Optional) Render ASCII portrait SVG
python scripts/make_ascii_svg.py

# 5. (Optional) Regenerate the info card
python scripts/make_info_card.py
```

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `GITHUB_USER` | `avivashishta` | GitHub username for contribution scraping |
| `STATIC` | _(unset)_ | Set to `1` to skip SMIL/CSS animations (useful for local preview) |

---

## 🎨 Customising the Heatmap Colours

Edit the `PALETTE` list in `scripts/render_heatmap_svg.py`:

```python
PALETTE = [
    "#161b22",   # 0 – no contribution
    "#0e4429",   # 1 – very low
    "#006d32",   # 2 – low
    "#26a641",   # 3 – medium
    "#39d353",   # 4 – high
    "#69f0a0",   # 5 – maximum (neon)
]
```

---

## 📦 Dependencies

| Package | Used by | Purpose |
|---|---|---|
| `requests` | `fetch_contributions.py` | HTTP fetching |
| `beautifulsoup4` | `fetch_contributions.py` | HTML parsing |
| `pillow` | `make_ascii_svg.py`, `prep_photo.py` | Image loading & saving |
| `numpy` | `make_ascii_svg.py`, `prep_photo.py` | Pixel array manipulation |
| `opencv-python` | `prep_photo.py` | CLAHE contrast enhancement |
| `rembg` | `prep_photo.py` | AI background removal |

> The daily GitHub Actions workflow only installs `requests` and `beautifulsoup4` — keeping CI fast and lightweight.

---

## 📄 License

MIT — feel free to fork, adapt, and use for your own GitHub profile.
