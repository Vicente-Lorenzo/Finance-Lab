(function(clicks, trigger) {
    if (!clicks && !trigger) return window.dash_clientside.no_update;
    window.location.reload();
    return window.dash_clientside.no_update;
})