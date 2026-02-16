
const testCases = [
    { input: '{"a": 1, "b": "hello"}', name: "Valid JSON", expected: true },
    { input: "{'a': 1, 'b': 'hello'}", name: "Python Dict String", expected: true },
    { input: "{'a': True, 'b': False, 'c': None}", name: "Python Booleans/None", expected: true },
    { input: "{'nested': {'x': 1}}", name: "Nested Python Dict", expected: true },
    { input: "{'list': [1, 2, 'three']}", name: "Python List", expected: true },
    { input: 'Not JSON at all', name: "Invalid", expected: false },
    { input: "{'text': \"It's ok\"}", name: "Mixed quotes 1", expected: false }, // Simple replace fails here
    { input: "{'text': 'Say \"Hello\"'}", name: "Mixed quotes 2", expected: false }, // Simple replace fails here
];

function robustParse(str) {
    try {
        return JSON.parse(str);
    } catch (e) {
        try {
            // Attempt to fix common Python string representation issues
            // This is a best-effort heuristic
            let fixed = str
                .replace(/'/g, '"')
                .replace(/\bTrue\b/g, 'true')
                .replace(/\bFalse\b/g, 'false')
                .replace(/\bNone\b/g, 'null');
            return JSON.parse(fixed);
        } catch (e2) {
            return null; // Failed
        }
    }
}

console.log("Running tests...");
testCases.forEach(tc => {
    const result = robustParse(tc.input);
    const success = (result !== null) === tc.expected;
    console.log(`${tc.name}: ${success ? "PASS" : "FAIL"} (Parsed: ${result ? JSON.stringify(result) : "null"})`);
    if (!success && tc.expected) {
        console.log(`  Failed input: ${tc.input}`);
        // Debug
        let fixed = tc.input
                .replace(/'/g, '"')
                .replace(/\bTrue\b/g, 'true')
                .replace(/\bFalse\b/g, 'false')
                .replace(/\bNone\b/g, 'null');
        console.log(`  Fixed attempt: ${fixed}`);
    }
});
