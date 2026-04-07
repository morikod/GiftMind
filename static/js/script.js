let selectedTags = [];
let people = JSON.parse(localStorage.getItem('giftPeople')) || [];

// Při načtení stránky
window.onload = () => {
    renderPeopleList();
};

function toggleTag(el) {
    el.classList.toggle('active');
    const tag = el.innerText;
    if (selectedTags.includes(tag)) {
        selectedTags = selectedTags.filter(t => t !== tag);
    } else {
        selectedTags.push(tag);
    }
}

function createNewPerson() {
    // Vyčistit formulář
    document.getElementById('person-name').value = '';
    document.getElementById('budget').value = '';
    document.getElementById('desc').value = '';
    document.getElementById('results').innerHTML = '';
    
    // Vyčistit tagy
    selectedTags = [];
    document.querySelectorAll('.tag.active').forEach(el => el.classList.remove('active'));
    
    document.getElementById('current-person-name').innerText = "Nový člověk";
    document.getElementById('person-name').focus();
}

function saveCurrentPerson() {
    const name = document.getElementById('person-name').value || "Neznámý";
    
    // Zjistíme, jestli už ho máme
    const existingIndex = people.findIndex(p => p.name === name);
    const personData = {
        name: name,
        budget: document.getElementById('budget').value,
        desc: document.getElementById('desc').value,
        tags: [...selectedTags],
        occasion: document.getElementById('occasion').value
    };

    if (existingIndex >= 0) {
        people[existingIndex] = personData;
    } else {
        people.push(personData);
    }

    localStorage.setItem('giftPeople', JSON.stringify(people));
    renderPeopleList();
}

function renderPeopleList() {
    const list = document.getElementById('people-list');
    list.innerHTML = '';
    people.forEach((p, index) => {
        const li = document.createElement('li');
        li.className = 'person-item';
        li.innerText = p.name;
        li.onclick = () => loadPerson(index);
        list.appendChild(li);
    });
}

function loadPerson(index) {
    const p = people[index];
    document.getElementById('current-person-name').innerText = "Dárek pro: " + p.name;
    document.getElementById('person-name').value = p.name;
    document.getElementById('budget').value = p.budget || '';
    document.getElementById('desc').value = p.desc || '';
    document.getElementById('occasion').value = p.occasion || 'Narozeniny';
    
    // Obnovit tagy
    selectedTags = p.tags || [];
    document.querySelectorAll('.tag').forEach(el => {
        if (selectedTags.includes(el.innerText)) {
            el.classList.add('active');
        } else {
            el.classList.remove('active');
        }
    });
}

async function startMagic() {
    const btn = document.getElementById('magic-btn');
    const results = document.getElementById('results');
    
    // Uložit člověka před generováním
    saveCurrentPerson();

    btn.innerText = "HLEDÁM REÁLNÉ DÁRKY...";
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                tags: selectedTags,
                description: document.getElementById('desc').value,
                budget: document.getElementById('budget').value,
                occasion: document.getElementById('occasion').value
            })
        });
        
        const textData = await response.text(); // Bereme text, pokud by AI vrátila špatný JSON
        const data = JSON.parse(textData);
        
        results.innerHTML = '';
        if (data.gifts && data.gifts.length > 0) {
            data.gifts.forEach(gift => {
                results.innerHTML += `
                    <div class="gift-card">
                        <div class="price-tag">Cena: ${gift.price || 'Neznámá'}</div>
                        <h4>${gift.title}</h4>
                        <p>${gift.reason}</p>
                    </div>`;
            });
        } else {
            results.innerHTML = '<p>Systém nenašel dárky. Zkus změnit popis.</p>';
        }
    } catch (e) {
        console.error(e);
        alert("Chyba při komunikaci s AI. Zkontroluj logy.");
    } finally {
        btn.innerText = "NAJÍT DALŠÍ DÁREK";
        btn.disabled = false;
    }
}
