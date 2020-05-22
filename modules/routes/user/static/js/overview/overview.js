$(document).ready(function () {

    // Blog overview date range init.
    $('#blog-overview-date-range').datepicker({});

    //
    // Small Stats

    const ERROR = "An error occurred.";

    function businessBalance() {
        let ref = $("#businessBalance");
        let loader = $("#businessBalanceLoading");
        let loaderText = $("#businessBalanceLoadingText");
        $.getJSON('/user/widgets/dash/current_business_balance/', function (data) {
            ref.text(data["available_balance"]);
            ref.removeClass("d-none");
            loader.remove();
        }).fail(function () {
            loaderText.text(ERROR);
        });
    }

    function departmentBalance() {
        let ref = $("#departmentBalance");
        let loader = $("#departmentBalanceLoading");
        let loaderText = $("#departmentBalanceLoadingText");
        $.getJSON('/user/widgets/dash/department_balance/', function (data) {
            ref.text(data["available_balance"]);
            ref.removeClass("d-none");
            loader.remove();
        }).fail(function () {
            loaderText.text(ERROR);
        });
    }

    function employeeCount() {
        let ref = $("#employeeCount");
        let loader = $("#employeeCountLoading");
        let loaderText = $("#employeeCountLoadingText");
        $.getJSON('/user/widgets/dash/department_employee_count/', function (data) {
            ref.text(data["amount"]);
            ref.removeClass("d-none");
            loader.remove();
        }).fail(function () {
            loaderText.text(ERROR);
        });
    }

    function outgoingTransactions() {
        let ref = $("#outgoingTransactions");
        let loader = $("#outgoingTransactionsLoading");
        let loaderText = $("#outgoingTransactionsText");
        $.getJSON('/user/widgets/dash/current_outgoing_transactions/', function (data) {
            ref.text(data["number_transactions"]);
            ref.removeClass("d-none");
            loader.remove();
        }).fail(function () {
            loaderText.text(ERROR);
        });
    }

    function activePlans() {
        let ref = $("#activePlans");
        let loader = $("#activePlansLoading");
        let loaderText = $("#activePlansText");
        $.getJSON('/user/widgets/dash/active_plans/', function (data) {
            ref.text(data["total"]);
            ref.removeClass("d-none");
            loader.remove();
        }).fail(function () {
            loaderText.text(ERROR);
        });
    }

    businessBalance();
    departmentBalance();
    employeeCount();
    outgoingTransactions();
    activePlans();

    //
    // Blog Overview Users
    //

    var bouCtx = document.getElementsByClassName('blog-overview-users')[0];

    // Data
    var bouData = {
        // Generate the days labels on the X axis.
        labels: Array.from(new Array(30), function (_, i) {
            return i === 0 ? 1 : i;
        }),
        datasets: [{
            label: 'Current Month',
            fill: 'start',
            data: [500, 800, 320, 180, 240, 320, 230, 650, 590, 1200, 750, 940, 1420, 1200, 960, 1450, 1820, 2800, 2102, 1920, 3920, 3202, 3140, 2800, 3200, 3200, 3400, 2910, 3100, 4250],
            backgroundColor: 'rgba(0,123,255,0.1)',
            borderColor: 'rgba(0,123,255,1)',
            pointBackgroundColor: '#ffffff',
            pointHoverBackgroundColor: 'rgb(0,123,255)',
            borderWidth: 1.5,
            pointRadius: 0,
            pointHoverRadius: 3
        }, {
            label: 'Past Month',
            fill: 'start',
            data: [380, 430, 120, 230, 410, 740, 472, 219, 391, 229, 400, 203, 301, 380, 291, 620, 700, 300, 630, 402, 320, 380, 289, 410, 300, 530, 630, 720, 780, 1200],
            backgroundColor: 'rgba(255,65,105,0.1)',
            borderColor: 'rgba(255,65,105,1)',
            pointBackgroundColor: '#ffffff',
            pointHoverBackgroundColor: 'rgba(255,65,105,1)',
            borderDash: [3, 3],
            borderWidth: 1,
            pointRadius: 0,
            pointHoverRadius: 2,
            pointBorderColor: 'rgba(255,65,105,1)'
        }]
    };

    // Options
    var bouOptions = {
        responsive: true,
        legend: {
            position: 'top'
        },
        elements: {
            line: {
                // A higher value makes the line look skewed at this ratio.
                tension: 0.3
            },
            point: {
                radius: 0
            }
        },
        scales: {
            xAxes: [{
                gridLines: false,
                ticks: {
                    callback: function (tick, index) {
                        // Jump every 7 values on the X axis labels to avoid clutter.
                        return index % 7 !== 0 ? '' : tick;
                    }
                }
            }],
            yAxes: [{
                ticks: {
                    suggestedMax: 45,
                    callback: function (tick, index, ticks) {
                        if (tick === 0) {
                            return tick;
                        }
                        // Format the amounts using Ks for thousands.
                        return tick > 999 ? (tick / 1000).toFixed(1) + 'K' : tick;
                    }
                }
            }]
        },
        // Uncomment the next lines in order to disable the animations.
        // animation: {
        //   duration: 0
        // },
        hover: {
            mode: 'nearest',
            intersect: false
        },
        tooltips: {
            custom: false,
            mode: 'nearest',
            intersect: false
        }
    };

    // Generate the Analytics Overview chart.
    window.BlogOverviewUsers = new Chart(bouCtx, {
        type: 'LineWithLine',
        data: bouData,
        options: bouOptions
    });

    // Hide initially the first and last analytics overview chart points.
    // They can still be triggered on hover.
    var aocMeta = BlogOverviewUsers.getDatasetMeta(0);
    aocMeta.data[0]._model.radius = 0;
    aocMeta.data[bouData.datasets[0].data.length - 1]._model.radius = 0;

    // Render the chart.
    window.BlogOverviewUsers.render();


    //
    // Plan avg line graph
    //

    var planDepartment = undefined;
    var xyData = [];
    var xyDataLabels = [];
    $.getJSON('/user/widgets/dash/plan_avg_six_months/', function (data, status, xhr) {
        xyDataLabels = Object.keys(data['data']);
        planDepartment = data['department'];
        $.each(data['data'], function (key, val) {
            console.log(key, val);
            let point = {};
            point["x"] = key;
            point["y"] = val['avg'];
            xyData.push(point)
        });
        $("#planAvgSixMonthsLoading").remove();
        loadAvgData();
    }).fail(function () {
        let ref = $("planAvgSixMonthsLoadingText");
        ref.text(ERROR);
        ref.prev().remove()
    });

    console.info("XYDATA", xyData);

    function loadAvgData() {
        var config = {
            type: 'line',
            data: {
                labels: xyDataLabels,
                datasets: [{
                    label: `${planDepartment} Plans`,
                    backgroundColor: "rgba(103, 58, 183, 1)",
                    borderColor: "rgba(139,69,230,0.76)",
                    data: xyData,
                    fill: false,
                }]
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: 'Plan Average Overview'
                },
                tooltips: {
                    mode: 'index',
                    intersect: false,
                },
                hover: {
                    mode: 'nearest',
                    intersect: true
                },
                scales: {
                    xAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: 'Month'
                        }
                    }],
                    yAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: 'Amount'
                        }
                    }]
                }
            }
        };

        window.planOverview = new Chart($("#planAvgSixMonths")[0], config);
    }

    //
    // Department Allocation Pie Chart
    //

    const deptList = [];
    const amountList = [];
    $.getJSON('/user/widgets/dash/department_allocation/', function (data, status, xhr) {
        $.each(data, function (key, val) {
            deptList.push(key.replace(/^\w/, c => c.toUpperCase()));
            amountList.push(parseFloat(val));
        });
        $("#deptAllocLoading").remove();
        setDepartmentOptions(deptList, amountList, $("#deptAllocFunds")[0]);
    });

    const deptUtilizationList = [];
    const utilizationList = [];
    $.getJSON('/user/widgets/dash/department_utilization/', function (data, status, xhr) {
        $.each(data, function (key, val) {
            deptUtilizationList.push(key.replace(/^\w/, c => c.toUpperCase()));
            utilizationList.push(parseFloat(val));
        });
        $("#deptUtilizationLoading").addClass("d-none");
        setDepartmentOptions(deptUtilizationList, utilizationList, $("#deptUtilization")[0]);
    });

    const ubdOptions = {
        legend: {
            position: 'bottom',
            labels: {
                padding: 20,
                boxWidth: 15
            }
        },
        cutoutPercentage: 0,
        // Uncomment the following line in order to disable the animations.
        // animation: false,
        tooltips: {
            custom: false,
            mode: 'index',
            position: 'nearest'
        }
    };

    function setDepartmentOptions(departmentList, amountList, chartCanvasSelection) {
        console.log(departmentList);
        console.log(amountList);

        let backgroundColor = [];
        let alphaBase = departmentList.length * 0.15;
        for (let i = 0; i < departmentList.length; i++) {
            backgroundColor.push(`rgba(94,23,235,${alphaBase})`);
            alphaBase /= 1.3
        }

        // Data
        const ubdData = {
            datasets: [{
                hoverBorderColor: '#ffffff',
                data: amountList,
                backgroundColor: backgroundColor
            }],
            labels: departmentList
        };

        // Generate the users by device chart.
        window.ubdChart = new Chart(chartCanvasSelection, {
            type: 'pie',
            data: ubdData,
            options: ubdOptions
        });
    }

    //
    // EMPLOYEE SPENDING
    //
    const table = $('#spendingTable').DataTable({
        paging: false,
        info: false,
        searching: false,
        scrollY: "400px",
        scrollCollapse: true,
        responsive: true,
        "initComplete": function (settings, json) {
            loadSpending();
        }
    });


    function loadSpending() {
        $.getJSON('/user/widgets/dash/department_employee__monthly_spending/', function (data, status, xhr) {
            $("#monthlySpendingLoading").remove();
            $.each(data, function (index, value) {
                table.row.add([
                    value["id"],
                    value['name'].toUpperCase(),
                    value['gpa_bal'],
                    value['monthly_spending']
                ]).draw();
            })

        }).fail(function () {
            let ref = $("#monthlySpendingLoadingText");
            ref.prev().remove();
            table.row.add([ERROR])
        });

    }
});

