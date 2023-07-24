function randomize(collection) {
    var randomNumber = Math.floor(Math.random() * collection.length);
    return collection[randomNumber];
}

function confetti() {
    $(".confetti").remove();
    var $confettiItems = $('<div class="confetti"></div>'),
        colors = ["#3b5692", "#f9c70b", "#00abed", "#ea6747"],
        height = 6.6,
        width = 6.6;

    var scale, $confettiItem;

    for (var i = 0; i < 350; i++) {
        scale = Math.random() * 1.75 + 1;
        $confettiItem = $(
            "<svg class='confetti-item' width='" +
            width * scale +
            "' height='" +
            height * scale +
            "' viewbox='0 0 " +
            width +
            " " +
            height +
            "'>\n  <use transform='rotate(" +
            Math.random() * 360 +
            ", " +
            width / 2 +
            ", " +
            height / 2 +
            ")' xlink:href='#svg-confetti' />\n</svg>"
        );
        $confettiItem.css({
            animation:
                Math.random() +
                2 +
                "s " +
                Math.random() * 2 +
                "s confetti-fall ease-in both",
            color: randomize(colors),
            left: Math.random() * 100 + "vw"
        });
        $confettiItems.append($confettiItem);
    }
    $(".main-confetti").append($confettiItems);
}

$(document).ready(function () {
    confetti();
});
