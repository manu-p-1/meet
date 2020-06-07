$(document).ready(function () {

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

    var bouCtx = $('#overallEmployeeSpending')[0];
    getOverallEmployeeSpending();

    function getOverallEmployeeSpending() {
        let loader = $("#overallEmployeeSpendingLoading");
        let loaderText = $("#overallEmployeeSpendingText");

        $.getJSON('/user/widgets/dash/monthly_employee_spending/', function (dataReturned) {
            let prevMonthData = dataReturned['data']['previous_month'];
            let currentMonthData = dataReturned['data']['current_month'];

            const prevMonthKeys = Object.keys(prevMonthData);
            const overallSpendingDataPast = Object.values(prevMonthData);

            const currentMonthKeys = Object.keys(currentMonthData);
            const overallSpendingDataCurrent = Object.values(currentMonthData);

            const overallSpendingLabels = [...new Set([...prevMonthKeys, ...currentMonthKeys])];
            loader.remove();

            renderOverallEmployeeSpendingChart(overallSpendingLabels,
                overallSpendingDataCurrent,
                overallSpendingDataPast)
        }).fail(function () {
            loaderText.text(ERROR);
        });
    }

    function renderOverallEmployeeSpendingChart(labels, curr, past) {
        console.log("entered");
        // Data
        var bouData = {
            // Generate the days labels on the X axis.
            labels: labels,
            datasets: [{
                label: 'Current Month',
                fill: 'start',
                data: curr,
                backgroundColor: 'rgba(103,58,183,0.1)',
                borderColor: 'rgb(139,69,230)',
                pointBackgroundColor: '#ffffff',
                pointHoverBackgroundColor: 'rgb(139,69,230)',
                borderWidth: 1.5,
                pointRadius: 0,
                pointHoverRadius: 3
            }, {
                label: 'Past Month',
                fill: 'start',
                data: past,
                backgroundColor: 'rgba(33,150,243,0.1)',
                borderColor: 'rgb(33,150,243)',
                pointBackgroundColor: '#ffffff',
                pointHoverBackgroundColor: 'rgb(33,150,243)',
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
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Day of the Month'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Amount'
                    }
                }]
            },
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
        window.OverallEmployeeSpending = new Chart(bouCtx, {
            type: 'LineWithLine',
            data: bouData,
            options: bouOptions
        });

        // // Hide initially the first and last analytics overview chart points.
        // // They can still be triggered on hover.
        var aocMeta = OverallEmployeeSpending.getDatasetMeta(0);
        aocMeta.data[0]._model.radius = 0;
        aocMeta.data[bouData.datasets[0].data.length - 1]._model.radius = 0;

        // Render the chart.
        window.OverallEmployeeSpending.render();
    }

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
        searching: true,
        scrollY: "400px",
        scrollCollapse: true,
        responsive: true,
        dom: "<'myfilter'f><'mylength'l>t",
        "initComplete": function () {
            loadSpending();
        },
        "fnRowCallback": function(nRow) {
          $('td:eq(2)', nRow).addClass("gpa-balance text-success font-weight-bold");
          $('td:eq(3)', nRow).addClass("gpa-spending text-danger font-weight-bold");
        }
    });

    var buttons = new $.fn.dataTable.Buttons(table, {
        buttons: [
            {
                extend: 'copyHtml5'
            },
            {
                extend: 'excelHtml5',
                title: 'Monthly Spending Excel Report - EAY'
            },
            {
                extend: 'pdfHtml5',
                title: 'Monthly Spending PDF Report - EAY'
            },
            {
                extend: 'csvHtml5',
                title: 'Monthly Spending CSV Report - EAY'
            },
        ]
    }).container().children().each(function () {
        $(this).addClass("dropdown-item");
    });
    $("#exportOptionDropDown").append(buttons);

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
            });
            $(".gpa-spending").prepend("- ");
        }).fail(function () {
            let ref = $("#monthlySpendingLoadingText");
            ref.prev().remove();
            table.row.add([ERROR])
        });
    }

    $("#spendingTable_filter input[type=search]").addClass("form-control d-inline-block")
});

