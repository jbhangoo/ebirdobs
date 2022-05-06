function addUser() {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        handle_add_response(this.responseText);
    };

    // Create parameter string
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const fullname = document.getElementById("fullname").value;
    const params = `username=${username}&pw=${password}&fullname=${fullname}`;

    xhttp.open("POST", "/useradd/");
    xhttp.send(JSON.stringify({'username':username, 'pw':password, 'fullname':fullname}));
}

function handle_add_response(content) {
    const selt = document.getElementById("status");
    if (content == 0) {
        selt.innerHTML = "Failed to add user";
    } else {
        selt.innerHTML = `Added user: ${content}`;
    }
}

function deleteUser() {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        handle_add_response(this.responseText);
    };

    // Create parameter string
    const userid = document.getElementById("userid").value;
    const params = `userid=${userid}`;

    xhttp.open("POST", "/userdel/");
    xhttp.send(params);
}

function handle_delete_response(content) {
    const output = JSON.parse(content);
}
