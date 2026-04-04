const output = document.getElementById('output');
const input = document.getElementById('user-input');
const btn = document.getElementById('send-btn');
const stopBtn = document.getElementById('stop-btn');
const langSelect = document.getElementById('lang-select');

let gameStarted = false;

// Funkce pro plynulé vypisování textu
async function typeWriter(text) {
    const div = document.createElement('div');
    div.className = 'ai-response';
    output.appendChild(div);
    
    // Rozdělíme na znaky pro efekt psacího stroje
    for (let char of text) {
        div.innerHTML += char;
        output.scrollTop = output.scrollHeight;
        await new Promise(r => setTimeout(r, 10)); 
    }
}

async function playGame() {
    let rawText = input.value.trim();
    if (!rawText) return;

    let processedText = rawText;
    if (gameStarted) {
        processedText = rawText.replace(/[^a-zA-Z]/g, "").toUpperCase();
        if (!['A', 'B', 'C'].includes(processedText)) {
            const errorMsg = document.createElement('div');
            errorMsg.className = 'error-msg';
            errorMsg.innerHTML = `\n> ${rawText}\n[ INVALID_INPUT ]: Vyberte A, B nebo C.`;
            output.appendChild(errorMsg);
            input.value = '';
            return;
        }
    }

    // Zobrazení vstupu uživatele
    const userDiv = document.createElement('div');
    userDiv.style.color = '#fff';
    userDiv.innerHTML = `<br>> ${rawText}`;
    output.appendChild(userDiv);

    const isStart = !gameStarted;
    const currentLang = langSelect.value;
    
    input.value = '';
    input.disabled = true;
    btn.disabled = true;

    // Animace načítání
    const loading = document.createElement('div');
    loading.innerHTML = "[ COMMUNICATING WITH NEURAL NETWORK... ]";
    output.appendChild(loading);

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                prompt: processedText, 
                is_start: isStart,
                lang: currentLang 
            })
        });

        const data = await response.json();
        loading.remove();
        
        await typeWriter(data.response);
        
        const line = document.createElement('div');
        line.innerHTML = "------------------------------------------";
        output.appendChild(line);
        
        gameStarted = true;
    } catch (err) {
        loading.innerHTML = "[ CRITICAL_ERROR ]: Připojení ztraceno.";
    } finally {
        input.disabled = false;
        btn.disabled = false;
        input.focus();
        output.scrollTop = output.scrollHeight;
    }
}

stopBtn.onclick = () => {
    output.innerHTML = "[ SYSTEM SHUTDOWN ]";
    setTimeout(() => location.reload(), 500);
};

function startBossFight() {
    output.innerHTML += `<div class="boss-arena">BOSS FIGHT! Нажимай буквы: <span id="target-char">?</span></div>`;
    let wins = 0;
    const target = document.getElementById('target-char');
    
    function nextChar() {
        if (wins >= 5) {
            output.innerHTML += "<div>[ BOSS DEFEATED ]: Доступ восстановлен.</div>";
            gameStarted = true; // Возвращаемся в игру
            return;
        }
        const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        const randomChar = chars[Math.floor(Math.random() * chars.length)];
        target.innerText = randomChar;
    }

    window.onkeydown = (e) => {
        if (e.key.toUpperCase() === target.innerText) {
            wins++;
            nextChar();
        }
    };
    nextChar();
}
btn.onclick = playGame;
input.onkeypress = (e) => { if (e.key === 'Enter') playGame(); };
