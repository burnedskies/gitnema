## Gitnema  

Small hacky project designed to enable video playback using Git sideband channels.

## Security Advisory  

The default viewing experience on Windows may be suboptimal because of a Git security advisory ([GHSA‑7jjc‑gg6m‑3329](https://github.com/git/git/security/advisories/GHSA-7jjc-gg6m-3329)).  
Patch commit: [git‑for‑windows commit 962ce4c](https://github.com/git-for-windows/git-snapshots/commit/962ce4c)


The patch attempts to masks control characters. You can disable/enable this functionality via the `sideband.allowControlCharacters` option
in your git config. This option can be toggled by the script [`scripts/sideband-aac-toggle.bat`](scripts/sideband-aac-toggle.bat)

**No changes should be needed** if you're currently using Git version **2.52.0** or older on **Linux**.

## Requirements  
 - **FFmpeg** - Must be installed and added to your system `PATH` to use `scripts/frame-extractor.py`.

## How to Use

1. **Run the main script**

   ```bash
   uv run main.py --host localhost --port 8000 films/{film}.gitnema
   ```

2. **Clone the repository**

   ```bash
   git clone http://localhost:8000/anything/anything
   ```

## Demo  

![Gitema demo](assets/demo.gif)