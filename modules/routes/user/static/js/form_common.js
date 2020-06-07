const registeredEmployees = {};

let form = $(".plan-form");
let loading = $(".employees-loading-icon");
loading.hide();

let destFund = $("#dest_fund");
let search = $("#searchEmployee");
destFund.children(":first-child").prop("disabled", true);

const REQ_ERR = "Your request could not be processed at this time. Please wait and try again later.";
const CHOOSE_ERR = "Please choose a fund destination before searching an employee";
const cache = {};


const employeeBoundary = $("#employeeIDBoundaryRow");
const disburseAll = $("#disbursement_type-0");
const disburseSearch = $("#disbursement_type-1");


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
            showErrorModal(CHOOSE_ERR);
            search.val('');
            destFund.focus();
            return;
        }

        const ll = [];
        loading.show();

        $.getJSON(`/util/plans/find/department_employees/?department=${x}`, request, function (data) {
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
    delAutoCompleteCache();
    removeAllEmployees();
});

function delAutoCompleteCache() {
    for (let member in cache) delete cache[member];
}

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


//For the Individual Employee toggle and set initial states
let indivUserToggle = $("#has_fund_individuals");
let employeesOnly = $("#employeesOnly");
disableOrEnable(employeesOnly.find(":input"), false);


indivUserToggle.on("click", function () {
    if (employeesOnly.hasClass("d-none")) {
        disableOrEnable(employeesOnly.find(":input"), false);
        indivUserToggle.attr("checked", "checked");
        employeesOnly.removeClass("d-none");
    } else {
        indivUserToggle.removeAttr("checked", "checked");
        employeesOnly.addClass("d-none");
        disableOrEnable(employeesOnly.find(":input"), false);
    }
});


//For the Date Picker
createDatePicker($("#start_date"), moment().startOf('minute'));
createDatePicker($("#end_date"), moment().startOf('minute').add(1, 'hour'));


let newEmployeeCount = $(".employeeIDInput").length;

//For Removing employees
$(document).on("click", ".remove-new-employee-input", function (e) {
    removeNewEmployee(e);
    if (newEmployeeCount === 0) {
        disburseAll.trigger("click");
    }
});

//For the end date toggle
const endDateToggle = $("#has_end_date");
const endDateGroup = $("#endDateGroup");
$(endDateToggle).on("click", function () {
    toggleDiv(endDateToggle, endDateGroup);
});

//For the velocity controls toggle
const controlToggle = $("#has_velocity_controls");
const fundControls = $("#fundControls");
$(controlToggle).on("click", function () {
    toggleDiv(controlToggle, fundControls);
});

$(".ui-menu.ui-widget.ui-autocomplete").addClass("shadow-lg");
boundaryDisable(true);

disburseAll.on("click", function () {
    boundaryDisable(true);
});

disburseSearch.on("click", function () {
    boundaryDisable(false);
});

function disableOrEnable(selector, truth){
    selector.prop("disabled", truth)
}

function boundaryDisable(truth) {
    $("#employeeIDBoundary *").prop("disabled", truth);
}

function alertTop(divAfter, data) {
    let alertdiv = $(".alert");
    if (alertdiv.length) {
        alertdiv.replaceWith(data);
    } else {
        $(divAfter).before(data);
    }
    window.scrollTo(0, 0);
}

function removeAlert() {
    let alertdiv = $(".alert");
    if (alertdiv.length) {
        alertdiv.remove();
    }
}

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
    delete registeredEmployees[textArea.attr("data-meet-id")];
    newEmployeeCount--;

   employeeBoundary.trigger("removeEmployee");
}

function removeAllEmployees() {
   employeeBoundary.empty();
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
        let template =
            `<div class="form-group col-md-3">
                <label class="text-muted additional-employee-input-label">Employee <span class="employeeCount">${newEmployeeCount + 1}</span></label>
                <div class="input-container">
                    <textarea class="employeeIDInput form-control position-relative" data-meet-id="${id}" name="employees_list-${newEmployeeCount}" type="text" readonly rows="2">NAME: ${name}&#13;&#10;ID: ${id}
                    </textarea>
                    <span class="remove-new-employee-input material-icons">remove_circle</span>
                </div>
            </div>`;

        employeeBoundary.append(template);
        registeredEmployees[id] = name;
        newEmployeeCount++;

        employeeBoundary.trigger('newEmployee');
    } else {
        showErrorModal("Only a maximum of 12 recipients can receive funds at one time");
    }
}

function resetForm() {
    form[0].reset();

    removeAllEmployees();

    if (indivUserToggle.is(":checked")) {
        indivUserToggle.trigger("click");
    }
    if (endDateToggle.is(":checked")) {
        endDateToggle.trigger("click");
    }

    if (controlToggle.is(":checked")) {
        controlToggle.trigger("click");
    }
    for (const key in registeredEmployees) {
        delete registeredEmployees[key];
    }
    $(".active-danger").addClass("d-none");
    $("#sidebarCurrentDate").val(moment().format('MMM Do, YYYY'));
    changePriority(PriorityObj.Low);
    form.trigger("formReset");
}

