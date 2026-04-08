"""
Phase 2 — SQLite FTS5 global arama katmanı.

``database.global_search`` LIKE sürümünü sarmalar; FTS tablosu yoksa veya
hata olursa otomatik LIKE'a düşer.

İlk ``global_search`` çağrısında tablo boşsa otomatik doldurulur; ayrıca
``python -c "import search_fts; search_fts.ensure_labdog_fts()"`` ile de
çalıştırılabilir.
Veri değişince ``mark_labdog_fts_stale()`` çağrılır; bir sonraki ``global_search``
öncesi ``rebuild_labdog_fts_index()`` ile tam yenileme yapılır. İsterseniz doğrudan
``rebuild_labdog_fts_index()`` de kullanılabilir.
"""
from __future__ import annotations

import json
import re
from typing import Any

from sqlalchemy import text

from database import (
    Experiment,
    Formulation,
    Product,
    Project,
    ProjectNote,
    RawMaterial,
    SessionLocal,
    Task,
    _gs_snip,
    get_engine,
)


def _fts_match_query(raw: str) -> str | None:
    tokens = re.findall(r"[\w\u00C0-\u024F]+", raw, re.UNICODE)
    if not tokens:
        return None
    parts: list[str] = []
    for t in tokens[:10]:
        if len(t) < 1:
            continue
        parts.append('"' + t.replace('"', '""') + '"*')
    return " AND ".join(parts) if parts else None


