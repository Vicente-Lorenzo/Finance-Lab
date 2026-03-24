/**
 * @param {number} clicks
 * @param {string} to
 * @param {string} cc
 * @param {string} bcc
 * @param {string} subject
 * @param {string} body
 */
(function(clicks, to, cc, bcc, subject, body) {
    if (!clicks) return;
    to = to || '';
    const params = [];
    if (cc) params.push(`cc=${encodeURIComponent(cc)}`);
    if (bcc) params.push(`bcc=${encodeURIComponent(bcc)}`);
    if (subject) params.push(`subject=${encodeURIComponent(subject)}`);
    if (body) params.push(`body=${encodeURIComponent(body)}`);
    const queryString = params.length > 0 ? '?' + params.join('&') : '';
    window.location.href = `mailto:${to}${queryString}`;
})