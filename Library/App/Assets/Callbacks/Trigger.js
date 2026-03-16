/**
 * @param {Object} payload
 * @param {Array} payload.original_outputs
 * @param {Array} payload.injected_inputs
 * @param {Array} payload.injected_states
 * @param {Array} payload.original_inputs
 * @param {Array} payload.original_states
 */
(function(payload) {
    if (!payload.injected_inputs[0]) return window.dash_clientside.no_update;
    let t = Object.assign({}, payload.injected_inputs[0] || {});
    t.index = (t.index || 0) + 1;
    t.counter = (t.counter || 0) + 1;
    return t;
})