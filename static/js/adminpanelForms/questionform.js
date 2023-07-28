new TomSelect('#who_added', {
    plugins: {
        'remove_button': {
            title: 'Remove this option.',
        },
        'no_backspace_delete': {},
    },
    maxItems: 1,
    items: [],
    maxOptions: 10,
    openOnFocus: false,
    placeholder: "Who added this question?",
    create: false,
    highlight: true
});
new TomSelect('#falls_under', {
    plugins: {
        'remove_button': {
            title: 'Remove this category.',
        },
        'no_backspace_delete': {},
    },
    maxItems: null,
    items: [],
    maxOptions: 10,
    openOnFocus: false,
    placeholder: "Choose the categories.",
    create: false,
    highlight: true
});
new TomSelect('#correct_option', {
    plugins: {
        'remove_button': {
            title: 'Remove this option.',
        },
        'no_backspace_delete': {},
    },
    maxItems: 1,
    items: [],
    maxOptions: 60,
    openOnFocus: false,
    placeholder: "Choose a correct option.",
    create: false,
    highlight: true
});
new TomSelect('#incorrect_options', {
    plugins: {
        'remove_button': {
            title: 'Remove this option.',
        },
        'no_backspace_delete': {},
        'input_autogrow': {},
    },
    maxItems: 3,
    items: [],
    maxOptions: 95,
    openOnFocus: false,
    placeholder: "Choose incorrect options.",
    create: false,
    highlight: true
});
new flatpickr("#date_added", {
    enableTime: true,
    dateFormat: "Y-m-d h:i K",
    time_24hr: false,
});
$(document).ready(function () {
    $(window).keydown(function (event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            return false;
        }
    });
});