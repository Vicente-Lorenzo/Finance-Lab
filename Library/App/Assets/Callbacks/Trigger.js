(function(result, injectInputs) {
    if (!injectInputs[0]) return window.dash_clientside.no_update;
    let t = Object.assign({}, injectInputs[0] || {});
    t.index = (t.index || 0) + 1;
    t.counter = (t.counter || 0) + 1;
    return t;
})