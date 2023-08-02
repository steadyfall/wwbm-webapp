var config_sessions = (date_list, session_list) => {
    return {
        type: 'line',
        data: {
            labels: date_list,
            datasets: [
                {
                    data: session_list,
                    backgroundColor: '#ffffff'
                }
            ]
        },
        options: {
            responsive: false,
            legend: {
                display: false
            },
            elements: {
                line: {
                    borderColor: '#2986cc',
                    borderWidth: 2
                },
                point: {
                    radius: 0
                }
            },
            tooltips: {
                enabled: false
            },
            scales: {
                yAxes: [
                    {
                        display: false
                    }
                ],
                xAxes: [
                    {
                        display: false
                    }
                ]
            }
        }
    }
};

var config_scores = (date_list, score_list) => {
    return {
        type: 'line',
        data: {
            labels: date_list,
            datasets: [
                {
                    data: score_list,
                    backgroundColor: '#ffffff'
                }
            ]
        },
        options: {
            responsive: false,
            legend: {
                display: false
            },
            elements: {
                line: {
                    borderColor: '#0273b0',
                    borderWidth: 2
                },
                point: {
                    radius: 0
                }
            },
            tooltips: {
                enabled: false
            },
            scales: {
                yAxes: [
                    {
                        display: false
                    }
                ],
                xAxes: [
                    {
                        display: false
                    }
                ]
            }
        }
    }
};

var config_useractive = (active_users_labels, active_users_activity) => {
    return {
        type: 'line',
        data: {
            labels: active_users_labels,
            datasets: [{
                data: active_users_activity,
                backgroundColor: '#ffffff'
            }]
        },
        options: {
            responsive: false,
            legend: {
                display: false
            },
            elements: {
                line: {
                    borderColor: '#e69138',
                    borderWidth: 2
                },
                point: {
                    radius: 0
                }
            },
            tooltips: {
                enabled: false
            },
            scales: {
                yAxes: [
                    {
                        display: false
                    }
                ],
                xAxes: [
                    {
                        display: false
                    }
                ]
            }
        }
    }
};

const config_sessionsTotal = (date_list, session_list, session_user_list, session_easy_list, session_medium_list, session_hard_list) => {
    return {
        type: 'bar',
        data: {
            labels: date_list,
            datasets: [{
                label: 'Session Count',
                data: session_list,
                backgroundColor: '#b82e2e'
            }, {
                label: 'Users who played',
                data: session_user_list,
                backgroundColor: '#18c8db'
            }, {
                label: 'EASY questions asked',
                data: session_easy_list,
                backgroundColor: '#18c446'
            }, {
                label: 'MEDIUM questions asked',
                data: session_medium_list,
                backgroundColor: '#5318db'
            }, {
                label: 'HARD questions asked',
                data: session_hard_list,
                backgroundColor: '#db1883'
            }]
        },
        options: {
            responsive: false,
            legend: false,
            scales: {
                xAxes: [{
                    stacked: false // this should be set to make the bars stacked
                }],
                yAxes: [{
                    stacked: false // this also..
                }]
            },
            maintainAspectRatio: true,
        }
    }
};

export { config_useractive, config_sessions, config_scores, config_sessionsTotal };
