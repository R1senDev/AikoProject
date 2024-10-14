async function done() {
    let response = await fetch(
        'http://localhost:5050',
        {
            method: 'POST',
            data: JSON.stringify({
                action: 'activate'
            })
        }
    )
}