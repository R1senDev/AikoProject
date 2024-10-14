const chatbox = document.getElementById('chatbox');
const sentT = chatbox.firstElementChild.cloneNode(true);
const recvT = chatbox.lastElementChild.cloneNode(true);


while (chatbox.hasChildNodes()) chatbox.firstChild.remove();


async function send() {
    let promptInput = document.getElementById('promptInput');
    let prompt = promptInput.value;
    promptInput.value = '';

    let newChild = sentT.cloneNode(true);
    newChild.lastElementChild.innerHTML = prompt;
    chatbox.appendChild(newChild);

    let response = await fetch(
        'http://localhost:5050/',
        {
            method: 'POST',
            body: JSON.stringify({
                action: 'prompt',
                payload: prompt
            })
        }
    );

    console.log('GOT IT!');
    let answer = await response.text();

    newChild = recvT.cloneNode(true);
    newChild.lastElementChild.innerHTML = answer;
    chatbox.appendChild(newChild);
}