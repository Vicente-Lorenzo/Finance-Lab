(function(nav) {
    if (!nav || !nav.href || nav.index == null) return window.dash_clientside.no_update;
    const last = (window.__lastNavIndex__ ?? -1);
    if (nav.index <= last) return window.dash_clientside.no_update;
    window.__lastNavIndex__ = nav.index;
    const href = nav.href;
    if (nav.external) {
        window.open(href, "_blank", "noopener,noreferrer");
        return "";
    }
    window.history.pushState({}, "", href);
    window.dispatchEvent(new PopStateEvent("popstate"));
})