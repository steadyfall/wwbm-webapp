function setNewDate() {
    newDate = new Date().getTime() + countDownmicsec;
    localStorage.setItem('newDate', newDate);
};
function setDifference() {
    difference = newDate - new Date().getTime();
    localStorage.setItem('difference', difference);
};

var timeLeft = document.getElementById("time-left");

var countDownSec = 20;
var countDownmicsec = countDownSec * 1000;

var newDate = localStorage.getItem('newDate');
if (!newDate) {setNewDate();}
var difference = localStorage.getItem('difference')
if (!difference) {setDifference();}

if (newDate - new Date().getTime() <= 0) {
    localStorage.clear();
    setNewDate();
    setDifference();
    timeLeft.innerHTML = countDownSec;
} else {
    timeLeft.innerHTML = Math.floor((newDate - new Date().getTime()) / 1000);
}

var x = setInterval(function () {
    difference = newDate - new Date().getTime();
    console.log(difference);
    if (difference < 10) {
        window.location.href = 'https://www.encodedna.com/javascript/operators/default.htm';
        // document.getElementById("newform").submit()
    }
    var seconds = Math.floor(difference / 1000);
    // console.log(seconds);
    timeLeft = document.getElementById("time-left");
    if (timeLeft.innerHTML <= 10) {
        timeLeft.style.color = 'red';
    }
    timeLeft.innerHTML = seconds;
    }, 1000);