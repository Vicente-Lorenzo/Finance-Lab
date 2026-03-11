(function(refresh_clicks, reset_trigger, refresh_trigger) {
    const r_clicked = (refresh_clicks != null && refresh_clicks > 0);
    
    const c_idx = (reset_trigger && reset_trigger.index != null) ? reset_trigger.index : 0;
    const c_last = (window.__lastResetIndex__ ?? 0);
    const c_triggered = (c_idx > c_last);

    const r_idx = (refresh_trigger && refresh_trigger.index != null) ? refresh_trigger.index : 0;
    const r_last = (window.__lastRefreshIndex__ ?? 0);
    const r_triggered = (r_idx > r_last);

    if (!r_clicked && !c_triggered && !r_triggered) return window.dash_clientside.no_update;
    
    if (c_triggered) window.__lastResetIndex__ = c_idx;
    if (r_triggered) window.__lastRefreshIndex__ = r_idx;
    
    window.location.reload();
})