"""View modules — one file per page."""
from views.dashboard    import render as dashboard
from views.projeler     import render as projeler
from views.gorevler     import render as gorevler
from views.hammaddeler import render as _hammaddeler_render


def hammaddeler(user=None, material_id=None):
    return _hammaddeler_render(current_user=user, material_id=material_id)
from views.placeholder  import render as placeholder
from views.ayarlar      import render as ayarlar

__all__ = ["dashboard", "projeler", "gorevler", "hammaddeler", "placeholder", "ayarlar"]
