const registeredEmployees = {};

$(function () {
    let form = $("#newPlanForm");
    let loading = $("#employeesLoadingIcon");
    loading.hide();
    let destFund = $("#destFund");
    let search = $("#searchEmployee");
    destFund.children(":first-child").prop("disabled", true);

    const cache = {};
    search.autocomplete({
        minLength: 1,
        source: function (request, response) {
            const term = request.term;

            if (term in cache) {
                response(cache[term]);
                return;
            }

            let x = $(destFund).find(":selected").val();
            if (!x) {
                alert("Please choose a fund destination before searching an employee");
                search.val('');
                destFund.focus();
                return;
            }

            const ll = [];
            loading.show();

            $.getJSON(`/util/department_employees/?department=${x}`, request, function (data, status, xhr) {
                if (data.length) {
                    $.each(data, function (index, value) {
                        let name = value['name'];
                        let id = value['id'];

                        let splitted = name.split(' ');
                        let fname = splitted[0];
                        let lname = splitted[1];

                        if (fname.toLowerCase().includes(term.toLowerCase()) ||
                            lname.toLowerCase().includes(term.toLowerCase())) {

                            ll.push({name: name, id: id});
                            cache[term] = ll;
                        }
                    });
                }
                response(ll);
            });
            //The sole purpose of this is to show that some kind of loading occured.
            setTimeout(function () {
                loading.hide()
            }, 1000);
        },

        select: function (event, ui) {
            console.info(ui);
            if (!registeredEmployees.hasOwnProperty(ui.item.id)) {
                addNewEmployee(ui.item.name, ui.item.id);
            }
        },

        focus: function (event, ui) {
            $(search).val(ui.item.name);
            return false;
        },
    }).autocomplete("instance")._renderItem = function (ul, item) {
        return $("<li>")
            .append(`<div> ${item.name} <br> ID: ${item.id} </div>`)
            .appendTo(ul);
    };

    //Listen to the destination fund change
    destFund.on("change", function () {
        cache.clear();
    });

    //For the Description Counter
    let memo = $("#memo");
    let memoCounterHolder = $("#count_message");
    let memoCounter = $("#count_message_amt");
    let memoBoxMaxLength = parseInt(memo.attr("maxLength"));
    updateMemoCounter(0);

    memo.on("input", function () {
        let num = $(this).val().length;
        updateMemoCounter(num);
    });


    //For the Date Picker
    createDatePicker($("#startDate"));
    createDatePicker($("#endDate"));


    //For the Individual Employee toggle
    let indivUserToggle = $("#fundIndivEmployeesToggle");
    let employeesOnly = $("#employeesOnly");

    indivUserToggle.on("click", function () {
        if (employeesOnly.hasClass("d-none")) {
            indivUserToggle.attr("checked", "checked");
            employeesOnly.removeClass("d-none");
        } else {
            indivUserToggle.removeAttr("checked", "checked");
            employeesOnly.addClass("d-none");
        }
    });

    var newEmployeeCount = 0;


    //For Removing employees
    $(document).on("click", ".removeNewEmployeeInput", function (e) {
        removeNewEmployee(e);
        if (newEmployeeCount === 0) {
            indivUserToggle.trigger("click");
        }
    });

    //For the end date toggle
    let endDateToggle = $("#endDateToggle");
    let endDateGroup = $("#endDateGroup");

    endDateToggle.on("click", function () {
        toggleDiv(endDateToggle, endDateGroup);
    });


    //For the velocity controls toggle
    let velocityControlsToggle = $("#controlToggle");
    let velocityControlsDiv = $("#fundControls");

    velocityControlsToggle.on("click", function () {
        toggleDiv(velocityControlsToggle, velocityControlsDiv);
    });


    /* THIS PART IS FOR SUBMITTING THE FORM */
    form.on("submit", function (e) {
        let answer = confirm("Are you sure you would like to create this plan? Some parts may be unmodifiable.");
        if (!answer) {
            return false;
        }
        e.preventDefault(); // avoid to execute the actual submit of the form.

        const form = $(this);
        const url = form.attr('action');
        replaceBtn("#createPlanButton");

        $.ajax({
            type: "POST",
            url: url,
            data: form.serialize(), // serializes the form's elements
            success: function (data) {
                let alertdiv = $(".alert");
                if (alertdiv.length) {
                    alertdiv.replaceWith(data['response']);
                } else {
                    $(".main-content-container").before(data['response']);
                }

                if (data['status'] === true) {
                    resetForm();
                }
                window.scrollTo(0, 0);
            },
            error: function (data) {
                alert("Your request could not be processed at this time. Please wait and try again later.");
            }
        });
        enableBtn("#createPlanButton");
    });


    function updateMemoCounter(value) {
        memoCounter.html(`${value}/${memoBoxMaxLength}`);
        if (value === memoBoxMaxLength) {
            memoCounterHolder.addClass("text-success");
        } else {
            if (memoCounterHolder.hasClass("text-success")) {
                memoCounterHolder.removeClass("text-success");
            }
        }
    }

    function removeNewEmployee(e) {
        let textArea = $(e.target).prev(".employeeIDInput");
        let closestGroup = $(textArea).closest(".form-group");
        let after = $(closestGroup).nextAll().find("label.additional-employee-input-label > .employeeCount");

        for (let labelNum of after) {
            let x = $(labelNum);
            x.html(parseInt(x.html()) - 1);
        }
        $(closestGroup).remove();
        delete registeredEmployees[textArea.attr("mrc_id")];
        newEmployeeCount--;
    }

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


    function addNewEmployee(name, id) {
        if (newEmployeeCount <= 12) {
            let bound = $("#employeeIDBoundaryRow");
            let template =
                `<div class="form-group col-md-3">
                <label class="text-muted additional-employee-input-label">Employee <span class="employeeCount">${newEmployeeCount + 1}</span></label>
                <div class="input-container">
                    <textarea class="employeeIDInput form-control position-relative" mrc_id="${id}" name="employeesOptional-${newEmployeeCount}" type="text" readonly rows="2">NAME: ${name}&#13;&#10;ID: ${id}
                    </textarea>
                    <span class="removeNewEmployeeInput material-icons">remove_circle</span>
                </div>
            </div>`;

            bound.append(template);
            registeredEmployees[id] = name;
            newEmployeeCount++;
        } else {
            alert("Only a maximum of 12 recipients can receive funds at one time");
        }
    }

    function resetForm() {
        form[0].reset();
        $("#employeeIDBoundaryRow").empty();
        if (indivUserToggle.is(":checked")) {
            indivUserToggle.trigger("click");
        }
        if (endDateToggle.is(":checked")) {
            endDateToggle.trigger("click");
        }
        if (velocityControlsToggle.is(":checked")) {
            velocityControlsToggle.trigger("click");
        }
        for (const key in registeredEmployees) {
            delete registeredEmployees[key];
        }
    }


    function createDatePicker(referenceSelector) {
        let pickerFormat = 'YYYY-MM-DD HH:mm:ss';
        referenceSelector.daterangepicker({
            autoUpdateInput: false,
            singleDatePicker: true,
            showDropdowns: true,
            timePicker: true,
            timePicker24Hour: true,
            timePickerSeconds: true,
            drops: "up",
            minDate: moment().startOf('second'),
            maxDate: moment().startOf('year').add(5, 'year'),
            locale: {
                format: pickerFormat
            }
        }, function (start, end, label) {
            referenceSelector.val(start);
        });

        referenceSelector.on('apply.daterangepicker', function (ev, picker) {
            $(this).val(picker.startDate.format(pickerFormat));
        });

        referenceSelector.on('cancel.daterangepicker', function (ev, picker) {
            $(this).val('');
        });
    }
});


