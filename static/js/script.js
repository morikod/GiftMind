const output = document.getElementById('output');
const input = document.getElementById('user-input');
const btn = document.getElementById('send-btn');

// Efekt psacího stroje
function typeText(element, text, speed = 15) {
    return new Promise((resolve) => {
        let i = 0;
        function type() {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                output.scrollTop = output.scrollHeight;
                setTimeout(type, speed);
            } else {
                resolve();
            }
        }
        type();
    });
}

async function playGame() {
    const text = input.value.trim();
    if (!text) return;

    output.innerHTML += `\n> ${text}\n`;
    input.value = '';
    input.disabled = true;
    btn.disabled = true;

    const typingMsg = document.createElement('div');
    typingMsg.className = 'system-msg';
    typingMsg.innerText = '[ AI přemýšlí... ]';
    output.appendChild(typingMsg);
    output.scrollTop = output.scrollHeight;

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: text })
        });

        if (!response.ok) throw new Error('Chyba serveru');

        const data = await response.json();
        typingMsg.remove();
        
        const responseContainer = document.createElement('span');
        output.appendChild(responseContainer);
        
        await typeText(responseContainer, data.response);
        
        output.innerHTML += `\n--------------------------\n`;
        
    } catch (err) {
        typingMsg.remove();
        output.innerHTML += `\n<span class="error-msg">[CHYBA]: Spojení přerušeno.</span>\n`;
    } finally {
        input.disabled = false;
        btn.disabled = false;
        input.focus();
        output.scrollTop = output.scrollHeight;
    }
}

btn.addEventListener('click', playGame);
input.addEventListener('keypress', (e) => { 
    if (e.key === 'Enter') playGame(); 
});