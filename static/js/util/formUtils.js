function replaceBtn(btn) {
    let ref = $(btn);
    ref.html(`<i class="fas fa-spinner fa-pulse"></i>`);
    ref.prop("disabled", true);
}

function serializedToObject(items) {
    var data = {};
    $(items).serializeArray().map(function (x) {
        data[x.name] = x.value;
    });
    return data;
}

function post(path, method = "POST", ...parameters) {
    let form = $('<form></form>');
    form.attr({"method": method, "action": path});
    form.addClass("d-none");
    $.each(parameters, function (key, obj) {
        for (let k in obj) {
            if (obj.hasOwnProperty(k)) {
                let field = $('<input></input>');
                field.attr("type", "hidden");
                field.attr("name", k);
                field.attr("value", obj[k]);
                form.append(field);
            }
        }
    });
    // Form NEEDS to be in th document body to submit form
    $(document.body).append(form);
    form.submit();
}

const arrSum = arr => arr.reduce((a, b) => a + b, 0);
const convertToNumber = arr => arr.map(Number);
