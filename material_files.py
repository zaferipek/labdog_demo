"""
Yerel MSDS/TDS PDF depolama — ``uploads/materials/{id}/msds.pdf`` ve ``tds.pdf``.

Güvenlik: yalnızca proje kökü altında, ilgili hammadde klasörüne yazma/okuma/silme.
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Literal

PROJECT_ROOT = Path(__file__).resolve().parent
UPLOADS_DIR = PROJECT_ROOT / "uploads"
MATERIALS_DIR_NAME = "materials"

# Plan: PDF öncelikli; OneDrive senkronu büyük dosyalarda yük getirebilir.
MAX_PDF_BYTES = 25 * 1024 * 1024

DocKind = Literal["msds", "tds"]


def material_upload_dir(material_id: int) -> Path:
    return UPLOADS_DIR / MATERIALS_DIR_NAME / str(int(material_id))


def relative_db_path(material_id: int, kind: DocKind) -> str:
    """Veritabanında saklanan göreli yol (posix)."""
    p = material_upload_dir(material_id) / f"{kind}.pdf"
    return str(p.relative_to(PROJECT_ROOT)).replace("\\", "/")


def _resolved_under_material(rel: str, material_id: int) -> Path | None:
    if not rel or not isinstance(rel, str):
        return None
    norm = rel.replace("\\", "/").strip()
    parts = [p for p in norm.split("/") if p]
    if ".." in parts or norm.startswith("/"):
        return None
    try:
        full = (PROJECT_ROOT / norm).resolve()
        base = material_upload_dir(material_id).resolve()
        full.relative_to(base)
    except (ValueError, OSError):
        return None
    return full


def read_material_pdf(rel: str | None, material_id: int) -> bytes | None:
    """Güvenli okuma; yol bu hammaddenin klasöründe değilse None."""
    if not rel:
        return None
    p = _resolved_under_material(rel, material_id)
    if p is None or not p.is_file():
        return None
    return p.read_bytes()


def delete_relative_pdf(rel: str | None, material_id: int) -> None:
    p = _resolved_under_material(rel, material_id) if rel else None
    if p is not None and p.is_file():
        p.unlink(missing_ok=True)


def delete_material_upload_folder(material_id: int) -> None:
    d = material_upload_dir(material_id)
    if d.is_dir():
        shutil.rmtree(d, ignore_errors=True)


def save_material_pdf(
    material_id: int,
    kind: DocKind,
    file_bytes: bytes,
    original_filename: str,
) -> tuple[bool, str, str | None]:
    """
    PDF kaydet; sabit dosya adı: ``msds.pdf`` / ``tds.pdf``.
    Dönüş: (başarı, mesaj, db için göreli yol).
    """
    if kind not in ("msds", "tds"):
        return False, "Geçersiz belge türü.", None
    if len(file_bytes) > MAX_PDF_BYTES:
        return False, f"Dosya çok büyük (en fazla {MAX_PDF_BYTES // (1024 * 1024)} MB).", None
    ext = Path(original_filename or "").suffix.lower()
    if ext != ".pdf":
        return False, "Yalnızca PDF yüklenebilir.", None
    dest_dir = material_upload_dir(material_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{kind}.pdf"
    dest.write_bytes(file_bytes)
    rel = str(dest.relative_to(PROJECT_ROOT)).replace("\\", "/")
    return True, "Kaydedildi.", rel
