var countDownSec = 20;
var countDownmicsec = countDownSec * 1000;

// Get NOW
var now = new Date();
var newDate = now.getTime() + countDownmicsec;

var x = setInterval(function () {

    var now = new Date();
    // console.log(now.getTime());
    var difference = newDate - now.getTime();
    // console.log(difference);
    var seconds = Math.floor(difference / 1000);
    // console.log(seconds);
    var timeLeft = document.getElementById("time-left");
    if (timeLeft.innerHTML < 10) {
        timeLeft.style.color = 'red';
    }
    timeLeft.innerHTML = seconds;
    if (difference < 100) {
        window.location.href = 'https://www.encodedna.com/javascript/operators/default.htm';
        // document.getElementById("newform").submit()
    }

}, 1000);