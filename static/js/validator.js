function nothingWritten(e) {
    e.style.borderColor = '#86b7fe';
    e.style.boxShadow = 'inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 8px rgba(20, 71, 208, 0.6)';
}

function validWritten(e) {
    e.style.borderColor = '#00FF00';
    e.style.boxShadow = 'inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 8px rgba(0, 255, 0, 0.6)';
}

function invalidWritten(e) {
    e.style.borderColor = '#FF0000';
    e.style.boxShadow = 'inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 8px rgba(255, 0, 0, 0.6)';
}

function usernameRegex(uname) {
    const regex = /^[\w.@+-]{1,149}$/;
    var isValid = regex.test(uname);
    return isValid;
}

function emailRegex(email) {
    const emailReg = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    var isValid = emailReg.test(email);
    return isValid;
}

function passwordRegex(pwd) {
    const notNumericPasswordRegex = /^.*\D.*$/;
    var username = document.getElementById('usernameInput').value.toLowerCase();
    // console.log(username);
    var isValid = (pwd.length >= 8) && (notNumericPasswordRegex.test(pwd)) && (username && (pwd.indexOf(username) === -1));
    /* console.log("pwd: ", pwd, "| >= 8:", (pwd.length >= 8), 
                "| all not numbers:", (~notNumericPasswordRegex.test(pwd)), 
                "| username:", username, 
                "| username not in password:", (pwd.indexOf(username) === -1), 
                "| result:",isValid); */
    return isValid;
}

function password2Regex(pwd) {
    var password = document.getElementById('passwordInput').value;
    // console.log(username);
    var isValid = (password && (pwd === password) && passwordRegex(pwd));
    // console.log(password, pwd, (pwd === password));
    return isValid;
}

function validOrInvalidPic(isValid, parent) {
    var status = '';
    var children = [].slice.call(parent.getElementsByTagName('*'), 0);
    // console.log(children);

    var childrenArray = new Array(children.length);
    var arrayLength = childrenArray.length;
    for (var i = 0; i < arrayLength; i++) {
        var classes = children[i].getAttribute("class");
        if ((classes !== null) && (~classes.indexOf("col-auto"))) {
            if (isValid) {
                status = '<div class="valid p-3 mx-auto"></div>';
            } else {
                status = '<div class="invalid p-3 mx-auto"></div>';
            }
            children[i].innerHTML = status;
            return children[i];
        }
    }
}

function inputValid(e, isValid) {
    validOrInvalidPic(isValid, e.parentNode.parentNode.parentNode);
    if (e.value.length === 0) {
        nothingWritten(e);
        return 1;
    }
    if (isValid) {
        validWritten(e);
    } else {
        invalidWritten(e);
    }
    return isValid;
}

$('#usernameInput').on("input focus keyup click change", function () {
    var isValid = usernameRegex(this.value);
    // console.log(isValid);
    return inputValid(this, isValid);
});


$('#emailInput').on("input focus keyup click change", function () {
    var isValid = emailRegex(this.value);
    // console.log(isValid);
    return inputValid(this, isValid);
});

$('#usernameInput, #passwordInput, #password2Input').on("input click change focus keyup", function () {
    var pwd = document.getElementById('passwordInput');
    var pwd2 = document.getElementById('password2Input');
    var passwordIsValid = passwordRegex(pwd.value);
    var password2IsValid = password2Regex(pwd2.value);
    // console.log(passwordIsValid, password2IsValid)
    inputValid(pwd, passwordIsValid);
    inputValid(pwd2, password2IsValid);
    return 1;
});

$('#submitButton').on('click', function (e) {
    var ul = document.getElementById("allAlerts");
    var uname = document.getElementById('usernameInput');
    var email = document.getElementById('emailInput');
    var pwd = document.getElementById('passwordInput');
    var pwd2 = document.getElementById('password2Input');
    var isValid = inputValid(uname, usernameRegex(uname.value)) && inputValid(email, emailRegex(email.value)) &&
        inputValid(pwd, passwordRegex(pwd.value)) && inputValid(pwd2, password2Regex(pwd2.value));
    if (!isValid) {
        e.preventDefault(); //prevent the default action
        var warning = '<li class="alert alert-danger">Modify before submitting.</li>';
        if (ul.innerHTML.indexOf(warning) === -1) {
            ul.innerHTML += warning;
        }
    }
});