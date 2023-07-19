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

$('#usernameInput').on("input focus keyup", function () {
    var isValid = usernameRegex(this.value);
    // console.log(isValid);

    validOrInvalidPic(isValid, this.parentNode.parentNode.parentNode);
    if (this.value.length === 0) {
        nothingWritten(this);
        return 1;
    }
    if (isValid) {
        validWritten(this);
    } else {
        invalidWritten(this);
    }
    return isValid;
});


$('#emailInput').on("input focus keyup", function () {
    var isValid = emailRegex(this.value);
    // console.log(isValid);

    validOrInvalidPic(isValid, this.parentNode.parentNode.parentNode);
    if (this.value.length === 0) {
        nothingWritten(this);
        return 1;
    }
    if (isValid) {
        validWritten(this);
    } else {
        invalidWritten(this);
    }
    return isValid;
});


$('#passwordInput').on("input focus keyup", function () {
    const numericPasswordRegex = /^(\d+)$/;
    var username = document.getElementById('usernameInput').value;
    // console.log(username);
    var isValid = (this.value.length >= 8) && (~numericPasswordRegex.test(this.value)) && (username && (this.value.indexOf(username) === -1));
    /* console.log("pwd: ", this.value, "| >= 8:", (this.value.length >= 8), 
                "| all not numbers:", (~numericPasswordRegex.test(this.value)), 
                "| username:", username, 
                "| username not in password:", (this.value.indexOf(username) === -1), 
                "| result:",isValid); */

    validOrInvalidPic(isValid, this.parentNode.parentNode.parentNode);
    if (this.value.length === 0) {
        nothingWritten(this);
        return 1;
    }
    if (isValid) {
        validWritten(this);
    } else {
        invalidWritten(this);
    }
    return isValid;
});

$('#password2Input').on("input focus keyup", function () {
    var password = document.getElementById('passwordInput').value;
    // console.log(username);
    var isValid = (password && (this.value === password));
    /* console.log("pwd: ", this.value, "| >= 8:", (this.value.length >= 8), 
                "| all not numbers:", (~numericPasswordRegex.test(this.value)), 
                "| username:", username, 
                "| username not in password:", (this.value.indexOf(username) === -1), 
                "| result:",isValid); */

    validOrInvalidPic(isValid, this.parentNode.parentNode.parentNode);
    if (this.value.length === 0) {
        nothingWritten(this);
        return 1;
    }
    if (isValid) {
        validWritten(this);
    } else {
        invalidWritten(this);
    }
    return isValid;
});