const testCases = [
    { input: '{"a": 1, "b": "hello"}', name: "Valid JSON", expected: true },
    { input: "{'a': 1, 'b': 'hello'}", name: "Python Dict String", expected: true },
    { input: "{'a': True, 'b': False, 'c': None}", name: "Python Booleans/None", expected: true },
    { input: "{'nested': {'x': 1}}", name: "Nested Python Dict", expected: true },
    { input: "{'list': [1, 2, 'three']}", name: "Python List", expected: true },
    { input: 'Not JSON at all', name: "Invalid", expected: false },
    { input: "{'text': \"It's ok\"}", name: "Mixed quotes 1", expected: true },
    { input: "{'text': 'Say \"Hello\"'}", name: "Mixed quotes 2", expected: true },
    { input: "{'key': 'It\\'s tricky'}", name: "Escaped single quote", expected: true },
    { input: "{'key': \"Say \\\"Hello\\\"\"}", name: "Escaped double quote", expected: true },
];

function robustParse(str) {
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

console.log("Running tests...");
let allPassed = true;
testCases.forEach(tc => {
    const result = robustParse(tc.input);
    const success = (result !== null) === tc.expected;
    console.log(`${tc.name}: ${success ? "PASS" : "FAIL"} (Parsed: ${result ? JSON.stringify(result) : "null"})`);
    if (!success) {
        allPassed = false;
        console.log(`  Input: ${tc.input}`);
        if (tc.expected) console.log(`  Expected valid JSON but got null`);
        else console.log(`  Expected failure but got valid JSON`);
    }
});

if (!allPassed) process.exit(1);
