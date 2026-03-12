(function(refresh_clicks, refresh_trigger) {
    const r_clicked = (refresh_clicks != null && refresh_clicks > 0);

    const r_idx = (refresh_trigger && refresh_trigger.index != null) ? refresh_trigger.index : 0;
    const r_last = (window.__lastRefreshIndex__ ?? 0);

    if (r_clicked || r_idx > r_last) {
        window.__lastRefreshIndex__ = r_idx;
        window.location.reload();
        return window.dash_clientside.no_update;
    }

    return window.dash_clientside.no_update;
})