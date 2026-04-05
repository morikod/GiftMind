const output = document.getElementById('output');
const input = document.getElementById('user-input');
const btn = document.getElementById('send-btn');
const langSelect = document.getElementById('lang-select');
const fileInput = document.getElementById('file-input');
const bossUi = document.getElementById('boss-ui');

let gameStarted = false;
let bossModeActive = false; // Флаг для блокировки ввода во время Boss Fight

async function typeWriter(text, color = 'inherit', whiteSpace = 'pre') {
    const div = document.createElement('div');
    div.className = 'ai-response';
    div.style.color = color;
    div.style.whiteSpace = whiteSpace; // 'pre' для ASCII дракона, 'pre-wrap' для текста
    output.appendChild(div);
    
    // Эффект печати
    for (let char of text) {
        div.innerHTML += char;
        output.scrollTop = output.scrollHeight;
        await new Promise(r => setTimeout(r, 8)); // Чуть быстрее печать
    }
}

async function playGame() {
    if (bossModeActive) return; // Блокируем ввод, если идет Boss Fight

    let rawText = input.value.trim();
    if (!rawText && !gameStarted) return;

    // ВЫВОД ЭХО (User Input) - Теперь видно, что ты пишешь!
    const userMsg = document.createElement('div');
    userMsg.style.color = "#ffff00"; // Желтый цвет для ввода пользователя
    userMsg.style.fontWeight = "bold";
    userMsg.innerHTML = `<br>> ${rawText}`;
    output.appendChild(userMsg);
    output.scrollTop = output.scrollHeight;

    // Контроль ввода тестов (A,B,C) только если это Quiz
    if (gameStarted && currentQType === "quiz" && !['A', 'B', 'C'].includes(rawText.toUpperCase())) {
        await typeWriter("\n[ ERROR ]: Zadejte pouze A, B nebo C.", "#ff3333", "pre-wrap");
        input.value = '';
        return;
    }

    const processedText = rawText;
    input.value = '';
    input.disabled = true;
    btn.disabled = true;

    const loading = document.createElement('div');
    loading.innerHTML = "[ COMMUNICATING... ]";
    output.appendChild(loading);
    output.scrollTop = output.scrollHeight;

    try {
        let response;
        if (!gameStarted) {
            // СТАРТ: Формируем FormData для отправки файла
            const formData = new FormData();
            formData.append('topic', processedText || "General IT Security");
            if (fileInput.files[0]) {
                formData.append('file', fileInput.files[0]);
            }
            response = await fetch('/api/start', { method: 'POST', body: formData });
        } else {
            // ИГРА: Отправляем JSON с ответом
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
            currentQType = data.type; // Запоминаем тип вопроса (quiz/open)
            const q = data.data;
            let msg = `\n[ OTÁZKA ${data.progress}/10 ] | Errors: ${data.errors}/3\n${q.q}\n`;
            
            if (currentQType === "quiz") {
                msg += `\n A) ${q.a}\n B) ${q.b}\n C) ${q.c}\n\n> Vaše volba:`;
            } else {
                msg += `\n> Napište Vaši odpověď:`;
            }
            await typeWriter(msg, 'inherit', "pre-wrap");
        } 
        
        else if (data.status === "wrong") {
            await typeWriter(`\n[ CHYBA ]: Nesprávná odpověď. Správně было: ${data.correct}.\n------------------------------------------`, "#ff3333", "pre-wrap");
            // После ошибки просто ждем ввода пользователя, сервер уже приготовил текущий вопрос
        }

        else if (data.status === "open_wrong") {
            // Специальный статус для открытых вопросов: Gemma 3 объясняет ошибку
            await typeWriter(`\n[ CHYBA ] Анализ ИИ:\n${data.explanation}`, "#ff3333", "pre-wrap");
            // ПОКАЗЫВАЕМ СЛЕДУЮЩИЙ ВОПРОС (он пришел в данных)
            currentQType = data.type;
            const q = data.data;
            let msg = `\n------------------------------------------\n\n[ OTÁZKA ${data.progress}/10 ]\n${q.q}\n`;
            if (currentQType === "quiz") {
                msg += `\n A) ${q.a}\n B) ${q.b}\n C) ${q.c}\n\n> Vaše volba:`;
            } else {
                msg += `\n> Napište Vaši odpověď:`;
            }
            await typeWriter(msg, 'inherit', "pre-wrap");
        }
        
        else if (data.status === "boss_fight") {
            bossUi.style.display = 'block';
            startBossFight();
        }
        
        else if (data.status === "win") {
            await typeWriter(`\n[ ACCESS GRANTED ] SYSTEM HACKNUT!\nFinaльный Анализ и Конспект:\n`, "#00ff41", "pre-wrap");
            await typeWriter(data.analysis, 'inherit', "pre-wrap");
            gameStarted = false; // Конец игры
        }

    } catch (err) {
        console.error(err);
        loading.innerHTML = "[ CRITICAL_ERROR ]: Spojení přerušeno.";
    } finally {
        input.disabled = false;
        btn.disabled = false;
        input.focus();
        output.scrollTop = output.scrollHeight;
    }
}

