const output = document.getElementById('output');
const input = document.getElementById('user-input');
const btn = document.getElementById('send-btn');
const stopBtn = document.getElementById('stop-btn');
const langSelect = document.getElementById('lang-select');
const fileInput = document.getElementById('file-input');
const bossUi = document.getElementById('boss-ui');

let gameStarted = false;
let currentQuestionNum = 0;

async function typeWriter(text) {
    const div = document.createElement('div');
    div.className = 'ai-response';
    output.appendChild(div);
    for (let char of text) {
        div.innerHTML += char;
        output.scrollTop = output.scrollHeight;
        await new Promise(r => setTimeout(r, 15)); 
    }
}

async function playGame() {
    let rawText = input.value.trim();
    if (!rawText && !gameStarted) return;

    // Pokud hra běží, kontrolujeme formát odpovědi (A, B, C)
    if (gameStarted && !['A', 'B', 'C'].includes(rawText.toUpperCase())) {
        const errorMsg = document.createElement('div');
        errorMsg.style.color = "#ff3333";
        errorMsg.innerHTML = `> ${rawText}<br>[ ERROR ]: Zadejte pouze A, B nebo C.`;
        output.appendChild(errorMsg);
        input.value = '';
        return;
    }

    const processedText = rawText;
    input.value = '';
    input.disabled = true;
    btn.disabled = true;

    const loading = document.createElement('div');
    loading.innerHTML = "[ SYNCING WITH TERMINAL... ]";
    output.appendChild(loading);

    try {
        let response;
        if (!gameStarted) {
            // PRVNÍ START - posíláme soubor přes FormData
            const formData = new FormData();
            formData.append('topic', processedText || "General Security");
            if (fileInput.files[0]) {
                formData.append('file', fileInput.files[0]);
            }

            response = await fetch('/api/start', {
                method: 'POST',
                body: formData // U FormData se neposílá Content-Type header manuálně
            });
        } else {
            // DALŠÍ OTÁZKY - posíláme JSON
            response = await fetch('/api/answer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ answer: processedText })
            });
        }

        const data = await response.json();
        loading.remove();

        if (data.status === "game") {
            gameStarted = true;
            const q = data.data; // JSON s otázkou
            const textToPrint = `\n[ OTÁZKA ${data.progress}/10 ]\n${q.q}\n\nA) ${q.a}\nB) ${q.b}\nC) ${q.c}`;
            await typeWriter(textToPrint);
        } 
        else if (data.status === "boss_fight") {
            await typeWriter("\n[ !!! ] SECURITY ALERT: Příliš mnoho chyb. Spouštím protiopatření...");
            startBossFight();
        }
        else if (data.status === "win") {
            await typeWriter(`\n[ ACCESS GRANTED ]: ${data.message}\n\nANALÝZA:\n${data.analysis || "Skvělý výkon, terminál ovládnut."}`);
            gameStarted = false;
        }
        else if (data.status === "wrong") {
            await typeWriter(`\n[ CHYBA ]: Nesprávná odpověď. Správně bylo: ${data.correct}.`);
            // Po zobrazení chyby automaticky načteme další otázku (volitelné)
            // nebo necháme uživatele něco napsat
        }

    } catch (err) {
        console.error(err);
        loading.innerHTML = "[ CRITICAL_ERROR ]: Spojení s jádrem přerušeno.";
    } finally {
        input.disabled = false;
        btn.disabled = false;
        input.focus();
        output.scrollTop = output.scrollHeight;
    }
}

function startBossFight() {
    bossUi.style.display = 'block';
    input.disabled = true;
    btn.disabled = true;
    
    let wins = 0;
    const target = document.getElementById('target-char');
    const progress = document.getElementById('boss-progress');
    
    function nextChar() {
        if (wins >= 5) {
            bossUi.style.display = 'none';
            input.disabled = false;
            btn.disabled = false;
            fetch('/api/boss_success', { method: 'POST' }).then(() => {
                typeWriter("\n[ BOSS DEFEATED ]: Systém obnoven. Pokračujeme...");
                // Tady by se měla načíst další otázka, ale pro jednoduchost počkáme na další input
            });
            return;
        }
        const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        const randomChar = chars[Math.floor(Math.random() * chars.length)];
        target.innerText = randomChar;
    }

    window.onkeydown = (e) => {
        if (bossUi.style.display === 'block') {
            if (e.key.toUpperCase() === target.innerText) {
                wins++;
                progress.innerText = `Sync: ${wins} / 5`;
                nextChar();
            }
        }
    };
    nextChar();
}

btn.onclick = playGame;
input.onkeydown = (e) => { if (e.key === 'Enter') playGame(); };

stopBtn.onclick = () => {
    output.innerHTML = "[ SYSTEM SHUTDOWN ]";
    setTimeout(() => location.reload(), 800);
};
