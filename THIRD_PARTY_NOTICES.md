# Third-party notices

AudiobookForge itself is licensed under the MIT License (see `LICENSE`).
Release builds also ship the third-party components listed below, each under its own license.
Python packages bundled by PyInstaller keep their own licenses as published on PyPI.

## FFmpeg (bundled `ffmpeg\ffmpeg.exe`, since 1.0.6)

- Component: `ffmpeg.exe` command-line program (no other FFmpeg files are shipped)
- Version: `n9.0.2-39-g7adfbe40dc-20261031` (FFmpeg 9.0 release branch)
- License: **GNU Lesser General Public License v3** (LGPL build: configured with `--enable-version3`,
  without `--enable-gpl` and without `--enable-nonfree`). The full license text is shipped as
  `ffmpeg\LICENSE.txt` next to `ffmpeg.exe`.
- Binary build: FFmpeg-Builds (formerly BtbN/FFmpeg-Builds), `win64-lgpl` static variant
  - Download: https://github.com/FFmpeg-Builds/FFmpeg-Builds/releases/download/autobuild-2026-10-31-12-59/ffmpeg-n9.0.2-39-g7adfbe40dc-win64-lgpl-9.0.zip
  - Archive SHA-256: `9d37c564e0d01c18cde184a079fa6ef04d7d2783ada41da81d04165cc8f1a650`
  - `ffmpeg.exe` SHA-256: `d03c858a130cae1382902925d9f46eb15d7de42e025d34cc29b7ddca6cfb4c62`
- Corresponding source code:
  - FFmpeg: https://github.com/FFmpeg/FFmpeg/tree/7adfbe40dcde598f93a6963d2f7b22cd75202ccc
    (also https://ffmpeg.org/download.html)
  - Build scripts and the exact versions of the statically linked libraries:
    https://github.com/FFmpeg-Builds/FFmpeg-Builds
  - The full configure line is printed by `ffmpeg\ffmpeg.exe -version`.
- `ffmpeg.exe` is an unmodified, separate program. AudiobookForge only runs it as an external
  process and does not link to FFmpeg libraries. You may replace it with your own build: put
  another `ffmpeg.exe` in the `ffmpeg` folder, or set `"ffmpeg_path"` in `config.json`.

FFmpeg is a trademark of Fabrice Bellard, originator of the FFmpeg project.

The build is fetched by `scripts/fetch_ffmpeg.ps1`, which verifies both SHA-256 values above
before anything is packaged. The binary is not stored in this git repository.
