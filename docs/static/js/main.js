/* add table functionality */
var dataTable = new DataTable("#grantsTable", {
    layout: {
        top: "{info}{search}",
        bottom: "{pager}"
    },
    labels: {
        placeholder: "Search grants…",
        perPage: "{select} grants per page",
        noRows: "No grants found",
        info: "Showing {start} to {end} of {rows} grants",
    }
});

/* set chart styling */
Chart.defaults.global.defaultFontSize = '18';
Chart.defaults.global.defaultFontFamily = '"Roboto", sans-serif';

/* create chart */
var ctx = document.getElementById('overtimechart').getContext('2d');
const cumulativeSum = (sum => value => sum += value)(0);
amountAwardedCumulative = Object.values(amountByDate).map(v => v.amount).map(cumulativeSum);
amountAwardedDates = Object.keys(amountByDate).map(v => new Date(v));

var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: amountAwardedDates,
        datasets: [{
            label: 'Grant amount',
            data: amountAwardedDates.map((k, i) => ({ x: k, y: amountAwardedCumulative[i] })),
            backgroundColor: '#bc2c26',
            borderColor: '#bc2c26',
            borderWidth: 1,
            pointRadius: 0,
            lineTension: 0,
            steppedLine: true,
        }]
    },
    options: {
        legend: {
            display: false
        },
        scales: {
            xAxes: [{
                type: 'time',
                ticks: {
                    maxTicksLimit: 5,
                },
                time: {
                    unit: 'day',
                },
                gridLines: {
                    display: false
                }
            }],
            yAxes: [{
                ticks: {
                    beginAtZero: true
                },
                gridLines: {
                    display: false
                },
                ticks: {
                    maxTicksLimit: 5,
                    callback: function (value, index, values) {
                        return "£" + value.toLocaleString();
                    }
                }
            }]
        }
    }
});