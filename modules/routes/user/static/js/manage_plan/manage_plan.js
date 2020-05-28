const searchForm = $("#searchForm");
const deletePlanButton = $("#deletePlanButton");

searchForm.on("submit", function (evt) {
    evt.preventDefault();
    $.ajax({
        url: `/util/plans/find/manage_plan/?value=${$("#planSearch").val()}`,
        type: 'GET',
        success: function (data) {
            if (data["response_status"] === "success") {
                resetForm();
                removeAlert();
                readonlyProp(false);

                let resp = data['response'];

                $("#planName").val(resp['plan_name']);
                $("#fundingAmount").val(resp['funding_amount']);
                $("#planJustification").val(resp['justification']);
                $("#memo").val(resp['memo']).trigger("input");
                $("#startDate").val(resp['start_date']);
                $("#destFund").val(resp['dest_fund']).change();

                if (resp['has_employee_specific']) {
                    $("#fundIndivEmployeesToggle").trigger("click");
                    loadEmployees(resp['employees_list']);
                }
                if (resp['has_end_date']) {
                    $("#endDateToggle").trigger("click");
                    $("#endDate").val(resp['end_date']);
                }
                if (resp['has_velocity_control']) {
                    $("#controlToggle").trigger("click");
                    $("#controlName").val(resp['control_name']);
                    $("#controlWindow").val(resp['control_window']);
                    $("#amountLimit").val(resp['amount_limit']);
                    $("#usageLimit").val(resp['start_date']);
                }

                changePriority(PriorityObj[resp['priority']]);

                function loadEmployees(employeeList) {
                    for (let val of employeeList) {
                        addNewEmployee(val['name'], val['id'])
                    }
                }

                if (data['active_status']['status']) { // Active Plan
                    readonlyProp(true);
                    alertTop(".main-content-container", data['active_status']['info']);
                    deletePlanButton.prop('disabled', false);
                    $("#editPriority").attr("style", "pointer-events:none;");
                }

            } else {
                alertTop(".main-content-container", data['response']);
            }
        },
        error: function () {
            showErrorModal(ERROR);
        }
    });
});

form.on("submit", function (evt) {
    evt.preventDefault();
    showConfirmModal("Are you sure you would like to update this plan?", function () {
        ajaxSubmitUpdateForm();
    });
});

function ajaxSubmitUpdateForm() {
    $("#timeZone").val(Intl.DateTimeFormat().resolvedOptions().timeZone);
    const url = form.attr('action');
    replaceBtn("#updatePlanButton");

    $.ajax({
        url: url,
        type: 'POST',
        data: form.serialize(),
        success: function (data) {
            alertTop(".main-content-container", data['response']);
            if (data['response_status']) {
                resetForm();
            }
            enableBtn("#updatePlanButton");
        },
        error: function () {
            showErrorModal(ERROR);
        }
    });
}

deletePlanButton.on("click", function (evt) {
    evt.preventDefault();
    showConfirmModal("Are you sure you would like to delete this plan?", function () {
        ajaxDeletePlan();
    });
});

function ajaxDeletePlan() {
    replaceBtn("#deletePlanButton");

    $.ajax({
        url: "/util/plans/find/delete_plan/",
        type: 'POST',
        data: form.serialize(),
        success: function (data) {
            alertTop(".main-content-container", data['response']);
            if (data['response_status']) {
                resetForm();
            }
            replaceBtn("#deletePlanButton");
        },
        error: function () {
            showErrorModal(ERROR);
        }
    });
}

readonlyProp(true);

function readonlyProp(valueBool) {
    form.find(":input:not([type=hidden])").prop('disabled', valueBool);
}



