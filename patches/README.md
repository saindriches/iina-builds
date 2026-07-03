# patches/

Every `*.patch` in a subdirectory is applied in filename order to that dependency's source with
`patch -p1 -F3` before it builds.

```
patches/
├── ffmpeg/   → FFmpeg source in the ffmpeg-iina formula
├── mpv/      → mpv source in the mpv-iina formula
└── iina/     → the IINA checkout, before xcodebuild
```

## FFmpeg — MMT/TLV demuxer

SuperFashi's base demuxer, then our self-contained fixes (core first; no later patch reworks an
earlier one):

- `0001-mmttlv-demuxer.patch` — the demuxer, verbatim from
  [SuperFashi's PR #21037](https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/21037). Additive (3 new files
  + registration); drops when #21037 merges.
- `0002-mmttlv-harden-parser.patch` — allocation / MFU-parsing hardening.
- `0003-mmttlv-seek-index.patch` — byte-offset index + hardened `read_timestamp` probe (reliable
  backward seek, fast forward seek); bounded duration scan; timestamp normalization.
- `0004-mmttlv-hevc-extradata.patch` — expose in-band VPS/SPS/PPS as extradata (survives seek/flush).
- `0005-mmttlv-metadata.patch` — audio-track titles, main-audio `DEFAULT`, present-section EIT,
  metadata-update events.

## mpv — ICC BT.1886 fix

- `mpv/0001-lcms-clamp-bt1886-black-point.patch` — backport of mpv#17439 (`47f81c8d`): clamp
  `src_black` with `MPMAX(0, …)` so a slightly-negative detected black point can't produce a NaN
  BT.1886 curve that grays all SDR on the ICC path IINA uses. The pinned `iina-release/1.5.0` mpv
  predates the fix.

  **Cache caveat:** mpv keys its ICC LUT cache on (profile + params), not the code version, so a
  machine that ran a pre-fix build keeps a poisoned LUT (e.g. `~/Library/Caches/io.mpv/`). Clear it
  **once** after installing the fixed build.

## iina

Wired, no patch currently. `IINA_REF` is pinned in `manifest.env`.

## Conventions & regeneration

Name patches `NNNN-description.patch` (numeric prefix = apply order); a patch is a `-p1` unified diff
rooted at the dependency's top dir. Any change under `patches/` busts the deps cache.

The FFmpeg patches come from `~/ffmpeg-mmt`, branch `series-final` (base `3dcc0f0` + the four fix
commits). `0001` is the base commit with its `Changelog`/`doc` hunks stripped (their context drifts
between point releases and would reject on FFmpeg 8.0); `0002`–`0005` are the fix commits:

```sh
cd ~/ffmpeg-mmt
git format-patch --stdout -1 3dcc0f0 | awk '
  /^diff --git a\/Changelog/{skip=1} /^diff --git a\/doc\//{skip=1}
  /^diff --git/ && $0 !~ /Changelog|doc\//{skip=0}
  /^ Changelog +\|/{next} /^ doc\/demuxers\.texi +\|/{next}
  !skip' > patches/ffmpeg/0001-mmttlv-demuxer.patch
git format-patch 3dcc0f0..series-final -o /tmp/series --no-signature   # then rename 0002-0005 to slugs
```

All five apply to a stock `n8.0` tree with zero rejects.
