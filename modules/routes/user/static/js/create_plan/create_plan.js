$(function () {
    //For the Date Picker
    let pickerFormat = 'MM/DD/YYYY hh:mm A';
    let ref = $("#activeRange");

    ref.daterangepicker({
        autoUpdateInput: false,
        timePicker: true,
        startDate: moment().startOf('minute'),
        minDate: moment().startOf('minute'),
        endDate: moment().startOf('hour').add(32, 'hour'),
        maxDate: moment().startOf('year').add(5, 'year'),
        locale: {
            format: pickerFormat
        }
    });
    ref.on('apply.daterangepicker', function (ev, picker) {
        $(this).val(picker.startDate.format(pickerFormat) + ' - ' + picker.endDate.format(pickerFormat));
    });

    ref.on('cancel.daterangepicker', function (ev, picker) {
        $(this).val('');
    });

    //For the Individual Employee toggle
    let indivUserToggle = $("#fundIndivEmployeesToggle");
    let fundIndivEmployeeDiv = $("#employeeIDBoundary");

    indivUserToggle.on("click", function () {
        toggleDiv(indivUserToggle, fundIndivEmployeeDiv);
    });

    //For adding employees
    let nei = $("#addNewEmployeeInput");
    var newEmployeeCount = 2;

    nei.on("click", addNewEmployee);

    function addNewEmployee() {
        if (newEmployeeCount <= 12) {
            let lastChild = $("#employeeIDBoundaryRow").children(":last-child");
            let template =
                `<div class="form-group col-md-3">
                <label class="text-muted additional-employee-input-label">Employee <span class="employeeCount">${newEmployeeCount}</span></label>
                <div class="input-container">
                    <input class="employeeIDInput form-control position-relative" name="employeeOptions" placeholder="Enter Employee ID" required>
                    <span class="removeNewEmployeeInput material-icons">remove_circle</span>
                </div>
            </div>`;

            lastChild.after(template);
            newEmployeeCount++;
        } else {
            alert("Only a maximum of 12 recipients can receive funds at one time");
        }
    }

    //For Removing employees
    let rei = $(".removeNewEmployeeInput");
    $(document).on("click", ".removeNewEmployeeInput", function (e) {
        if (newEmployeeCount > 2) {
            removeNewEmployee(e);
        } else {
            indivUserToggle.trigger("click");
        }
    });

    function removeNewEmployee(e) {
        let closestGroup = $(e.target).closest(".form-group");
        let after = $(closestGroup).nextAll().find("label.additional-employee-input-label > .employeeCount");

        for (let labelNum of after) {
            let x = $(labelNum);
            x.html(parseInt(x.html()) - 1);
        }
        $(closestGroup).remove();
        newEmployeeCount--;
    }

    //For the veolocity controls toggle
    let velocityControlsToggle = $("#controlToggle");
    let velocityControlsDiv = $("#fundControls");

    velocityControlsToggle.on("click", function () {
        toggleDiv(velocityControlsToggle, velocityControlsDiv);
    });

    function toggleDiv(toggler, divElement) {
        if (divElement.hasClass("d-none")) {
            toggler.attr("checked", "checked");
            divElement.removeClass("d-none");
            divElement.find("input").attr("required")
        } else {
            toggler.removeAttr("checked", "checked");
            divElement.addClass("d-none");
            divElement.find("input").removeAttr("required");
        }
    }
});


