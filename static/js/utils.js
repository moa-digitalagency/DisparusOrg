// Security Utility
function escapeHtml(text) {
    if (!text) return '';
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Robust JSON Parser for Python-style strings (e.g. single quotes, True/False/None)
function robustJSONParse(str) {
    if (typeof str !== 'string') return null;

    // First, try standard JSON parse
    try {
        return JSON.parse(str);
    } catch (e) {
        // Continue to repair logic
    }

    let out = '';
    let buffer = '';
    let inString = false;
    let quoteChar = null; // The original quote char used in input (' or ")
    let escaped = false;

    // Helper to process non-string parts (keywords)
    function flushBuffer() {
        if (buffer) {
            let replaced = buffer
                .replace(/\bTrue\b/g, 'true')
                .replace(/\bFalse\b/g, 'false')
                .replace(/\bNone\b/g, 'null');
            out += replaced;
            buffer = '';
        }
    }

    for (let i = 0; i < str.length; i++) {
        let char = str[i];

        if (inString) {
            if (escaped) {
                // Previous char was backslash.
                // If original string was single-quoted, and we see \', we output just '
                if (quoteChar === "'" && char === "'") {
                    out += "'";
                } else {
                    // Otherwise output the backslash and the char
                    out += '\\' + char;
                }
                escaped = false;
            } else if (char === '\\') {
                escaped = true;
            } else if (char === quoteChar) {
                // End of string
                out += '"'; // Close with double quote
                inString = false;
                quoteChar = null;
            } else {
                if (char === '"') {
                    // Unescaped double quote inside string
                    // Must escape it because we are wrapping in double quotes
                    out += '\\"';
                } else {
                    out += char;
                }
            }
        } else {
            if (char === "'" || char === '"') {
                flushBuffer();
                inString = true;
                quoteChar = char;
                out += '"'; // Start with double quote
            } else {
                buffer += char;
            }
        }
    }
    // Handle any remaining buffer
    flushBuffer();

    try {
        return JSON.parse(out);
    } catch (e) {
        return null;
    }
}
