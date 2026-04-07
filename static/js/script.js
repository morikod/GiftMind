let selectedTags = [];

function toggleTag(el) {
    el.classList.toggle('active');
    const tag = el.innerText;
    if (selectedTags.includes(tag)) {
        selectedTags = selectedTags.filter(t => t !== tag);
    } else {
        selectedTags.push(tag);
    }
}

async function startMagic() {
    const btn = document.getElementById('magic-btn');
    const results = document.getElementById('results');
    btn.innerText = "Architekt přemýšlí...";
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                tags: selectedTags,
                description: document.getElementById('desc').value
            })
        });
        const data = await response.json();
        results.innerHTML = '';
        data.gifts.forEach(gift => {
            results.innerHTML += `
                <div class="gift-card">
                    <div class="vibe">${gift.vibe}</div>
                    <h4>${gift.title}</h4>
                    <p>${gift.reason}</p>
                </div>`;
        });
    } catch (e) {
        alert("Chyba v matrixu.");
    } finally {
        btn.innerText = "GENEROVAT DALŠÍ";
    }
}