function createDatePicker(referenceSelector, minimumDate) {
    let pickerFormat = 'MM/DD/YYYY hh:mm A';
    referenceSelector.daterangepicker({
        autoUpdateInput: false,
        singleDatePicker: true,
        showDropdowns: true,
        timePicker: true,
        drops: "up",
        minDate: minimumDate,
        maxDate: moment().startOf('year').add(5, 'year'),
        locale: {
            format: pickerFormat
        }
    }, function (start) {
        referenceSelector.val(start);
    });

    referenceSelector.on('apply.daterangepicker', function (ev, picker) {
        $(this).val(picker.startDate.format(pickerFormat));
    });

    referenceSelector.on('cancel.daterangepicker', function () {
        $(this).val('');
    });
}

//This is for Priorities on the sidebar
const PriorityObj = {
    Low: {
        name: "Low",
        class_: "text-success"
    },
    Medium: {
        name: "Medium",
        class_: "text-warning"
    },
    High: {
        name: "High",
        class_: "text-danger"
    },
    Urgent: {
        name: "Urgent",
        class_: "text-dark"
    }
};

$(".priority-select-dropdown .dropdown-item").on("click", function () {
    changePriority(PriorityObj[$(this).val()]);
});

function changePriority(priorityobj) {
    console.log(priorityobj);
    $("input[name=priority]").val(priorityobj.name);

    $("#prioritySetting")
        .text(priorityobj.name)
        .val(priorityobj.name)
        .removeClass()
        .addClass(priorityobj.class_);
}


const UpdateTotalModule = (function () {
    const tot = {};
    const sft = $("#sidebarFundingTotal");
    const departmentSizeCache = {};
    let fundingAmount = 0.00;
    let fundingInput = null;

    tot.reset = function resetzero() {
        fundingAmount = fundingInput = 0;
        sft.html(currency_formatter.format(0));
    };

    function adjustSidebarTotal() {
        let cleaned = fundingAmount;
        try {
            if (isNaN(cleaned)) {
                formatZero();
            } else {
                cleaned = currency_formatter.format(cleaned);
            }
        } catch (err) {
            formatZero();
        }

        function formatZero() {
            cleaned = currency_formatter.format(0.00);
        }

        sft.html(cleaned);
    }

    async function adjustFundsWithDepartment() {

        fundingAmount = fundingInput * await inner_size();
        adjustSidebarTotal();

        function inner_size() {
            let optVal = $(destFund.find(":selected")[0]).val();

            if (optVal.trim()) {
                if (!departmentSizeCache.hasOwnProperty(optVal)) {
                    return new Promise((res) => {
                        $.getJSON("/util/plans/find/department_size/?department=" + optVal, function (data) {
                            console.log(data);
                            departmentSizeCache[optVal] = data['size'];
                            res(data['size']);
                        }).fail(function () {
                            alert(ERROR);
                            res(0);
                        });
                    });
                }
                return departmentSizeCache[optVal];
            } else {
                showConfirmModal("Your funding total will remain zero until you choose a funding destination");
                return 0;
            }
        }
    }

    function adjustFundsWithEmployees() {
        fundingAmount = fundingInput * $(".employeeIDInput").length;
        adjustSidebarTotal();
    }

    function adjustFundsWithInput() {
        fundingAmount = fundingInput;
        adjustSidebarTotal();
    }

    function adjustFundsIfEmployeeSpecific() {
        if (indivUserToggle.is(':checked')) {
            let checked = $("input[name='disbursement_type']:checked").val();
            if (checked === "DISB_ALL") {
                adjustFundsWithDepartment();
            } else {
                adjustFundsWithEmployees();
            }
        } else {
            adjustFundsWithInput();
        }
    }

    $("#funding_amount").on("change input", function () {
        fundingInput = $(this).val();
        adjustFundsIfEmployeeSpecific();
    });

    destFund.on("change", function () {
        adjustFundsIfEmployeeSpecific();
    });

    indivUserToggle.on("click", function () {
        if ($(this).is(":checked")) {
            adjustFundsWithDepartment();
        } else {
            fundingAmount = fundingInput;
            adjustSidebarTotal();
        }
    });

    //ON SEARCH CLICK

    disburseAll.on("click", function () {
        adjustFundsWithDepartment();
    });

    disburseSearch.on("click", function () {
        adjustFundsWithEmployees();
    });

   employeeBoundary.on("newEmployee", function () {
        adjustFundsWithEmployees();
    });

   employeeBoundary.on("removeEmployee", function(){
        adjustFundsWithEmployees();
    });

    form.on("formReset", function () {
        tot.reset();
    });

    return tot;
}());

$(document).scroll(function () {
    if ($(window).width() >= 992) {
        var y = $(document).scrollTop(), header = $("#sidebarItems");
        if (y >= (y + $('#mainContent').offset().top) || Math.floor(y) <= 230) {
            header.css({ "position": "static", "width": "auto" });
        }
        else {
            header.css({ "position": "sticky", "width": "auto", "top": "70px" });
        }
    }
});
