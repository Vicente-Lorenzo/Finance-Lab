from __future__ import annotations

import os
import json
import shutil
from pathlib import Path
from typing import Iterable, Literal

def is_readable(path: Path) -> bool:
    try:
        if path.is_dir():
            next(path.iterdir(), None)
            return True
        if path.is_file() or path.is_symlink():
            with path.open("rb"):
                return True
        return False
    except Exception:
        return False

def is_writable(path: Path) -> bool:
    try:
        base = path if path.is_dir() else path.parent
        if not base.exists():
            return False
        tmp = base / ".write_test.tmp"
        tmp.write_text("x", encoding="utf-8")
        tmp.unlink(missing_ok=True)
        return True
    except Exception:
        return False

def mkdir(path: Path, *, safe: bool = True) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        if safe:
            return False
        raise

def remove(path: Path, *, safe: bool = True) -> bool:
    try:
        if path.is_symlink() or path.is_file():
            path.unlink(missing_ok=True)
        elif path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        return True
    except Exception:
        if safe:
            return False
        raise

def read_text(path: Path, *, safe: bool = True, encoding: str = "utf-8") -> str:
    try:
        return path.read_text(encoding=encoding)
    except Exception:
        if safe:
            return ""
        raise

def write_text(path: Path, text: str, *, safe: bool = True, encoding: str = "utf-8") -> bool:
    try:
        mkdir(path.parent, safe=True)
        path.write_text(text, encoding=encoding)
        return True
    except Exception:
        if safe:
            return False
        raise

def read_json(path: Path, *, safe: bool = True, encoding: str = "utf-8") -> dict:
    try:
        data = json.loads(path.read_text(encoding=encoding))
        return data if isinstance(data, dict) else {}
    except Exception:
        if safe:
            return {}
        raise

def write_json(path: Path, data: dict, *, safe: bool = True, encoding: str = "utf-8") -> bool:
    try:
        mkdir(path.parent, safe=True)
        path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding=encoding)
        return True
    except Exception:
        if safe:
            return False
        raise

def symlink(dst: Path, src: Path, *, safe: bool = True) -> bool:
    try:
        mkdir(dst.parent, safe=True)
        if dst.exists() or dst.is_symlink():
            remove(dst, safe=True)
        os.symlink(str(src), str(dst))
        return True
    except Exception:
        if safe:
            return False
        raise

def hardlink(dst: Path, src: Path, *, safe: bool = True) -> bool:
    try:
        if src.is_dir():
            raise IsADirectoryError(str(src))
        mkdir(dst.parent, safe=True)
        if dst.exists() or dst.is_symlink():
            remove(dst, safe=True)
        os.link(str(src), str(dst))
        return True
    except Exception:
        if safe:
            return False
        raise

def copy(dst: Path, src: Path, *, safe: bool = True) -> bool:
    try:
        mkdir(dst.parent, safe=True)
        if dst.exists() or dst.is_symlink():
            remove(dst, safe=True)
        shutil.copy2(str(src), str(dst))
        return True
    except Exception:
        if safe:
            return False
        raise

def smartlink(dst: Path, src: Path, *, safe: bool = True) -> str | None:
    if symlink(dst, src, safe=True):
        return "symlink"
    if hardlink(dst, src, safe=True):
        return "hardlink"
    if copy(dst, src, safe=True):
        return "copy"
    if safe:
        return None
    raise RuntimeError(f"Failed to link/copy {src} to {dst}")

def mirror(
    *,
    src_root: Path,
    dst_root: Path,
    subdirs: Iterable[str],
    manifest_name: str,
    safe: bool = True,
    conflict: Literal["error", "skip"] = "error"):

    src_root = Path(src_root)
    dst_root = Path(dst_root)
    writable = is_writable(dst_root) if dst_root.exists() else is_writable(dst_root.parent)
    created = 0
    updated = 0
    removed = 0
    conflicts = 0
    mode_counts = {"symlink": 0, "hardlink": 0, "copy": 0}
    for sub in subdirs:
        src_dir = src_root / sub
        dst_dir = dst_root / sub
        manifest_path = dst_dir / manifest_name
        manifest = read_json(manifest_path, safe=True) if manifest_path.exists() else {}
        managed = manifest.get("files") if isinstance(manifest.get("files"), dict) else {}
        if writable:
            mkdir(dst_dir, safe=True)
            if not manifest_path.exists():
                write_json(manifest_path, {"files": {}}, safe=True)
        if not src_dir.exists():
            if writable and managed:
                for rel in list(managed.keys()):
                    remove(dst_dir / rel, safe=True)
                    removed += 1
                managed.clear()
                manifest["files"] = managed
                write_json(manifest_path, manifest, safe=True)
            continue
        seen: set[str] = set()
        for src in src_dir.rglob("*"):
            if src.is_dir():
                continue
            rel = src.relative_to(src_dir).as_posix()
            seen.add(rel)
            dst = dst_dir / rel
            if dst.exists() and rel not in managed:
                conflicts += 1
                if conflict == "error":
                    if safe:
                        continue
                    raise RuntimeError(f"Asset conflict: {dst} shadows library asset {src}")
                continue
            if not writable:
                continue
            if dst.exists() and rel in managed and managed[rel].get("mode") == "copy":
                try:
                    sst, dstst = src.stat(), dst.stat()
                    if sst.st_size != dstst.st_size or sst.st_mtime > dstst.st_mtime:
                        remove(dst, safe=True)
                        updated += 1
                except Exception:
                    remove(dst, safe=True)
                    updated += 1
            if dst.exists():
                continue
            mode = smartlink(dst, src, safe=True)
            if mode is None:
                continue
            managed[rel] = {"src": src.as_posix(), "mode": mode}
            created += 1
            mode_counts[mode] += 1
        if writable:
            for rel in list(managed.keys()):
                if rel not in seen:
                    remove(dst_dir / rel, safe=True)
                    managed.pop(rel, None)
                    removed += 1

            manifest["files"] = managed
            write_json(manifest_path, manifest, safe=True)
    return writable, created, updated, removed, conflicts, mode_counts
