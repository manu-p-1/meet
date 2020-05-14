$(function () {

    //For the Description Counter
    let descriptionBox = $("#description");
    let descriptionCounterHolder = $("#count_message");
    let descriptionCounter = $("#count_message_amt");
    let descriptionBoxMaxLength = parseInt(descriptionBox.attr("maxLength"));
    updateDescriptionCounter(0);

    descriptionBox.on("input", function () {
        let num = $(this).val().length;
        updateDescriptionCounter(num);
    });

    function updateDescriptionCounter(value) {
        descriptionCounter.html(`${value}/${descriptionBoxMaxLength}`);
        if (value === descriptionBoxMaxLength) {
            descriptionCounterHolder.addClass("text-success");
        } else {
            if (descriptionCounterHolder.hasClass("text-success")) {
                descriptionCounterHolder.removeClass("text-success");
            }
        }
    }

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
                    <input class="employeeIDInput form-control position-relative" name="employeesOptional-${newEmployeeCount - 1}" placeholder="Enter Employee ID" type="text" required value>
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

    //For the velocity controls toggle
    let velocityControlsToggle = $("#controlToggle");
    let velocityControlsDiv = $("#fundControls");

    velocityControlsToggle.on("click", function () {
        toggleDiv(velocityControlsToggle, velocityControlsDiv);
    });

    function toggleDiv(toggler, divElement) {
        if (divElement.hasClass("d-none")) {
            toggler.attr("checked", "checked");
            divElement.removeClass("d-none");
            divElement.find("input").prop("required", true)
        } else {
            toggler.removeAttr("checked", "checked");
            divElement.addClass("d-none");
            divElement.find("input").removeAttr("required");
        }
    }

    /* THIS PART IS FOR SUBMITTING THE FORM */
    $("#newPlanForm").on("submit", function (e) {
        let answer = confirm("Are you sure you would like to create this plan? Some parts may be unmodifiable.");
        if (!answer) {
            return false;
        }
        e.preventDefault(); // avoid to execute the actual submit of the form.

        var form = $(this);
        var url = form.attr('action');
        console.log(form.serialize());
        $.ajax({
            type: "POST",
            url: url,
            data: form.serialize(), // serializes the form's elements.
            success: function (data) {
                alert(data);
            },
            error: function (data) {
                alert(data);
            }
        });
    })
});


