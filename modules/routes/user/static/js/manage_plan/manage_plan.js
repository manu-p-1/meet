let searchForm = $("#searchForm");
var planForm = $(".plan-form");
searchForm.on("submit", function (e) {
    e.preventDefault();
    $.ajax({
        url: `/util/plans/find/manage_plan/?value=${$("#planSearch").val()}`,
        type: 'GET',
        success: function (data) {
            if (data["response_status"] === "success") {
                resetForm();
                removeAlert();

                if (!data['active']) {
                    readonlyProp(false);
                } else {
                    $(".active-danger").removeClass("d-none");
                }
                data = data['response'];

                $("#planName").val(data['plan_name']);
                $("#fundingAmount").val(data['funding_amount']);
                $("#planJustification").val(data['justification']);
                $("#memo").val(data['memo']).trigger("input");
                $("#startDate").val(data['start_date']);
                $("#destFund").val(data['dest_fund']).change();

                if (data['has_employee_specific']) {
                    $("#fundIndivEmployeesToggle").trigger("click");
                    loadEmployees(data['employees_list']);
                }
                if (data['has_end_date']) {
                    $("#endDateToggle").trigger("click");
                    $("#endDate").val(data['end_date']);
                }
                if (data['has_velocity_control']) {
                    $("#controlToggle").trigger("click");
                    $("#controlName").val(data['control_name']);
                    $("#controlWindow").val(data['control_window']);
                    $("#amountLimit").val(data['amount_limit']);
                    $("#usageLimit").val(data['start_date']);
                }

                function loadEmployees(employeeList) {
                    for (let val of employeeList) {
                        addNewEmployee(val['name'], val['id'])
                    }
                }
            } else {
                alertTop(".main-content-container", data['response']);
            }
        },
        error: function () {
            alert(ERROR);
        }
    });
});

planForm.on("submit", function (e) {
    let answer = confirm("Are you sure you would like to update this plan?");
    if (!answer) {
        return false;
    }
    e.preventDefault();
    $("#timeZone").val(Intl.DateTimeFormat().resolvedOptions().timeZone);
    const form = $(this);
    const url = form.attr('action');
    replaceBtn("#updatePlanButton");

    $.ajax({
        url: url,
        type: 'POST',
        data: form.serialize(),
        success: function (data) {
            alertTop(".main-content-container", data['response']);
            if (data['response_status'] === true) {
                resetForm();
            }
            enableBtn("#updatePlanButton");
        },
        error: function () {
            alert(ERROR);
        }
    });
});


$("#deletePlanButton").on("click", function (e) {
    let answer = confirm("Are you sure you would like to delete this plan?");
    if (!answer) {
        return false;
    }
    e.preventDefault();

    replaceBtn("#deletePlanButton");

    $.ajax({
        url: "/util/plans/find/delete_plan/",
        type: 'POST',
        data: form.serialize(),
        success: function (data) {
            alertTop(".main-content-container", data['response']);
            if (data['response_status'] === true) {
                resetForm();
            }
            replaceBtn("#deletePlanButton");
        },
        error: function () {
            alert(ERROR);
        }
    });
});

readonlyProp(true);

function readonlyProp(valueBool) {
    planForm.find(":input").prop('disabled', valueBool);
}



