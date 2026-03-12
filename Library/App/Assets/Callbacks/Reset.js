(function(result, injectInputs, injectStates, originalInputs, originalStates) {
    // This is now an Injection Function.
    // injectInputs[0] = n_clicks
    // injectInputs[1] = trigger

    const n_clicks = injectInputs[0];
    const trigger = injectInputs[1];

    const op_index = (trigger && trigger.index != null) ? trigger.index : (n_clicks || 0);

    // 2. Synchronize via Window (Single Source of Truth for Client)
    // If this is a new operation index, reset the window counter.
    if (window._clean_reset_idx !== op_index) {
        window._clean_reset_idx = op_index;
        window._clean_reset_cnt = 0;
    }

    // 3. Atomically Increment
    window._clean_reset_cnt++;

    // 4. Construct the Counter Payload
    let t = {
        index: window._clean_reset_idx,
        counter: window._clean_reset_cnt
    };

    // Return ONLY the injected output (the counter)
    return t;
})