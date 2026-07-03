#!/usr/bin/env python3
"""Reconcile IINA's project.pbxproj dylib references with the dylibs we actually built.

IINA's project pins the exact versioned dylib filenames of its prebuilt bundle (e.g.
libavcodec.61.dylib, libnettle.8.dylib). Building the dependencies from source with current
Homebrew bottles + our patched FFmpeg produces newer sonames (libavcodec.62, libnettle.9, ...),
and a slightly different set. Each dylib is referenced in the project both to LINK (-l flags) and
to EMBED (Copy Files -> Frameworks), by filename, so a filename remap fixes both.

For every versioned dylib the project references:
  - if we built the same library at a different version -> rewrite the filename everywhere;
  - if we did not build it at all (e.g. libpostproc when FFmpeg has no --enable-postproc, or the
    x86_64-only libgcc_s / libstdc++ on an arm64 build) -> drop every line that references it, so
    it is neither linked nor embedded.

Libraries we built that the project does NOT reference ("extras", transitive deps of our mpv) are
left to a post-build copy into the app bundle, so they are still present at runtime.

Usage: reconcile_dylibs.py <project.pbxproj> <deps/lib dir>
"""
import os, re, sys, glob


def stem(fn: str) -> str:
    """Library identity = filename minus '.dylib' minus the trailing run of numeric ('.N')
    version components. Name-embedded digits stay (libX11.6 -> libX11, libpng16.16 -> libpng16,
    libjxl_cms.0.11 -> libjxl_cms), because only purely-numeric trailing parts are the version."""
    parts = fn[:-len(".dylib")].split(".")
    while len(parts) > 1 and parts[-1].isdigit():
        parts.pop()
    return ".".join(parts)


def main() -> int:
    proj_path, libdir = sys.argv[1], sys.argv[2]
    # Real dylibs we built (ignore symlinks; the versioned real file is the canonical one).
    actual = {}
    for p in glob.glob(os.path.join(libdir, "*.dylib")):
        if os.path.islink(p):
            continue
        actual[stem(os.path.basename(p))] = os.path.basename(p)

    text = open(proj_path).read()
    referenced = sorted(set(re.findall(r"lib[A-Za-z0-9_+-]+(?:\.\d+)+\.dylib", text)))

    remap, drop = {}, []
    for ref in referenced:
        s = stem(ref)
        if s in actual:
            if actual[s] != ref:
                remap[ref] = actual[s]
        else:
            drop.append(ref)

    # Drop first (whole lines mentioning an unbuilt dylib: its PBXBuildFile, PBXFileReference,
    # link-phase and embed-phase membership all carry the filename in a comment).
    if drop:
        keep = [ln for ln in text.splitlines(keepends=True)
                if not any(d in ln for d in drop)]
        text = "".join(keep)
        for d in drop:
            print(f"drop    {d}")
    # Then remap version-skewed filenames everywhere they appear.
    for old, new in remap.items():
        text = text.replace(old, new)
        print(f"remap   {old} -> {new}")

    open(proj_path, "w").write(text)
    print(f"\nreconciled: {len(remap)} remapped, {len(drop)} dropped, "
          f"{len(actual)} dylibs built")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
