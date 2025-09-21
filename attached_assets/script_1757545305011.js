let editor;

require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' }});
require(['vs/editor/editor.main'], function() {
    editor = monaco.editor.create(document.getElementById('editor'), {
        value: '# Schreibe hier deinen Python Code...\nprint("Hello, AI Agent!")',
        language: 'python',
        theme: 'vs-dark',
        automaticLayout: true
    });
});

async function sendMessage() {
    const input = document.getElementById("userInput");
    const message = input.value;
    if (!message) return;
    addMessage("Du", message);
    input.value = "";

    const response = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: message})
    });
    const data = await response.json();
    addMessage("Agent", data.response);
}

async function executeCode() {
    const code = editor.getValue();
    if (!code) return;

    const response = await fetch("/execute", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({code: code})
    });
    const data = await response.json();
    document.getElementById("output").textContent = data.output;
}

function addMessage(sender, text) {
    const chat = document.getElementById("chat");
    const div = document.createElement("div");
    div.textContent = sender + ": " + text;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}
