(function(clicks, trigger) {
    const clicked = (clicks != null && clicks > 0);
    const idx = (trigger && trigger.index != null) ? trigger.index : 0;
    const last = (window.__lastRefreshIndex__ ?? 0);
    const triggered = (idx > last);
    if (!clicked && !triggered) return window.dash_clientside.no_update;
    if (triggered) window.__lastRefreshIndex__ = idx;
    window.location.reload();
})