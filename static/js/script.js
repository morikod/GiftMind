let currentProfile = null;
let selectedTags = [];

const allTags = ["hry","anime","sport","hudba","filmy","technologie","fitness","cestování","auta","meme","programování"];

function initTags(){
    const container = document.getElementById('tagContainer');
    allTags.forEach(tag=>{
        const btn = document.createElement('button');
        btn.innerText = tag;
        btn.onclick = ()=>{
            btn.classList.toggle('active');
            if(selectedTags.includes(tag)){
                selectedTags = selectedTags.filter(t=>t!==tag);
            } else {
                selectedTags.push(tag);
            }
        }
        container.appendChild(btn);
    })
}

function typeText(text, el){
    let i = 0;
    const interval = setInterval(()=>{
        el.innerHTML += text[i];
        i++;
        if(i>=text.length) clearInterval(interval);
    }, 25);
}

function openForm(){
    document.getElementById('form').classList.remove('hidden');
}

function createProfile(){
    const data = {
        name: document.getElementById('name').value,
        tags: selectedTags.join(','),
        desc: document.getElementById('desc').value,
        budget: document.getElementById('budget').value,
        reason: document.getElementById('reason').value
    }

    fetch('/create_profile',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify(data)
    }).then(()=>{
        loadProfiles();
        document.getElementById('form').classList.add('hidden');
    })
}

function loadProfiles(){
    fetch('/get_profiles')
}
