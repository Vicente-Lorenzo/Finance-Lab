(function(result, injectInputs) {
    let t = injectInputs[0] || {};
    t.index = (t.index || 0) + 1;
    t.counter = (t.counter || 0) + 1;
    return t;
})