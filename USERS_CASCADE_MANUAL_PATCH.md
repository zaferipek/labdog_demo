# Kullanıcı güncellemesi → görev / not / proje metin alanları

**Durum:** Tüm mantık **`database.update_user`** içinde (tek transaction).

1. **Ad Soyad (görünen isim)** değişince: `Task.assignee`, `ProjectNote.author`, `Project.rd_specialist` alanlarında eski görünen adla **tam eşleşen** değerler yeni ada çekilir.
2. **Giriş kullanıcı adı** değişince: aynı üç alanda eski kullanıcı adıyla **tam eşleşen** değerler yeni kullanıcı adına çekilir (önce görünen ad güncellemesi uygulanır).

Ardından global FTS indeksi gerekirse **`search_fts.mark_labdog_fts_stale()`** ile sonraki aramada yenilenir.

`views/users.py` içinde ek kod gerekmez.
