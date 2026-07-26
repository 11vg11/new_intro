<div align="center">

<h1>Hi, I'm Avi 👋</h1>
<p>I’m a developer who enjoys building useful tools, writing clean code, and turning ideas into real products.</p>
<p>My interests span Python, web development, automation, and creating thoughtful developer experiences.</p>

<br>

<img src="./output/contrib-heatmap.svg" width="860" alt="Contribution heatmap" />

<br><br>

<img src="./output/avi-ascii.svg" width="360" alt="ASCII portrait" />
<img src="./output/info-card.svg" width="520" alt="Info card" />

</div>

---

## About Me

I’m someone who likes solving practical problems with code and learning by building. Whether it’s a small script, a polished web experience, or a full workflow automation, I enjoy making things that are useful and maintainable.

### What I’m into
- Building tools that save time
- Writing readable, reliable software
- Exploring new technologies and improving my craft
- Turning ideas into simple, effective solutions

### Current focus
- Python and automation
- Web development and developer tooling
- Clean architecture and thoughtful UX

---

## Skills

- Python
- JavaScript
- Git and GitHub workflows
- Automation and scripting
- SVG and visual content generation
- Problem solving and rapid prototyping

---

## Projects

This profile page is generated from a small personal workflow that combines:
- a contribution heatmap
- an ASCII portrait
- a compact info card

It’s a fun way to make a GitHub profile feel more personal and expressive.

---

## Connect

- GitHub: [11vg11](https://github.com/11vg11)
- Email: hi@avivashishta.com

---

## Featured Profile Art

This repository generates three visual pieces for the profile page:

- Contribution heatmap — refreshed automatically
- ASCII portrait — generated from a photo
- Info card — a compact self-introduction panel


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