def ensure_labdog_fts() -> None:
    """FTS tablosunu oluşturur; boşsa indeksi doldurur."""
    engine = get_engine()
    ddl = """
    CREATE VIRTUAL TABLE IF NOT EXISTS labdog_fts USING fts5(
      entity_type UNINDEXED,
      entity_id UNINDEXED,
      code UNINDEXED,
      title,
      body,
      url_json UNINDEXED,
      tokenize='unicode61'
    )
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(ddl))
            conn.commit()
    except Exception:
        return
    try:
        with engine.connect() as conn:
            n = conn.execute(text("SELECT COUNT(*) FROM labdog_fts")).scalar_one()
        if int(n) == 0:
            rebuild_labdog_fts_index()
    except Exception:
        pass


def rebuild_labdog_fts_index() -> tuple[bool, str]:
    """Tüm aranabilir satırları FTS tablosuna yazar (tam yenileme)."""
    engine = get_engine()
    session = SessionLocal()
    rows: list[tuple[str, str, str, str, str, str]] = []

    def uj(d: dict[str, Any]) -> str:
        return json.dumps(d, ensure_ascii=False)

    try:
        for p in session.query(Project).all():
            code = p.code or f"PRJ-{p.id:04d}"
            body = " ".join(
                x for x in (p.description, p.rd_specialist, p.customer, code) if x
            )
            rows.append(
                (
                    "project",
                    str(p.id),
                    code,
                    p.name,
                    body,
                    uj({"page": "Projeler", "project_id": str(p.id)}),
                )
            )

        for t in session.query(Task).all():
            code = t.code or f"TSK-{t.id:04d}"
            body = " ".join(
                x for x in (t.title, t.description, t.assignee, code) if x
            )
            rows.append(
                (
                    "task",
                    str(t.id),
                    code,
                    t.title,
                    body,
                    uj({"page": "Görevler", "task_id": str(t.id)}),
                )
            )

        for m in session.query(RawMaterial).all():
            code = m.code or f"HAM-{m.id:04d}"
            body = " ".join(
                x
                for x in (
                    m.name,
                    m.stock_name,
                    m.supplier,
                    m.brand,
                    m.function,
                    m.cas_number,
                    m.notes,
                    m.safety_data_sheet_url,
                    m.tds_url,
                    code,
                )
                if x
            )
            rows.append(
                (
                    "material",
                    str(m.id),
                    code,
                    m.name,
                    body,
                    uj({"page": "Hammaddeler", "material_id": str(m.id)}),
                )
            )

        for f in session.query(Formulation).all():
            code = f.code or f"FRM-{f.id:04d}"
            body = " ".join(x for x in (f.name, f.notes, code, str(f.version)) if x)
            rows.append(
                (
                    "formulation",
                    str(f.id),
                    code,
                    f.name,
                    body,
                    uj(
                        {
                            "page": "Projeler",
                            "project_id": str(f.project_id),
                            "project_tab": "form",
                            "formulation_id": str(f.id),
                        }
                    ),
                )
            )

        for pr in session.query(Product).all():
            code = pr.code or f"URN-{pr.id:04d}"
            body = " ".join(x for x in (pr.name, pr.notes, code) if x)
            rows.append(
                (
                    "product",
                    str(pr.id),
                    code,
                    pr.name,
                    body,
                    uj(
                        {
                            "page": "Projeler",
                            "project_id": str(pr.project_id),
                            "project_tab": "form",
                            "product_id": str(pr.id),
                        }
                    ),
                )
            )

        for n in session.query(ProjectNote).all():
            proj = session.get(Project, n.project_id)
            pname = proj.name if proj else ""
            title = _gs_snip(n.content, 80) or "(Not)"
            body = " ".join(x for x in (n.content, n.author, pname, n.note_type.value) if x)
            rows.append(
                (
                    "note",
                    str(n.id),
                    "",
                    title,
                    body,
                    uj(
                        {
                            "page": "Projeler",
                            "project_id": str(n.project_id),
                            "project_tab": "notlar",
                            "note_id": str(n.id),
                        }
                    ),
                )
            )

        for e in session.query(Experiment).all():
            code = e.code or f"DNY-{e.id:04d}"
            body = " ".join(x for x in (e.title, e.notes, code) if x)
            rows.append(
                (
                    "experiment",
                    str(e.id),
                    code,
                    e.title,
                    body,
                    uj(
                        {
                            "page": "Projeler",
                            "project_id": str(e.project_id),
                            "project_tab": "deney",
                            "experiment_id": str(e.id),
                        }
                    ),
                )
            )

        ins = text(
            """INSERT INTO labdog_fts(
            entity_type, entity_id, code, title, body, url_json
            ) VALUES (:t,:eid,:c,:ti,:bo,:uj)"""
        )
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM labdog_fts"))
            for r in rows:
                conn.execute(
                    ins,
                    {
                        "t": r[0],
                        "eid": r[1],
                        "c": r[2],
                        "ti": r[3],
                        "bo": r[4],
                        "uj": r[5],
                    },
                )
        return True, f"{len(rows)} FTS satırı yazıldı."
    except Exception as exc:
        return False, str(exc)
    finally:
        session.close()


def _global_search_fts_only(
    q: str,
    *,
    max_total: int = 80,
) -> list[dict[str, Any]] | None:
    raw = (q or "").strip()
    if len(raw) < 2:
        return []
    mq = _fts_match_query(raw)
    if not mq:
        return None
    engine = get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """SELECT entity_type, entity_id, code, title, body, url_json
                    FROM labdog_fts
                    WHERE labdog_fts MATCH :mq
                    ORDER BY rank
                    LIMIT :lim"""
                ),
                {"mq": mq, "lim": max_total},
            )
            out: list[dict[str, Any]] = []
            for row in result.mappings():
                url = json.loads(row["url_json"])
                code = row["code"] or None
                if code == "":
                    code = None
                out.append(
                    {
                        "type":    row["entity_type"],
                        "title":   row["title"] or "",
                        "snippet": _gs_snip(row["body"]),
                        "code":    code,
                        "url":     url,
                    }
                )
            return out
    except Exception:
        return None


_fts_lazy_init_done = False
_fts_index_stale = False


def mark_labdog_fts_stale() -> None:
    """Aranabilir veri değişti; bir sonraki FTS aramasından önce indeks yenilenecek."""
    global _fts_index_stale
    _fts_index_stale = True


def global_search(
    q: str,
    *,
    limit_per_type: int = 12,
    max_total: int = 80,
) -> list[dict[str, Any]]:
    """
    Önce FTS5; tablo/sorgu hatasında ``database.global_search`` (LIKE).
    İlk çağrıda FTS tablosu yoksa oluşturulup boşsa indeks doldurulur.
    Commit sonrası işaretlenen değişikliklerde indeks tam yenilenir.
    """
    global _fts_lazy_init_done, _fts_index_stale
    if not _fts_lazy_init_done:
        ensure_labdog_fts()
        _fts_lazy_init_done = True
    if _fts_index_stale:
        try:
            rebuild_labdog_fts_index()
        except Exception:
            pass
        _fts_index_stale = False
    fts = _global_search_fts_only(q, max_total=max_total)
    if fts is not None:
        return fts
    from database import global_search as _like

    return _like(q, limit_per_type=limit_per_type, max_total=max_total)
