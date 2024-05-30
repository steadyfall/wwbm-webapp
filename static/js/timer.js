function setNewDate() {
    newDate = new Date().getTime() + countDownSec * 1000;
    localStorage.setItem('newDate', newDate);
};
function setDifference() {
    difference = newDate - new Date().getTime();
    localStorage.setItem('difference', difference);
};

let x;
let newDate;
let difference;
let countDownSec;
let paused;
let timeLeft;

timeLeft = document.getElementById("time-left");

countDownSec = parseInt(timeLeft.textContent);
++countDownSec;
paused = false;

function pause() {
    if (!paused) {
        countDownSec = parseInt(difference / 1000);
        ++countDownSec;
    }
    localStorage.clear();
    timeLeft.innerHTML = countDownSec;
    paused = !paused;
    // console.log(paused, 'lmao', countDownSec);
    var startBack = paused ? clearInterval(x) : startTimer();
}

function timeUpdate() {
    var newDate = localStorage.getItem('newDate');
    if (!newDate) { setNewDate(); }
    var difference = localStorage.getItem('difference')
    if (!difference) { setDifference(); }

    if (newDate - new Date().getTime() <= 0) {
        localStorage.clear();
        setNewDate();
        setDifference();
        timeLeft.innerHTML = countDownSec;
    } else {
        timeLeft.innerHTML = Math.floor((newDate - new Date().getTime()) / 1000);
    }
}

function checker() {
    difference = newDate - new Date().getTime();
    // console.log(difference);
    if (difference < 10) {
        $('#sendAnswer').click();
        // document.getElementById("newform").submit()
    }
    var seconds = Math.floor(difference / 1000);
    // console.log(seconds);
    if (timeLeft.innerHTML <= 10) {
        timeLeft.style.color = 'red';
    } else {
        timeLeft.style.color = 'white';
    }
    timeLeft.innerHTML = seconds;
}

function startTimer() {
    // console.log(countDownSec);
    timeUpdate();
    x = setInterval(checker, 1000);
}


if (!paused) {
    startTimer();
}

$('#lifelineButton').on('click', pause);
$('#sendAnswer').on("click submit", function submitChecker(e) {
    if (!paused) {
        pause();
    }
    var arr = [];
    var common = "#option_";
    for (i = 0; i <= 3; i++) {
        var newcommon = (' ' + common).slice(1) + String.fromCharCode(97+i);
        arr[i] = newcommon;
    }
    var option = arr.some(o => $(o).is(":checked"));
    if (!option) {
        for (i = 0; i <= arr.length - 1; i++) {
            if (~($(arr[i]).is(":checked"))) {
                $(arr[i]).attr('checked', true);
                break;
            }
        }
        // console.log(arr);
        // e.preventDefault();
    }
});

$('#confirmLifeline').on("click", function (e) {
    $('#timeLeftAfterLifeline').val(parseInt(timeLeft.textContent));
    e.attr('disabled', true);
});

$('#closeLifeline').on("click", function () {
    $('#lifelineButton').attr('disabled', true);
    pause();
});
