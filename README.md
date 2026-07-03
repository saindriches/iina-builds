# iina-builds

Custom [IINA](https://github.com/iina/iina) (macOS) builds with **patched dependencies compiled
from source**. IINA normally ships prebuilt dylibs, so a patched FFmpeg/mpv never reaches the app;
this repo rebuilds the `ffmpeg-iina` and `mpv-iina` Homebrew formulas from source with the patches
under [`patches/`](patches/), then runs IINA's normal `xcodebuild`. GitHub Actions does it all and
caches the dependency build.

## What's patched

- **FFmpeg — MMT/TLV demuxer** so IINA opens Japanese ISDB-S3 / 4K·8K **`.mmts`** streams. Base
  demuxer from [SuperFashi's PR #21037](https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/21037) (`0001`),
  plus our fixes: parser hardening (`0002`), seeking (`0003`), HEVC extradata (`0004`), stream
  metadata (`0005`).
- **mpv — ICC BT.1886 fix** (`patches/mpv/0001`) so SDR video isn't gray with *Load ICC profile* on
  (backport of mpv#17439). Clear mpv's ICC LUT cache once after installing — see
  [`patches/README.md`](patches/README.md).

`IINA_REF` and dependency versions are pinned in [`manifest.env`](manifest.env).

## Build & use

Run **Actions → build → Run workflow**, then download the `IINA-patched` artifact:

```sh
tar xf IINA.tar.xz
xattr -dr com.apple.quarantine IINA.app   # clear Gatekeeper
open IINA.app
```

Ad-hoc signed — fine for personal use, not notarized.

## Adding a patch

Drop a `-p1` diff into `patches/<ffmpeg|mpv|iina>/` named `NNNN-description.patch` and push; it's
applied to that dependency's source before it builds. See [`patches/README.md`](patches/README.md).
