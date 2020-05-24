/* THIS PART IS FOR SUBMITTING THE FORM */
form.on("submit", function (e) {
    let answer = confirm("Are you sure you would like to create this plan? Some parts may be unmodifiable.");
    if (!answer) {
        return false;
    }
    e.preventDefault(); // avoid to execute the actual submit of the form.
    $("#timeZone").val(Intl.DateTimeFormat().resolvedOptions().timeZone);
    const form = $(this);
    const url = form.attr('action');
    replaceBtn("#createPlanButton");

    $.ajax({
        type: "POST",
        url: url,
        data: form.serialize(), // serializes the form's elements
        success: function (data) {
            alertTop(".main-content-container", data['response']);

            if (data['response_status'] === "success") {
                resetForm();
            }
            enableBtn("#createPlanButton")
        },
        error: function (data) {
            alert(ERROR);
        }
    });
});