# iina-builds

Custom [IINA](https://github.com/iina/iina) (macOS) builds with **custom dependencies compiled from
source**. IINA normally ships prebuilt dylibs, so a modified FFmpeg/mpv never reaches the app; this
repo rebuilds the `ffmpeg-iina` and `mpv-iina` Homebrew formulas from source — retargeting
`ffmpeg-iina` at our MMT/TLV FFmpeg fork branch and applying the `patches/mpv/` + `patches/iina/`
source patches — then runs IINA's normal `xcodebuild`. GitHub Actions does it all and caches the
dependency build.

## What's customized

- **FFmpeg — MMT/TLV demuxer** so IINA opens Japanese ISDB-S3 / 4K·8K **`.mmts`** streams. Built
  from our fork branch [`saindriches/FFmpeg` @ `mmt-tlv`](https://github.com/saindriches/FFmpeg/tree/mmt-tlv)
  (based on [SuperFashi's PR #21037](https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/21037), plus parser
  hardening, seeking, HEVC extradata, and stream-metadata work). No in-repo ffmpeg patches — the CI
  retargets the `ffmpeg-iina` formula's source at the fork commit pinned in `manifest.env`.
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

## Changing a dependency

- **FFmpeg**: the MMT/TLV work lives in the fork branch, not here. Bump `FFMPEG_REF` in
  [`manifest.env`](manifest.env) and the workflow `env:` to a new `mmt-tlv` commit and push.
- **mpv / IINA**: drop a `-p1` diff into `patches/mpv/` or `patches/iina/` named
  `NNNN-description.patch` and push; it's applied to that source before it builds. See
  [`patches/README.md`](patches/README.md).
