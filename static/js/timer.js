(function () {
    "use strict";

    var timer = document.getElementById("question-timer");
    var form = document.getElementById("game-form");
    if (!timer || !form) {
        return;
    }

    var output = document.getElementById("time-left");
    var timeoutInput = document.getElementById("timed-out");
    var remaining = Number.parseInt(timer.dataset.seconds, 10);
    var intervalId = null;
    var paused = false;

    function paint() {
        output.textContent = String(Math.max(remaining, 0));
        timer.classList.toggle("urgent", remaining <= 10);
    }

    function stop() {
        if (intervalId !== null) {
            window.clearInterval(intervalId);
            intervalId = null;
        }
    }

    function expire() {
        stop();
        timeoutInput.value = "yes";
        document.getElementById("submit-answer").disabled = true;
        form.submit();
    }

    function start() {
        stop();
        intervalId = window.setInterval(function () {
            if (paused) {
                return;
            }
            remaining -= 1;
            paint();
            if (remaining <= 0) {
                expire();
            }
        }, 1000);
    }

    var modal = document.getElementById("lifeline-modal");
    var openButton = document.getElementById("open-lifelines");
    var cancelButton = document.getElementById("cancel-lifeline");
    var confirmButton = document.getElementById("confirm-lifeline");
    var retainedTime = document.getElementById("time-left-after-lifeline");
    var lifelineForm = document.getElementById("lifeline-form");

    function openModal() {
        paused = true;
        modal.hidden = false;
        cancelButton.focus();
    }

    function closeModal() {
        modal.hidden = true;
        paused = false;
        openButton.focus();
    }

    if (openButton && modal) {
        openButton.addEventListener("click", openModal);
        cancelButton.addEventListener("click", closeModal);
        modal.addEventListener("click", function (event) {
            if (event.target === modal) {
                closeModal();
            }
        });
        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && !modal.hidden) {
                closeModal();
            }
        });
        lifelineForm.addEventListener("submit", function () {
            retainedTime.value = String(remaining);
            window.setTimeout(function () {
                confirmButton.disabled = true;
            }, 0);
        });
    }

    form.addEventListener("submit", stop);
    paint();
    start();
}());
