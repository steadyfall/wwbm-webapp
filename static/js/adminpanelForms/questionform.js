var whoAddedConfig = (allOptions) => {
    return {
        plugins: {
            'remove_button': {
                title: 'Remove this user.',
            },
            'no_backspace_delete': {},
        },
        maxItems: 1,
        items: allOptions,
        maxOptions: 10,
        openOnFocus: false,
        placeholder: "Who added this question?",
        create: false,
        highlight: true
    }
};
var fallsUnderConfig = (allOptions) => {
    return {
        plugins: {
            'remove_button': {
                title: 'Remove this category.',
            },
            'no_backspace_delete': {},
        },
        maxItems: null,
        items: allOptions,
        maxOptions: 10,
        openOnFocus: false,
        placeholder: "Choose the categories.",
        create: false,
        highlight: true
    }
};
var questionTypeConfig = (allOptions) => {
    return {
        plugins: {
            'remove_button': {
                title: 'Remove this type.',
            },
            'no_backspace_delete': {},
        },
        maxItems: 1,
        items: allOptions,
        maxOptions: 10,
        openOnFocus: false,
        placeholder: "Which type is the given question?",
        create: false,
        highlight: true
    }
};
var difficultyConfig = (allOptions) => {
    return {
        plugins: {
            'remove_button': {
                title: 'Remove this difficulty.',
            },
            'no_backspace_delete': {},
        },
        maxItems: 1,
        items: allOptions,
        maxOptions: 10,
        openOnFocus: false,
        placeholder: "What difficulty is this question?",
        create: false,
        highlight: true
    }
};
var correctOptionConfig = (allOptions) => {
    return {
        plugins: {
            'remove_button': {
                title: 'Remove this option.',
            },
            'no_backspace_delete': {},
        },
        maxItems: 1,
        items: allOptions,
        maxOptions: 60,
        openOnFocus: false,
        placeholder: "Choose a correct option.",
        create: false,
        highlight: true
    }
};
var incorrectOptionConfig = (allOptions) => {
    return {
        plugins: {
            'remove_button': {
                title: 'Remove this option.',
            },
            'no_backspace_delete': {},
            'input_autogrow': {},
        },
        maxItems: 3,
        items: allOptions,
        maxOptions: 95,
        openOnFocus: false,
        placeholder: "Choose incorrect options.",
        create: false,
        highlight: true
    }
};
const dateAddedConfig = {
    enableTime: true,
    dateFormat: "Y-m-dTH:i",
    time_24hr: true,
};
export { whoAddedConfig, fallsUnderConfig, correctOptionConfig, incorrectOptionConfig, questionTypeConfig, difficultyConfig, dateAddedConfig };