// Переменные для Boss Fight
let currentQType = "quiz"; 

function startBossFight() {
    bossModeActive = true; // Блокировка ввода
    input.disabled = true;
    
    let wins = 0;
    const target = document.getElementById('target-char');
    const progress = document.getElementById('boss-progress');
    
    //ASCII ДРАКОН - Твое требование выполнено!
    const dragonArt = `
░░░░░░▀█▄░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
▀▄▄░░░░░▀▀███▄▄▄░░░░░░░░░░░░░░░░░░░░░░
░░▀▀██▄▄▄▄░░░▀▀▀██▄▄░░░░░░░░░░░░░░░░░░
░░░░░░▀▀▀███▄▄░░░▀▀░▄▄▄▄░░░░░░░░░░░░░░
░░░░░░░░░░▄█████████▀░░▀█░░░░░░░░░░░░░
░░░░░░░░░▀█░░▀███▀░░░░░░▀█▄▄░░░░░░░░░░
░░░░░▄█████░░░░░░░░░░░░░░░▀▀█░░░░░░░░░
░░░░░░██▄░░░▀▀██░░░░░░░░░░░░██░░░░░░░░
░░▄▄█▀▀▀▀░░░░▄░░░░░░░░▀▀██░░▀█▄░░░░░░░
░░▄▄██░░░░░▀▀▀▀░░░░░░░░░░░░░░░▀█▄░░▄░░
░██▀▀▀░░░░░░░▄░░░░░░░██▀▀█▄▄░░░▀████░░
░█▀░░░░░░░░▄▀▀░░░░░░░▀█▄░░▀██▄░░░▀▀█▄░
░█▄░░░░░░░░░░░░░░░░░░░░█▄░░▀▀██▄░░░░██
░░█▄░░░░░░░░░░░░██▀█▄░░▀██░░░░▄██▄░░█▀
░░░█▄░░░░░░░░░▄█▀░░░▀█▄░▀██▄▄░░░▄███▀░
░░░░▀█▄░░░░░░░█▀░░░░░░▀█▄░▀▀█▄░░░░░░░░
░░░░░░▀██▄▄▄░▄█░░░░░░░░░████▀░░░░░░░░░
░░░░░░░░░░▀▀▀▀▀░░░░░░░░░░░░░░░░░░░░░░░`;
    
    // Вставляем дракона в Boss UI
    const dragonContainer = document.getElementById('dragon-container');
    dragonContainer.innerText = dragonArt;

    function nextChar() {
        if (wins >= 5) {
            bossUi.style.display = 'none';
            bossModeActive = false; // Разблокировка
            input.disabled = false;
            
            // Скрытый запрос на сервер для сброса ошибок
            fetch('/api/boss_success', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                // БЕЗ перезагрузки. Просто сообщение и ждем ввода.
                typeWriter("\n[ BOSS DEFEATED ]: Přístup obnoven. Vaše mezery v obraně byly opraveny. Pokračujte...", "#ffff00", "pre-wrap");
            });
            return;
        }
        const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        const randomChar = chars[Math.floor(Math.random() * chars.length)];
        target.innerText = randomChar;
    }

    // Обработка нажатий клавиш только в режиме босса
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

// Уведомление о файле
fileInput.onchange = () => {
    if (fileInput.files.length > 0) {
        const info = document.createElement('div');
        info.innerHTML = `\n[ INFO ]: Soubor ${fileInput.files[0].name} připraven k RAG analýзе.`;
        info.style.color = "#00ff41";
        output.appendChild(info);
        output.scrollTop = output.scrollHeight;
    }
};
