async function done() {
    let name = document.getElementById('name').value;
    let fullname = document.getElementById('fullname').value;
    let sex = document.getElementById('sex').value;
    let age = document.getElementById('age').value;
    let pron = document.getElementById('pron').value;

    if (name == '' || fullname == '') return;

    let response = await fetch(
        'http://localhost:5050/',
        {
            method: 'POST',
            body: JSON.stringify({
                action: 'config',
                payload: {
                    name: name,
                    fullname: fullname,
                    sex: sex,
                    age: age,
                    pron: pron
                }
            })
        }
    )

    window.location = '/AikoSetupDone';
}