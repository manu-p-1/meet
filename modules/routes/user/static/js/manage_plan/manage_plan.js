const searchForm = $("#searchForm");
const deletePlanButton = $("#deletePlanButton");

searchForm.on("submit", function (evt) {
    evt.preventDefault();
    $.ajax({
        url: "/util/plans/find/manage_plan/?"
            + "value=" + encodeURIComponent($("#planSearch").val()) + "&"
            + "tz=" + encodeURIComponent(getTz()),

        type: 'GET',
        success: function (data) {
            if (data["response_status"] === "success") {
                resetForm();
                removeAlert();
                readonlyProp(false);

                let resp = data['response'];

                $("#plan_name").val(resp['plan_name']);
                $("#funding_amount").val(resp['funding_amount']).trigger("input");
                $("#plan_justification").val(resp['justification']);
                $("#memo").val(resp['memo']).trigger("input");
                $("#start_date").val(resp['start_date']);
                $("#dest_fund").val(resp['dest_fund']).change();

                if (resp['has_employee_specific']) {
                    $("#has_fund_individuals").trigger("click");

                    if (resp['has_all_employees']) {
                        $("#disbursement_type-0").click();
                    } else {
                        $("#disbursement_type-1").click();
                        loadEmployees(resp['employees_list']);
                    }
                }
                if (resp['has_end_date']) {
                    $("#has_end_date").trigger("click");
                    $("#end_date").val(resp['end_date']);
                }
                if (resp['has_velocity_control']) {
                    $("#has_velocity_controls").trigger("click");
                    $("#vel_control_name").val(resp['control_name']);
                    $("#vel_control_window").val(resp['control_window']);
                    $("#vel_amt_limit").val(resp['amount_limit']);
                    $("#vel_usage_limit").val(resp['start_date']);
                }

                changePriority(PriorityObj[resp['priority']]);

                function loadEmployees(employeeList) {
                    for (let val of employeeList) {
                        addNewEmployee(val['name'], val['id']);
                    }
                }

                let active = data['status']['active']['info'];
                let expired = data['status']['expired']['info'];

                if (active) { // Active Plan
                    readonlyProp(true);
                    alertTop(".main-content-container", active);
                    deletePlanButton.prop('disabled', false);
                    $("#editPriority").attr("style", "pointer-events:none;");
                }
                else if (expired){
                    readonlyProp(true);
                    alertTop(".main-content-container", expired['response']);
                    $("#editPriority").attr("style", "pointer-events:none;");
                }

            } else {
                alertTop(".main-content-container", data['response']);
            }
        },
        error: function () {
            showErrorModal(REQ_ERR);
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
    $("#time_zone").val(getTz());
    const url = form.attr('action');
    replaceBtn("#update_plan_btn");

    $.ajax({
        url: url,
        type: 'POST',
        data: form.serialize(),
        success: function (data) {
            alertTop(".main-content-container", data['response']);
            if (data['response_status']) {
                resetForm();
            }
            enableBtn("#update_plan_btn");
        },
        error: function () {
            showErrorModal(REQ_ERR);
        }
    });
}

function getTz() {
    return Intl.DateTimeFormat().resolvedOptions().timeZone
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
            showErrorModal(REQ_ERR);
        }
    });
}

readonlyProp(true);

function readonlyProp(valueBool) {
    form.find(":input:not([type=hidden])").prop('disabled', valueBool);
    form.find(".remove-new-employee-input").attr("style", "pointer-events:none");
}



