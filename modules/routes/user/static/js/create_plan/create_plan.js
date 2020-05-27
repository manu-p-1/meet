/* THIS PART IS FOR SUBMITTING THE FORM */
form.on("submit", function (evt) {
    evt.preventDefault();
    showConfirmModal("Are you sure you would like to create this plan? Some parts may be unmodifiable.", function () {
        ajaxSubmitCreateForm();
    });
});

function ajaxSubmitCreateForm() {
    $("#timeZone").val(Intl.DateTimeFormat().resolvedOptions().timeZone);
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
            enableBtn("#createPlanButton");
        },
        error: function (data) {
            showErrorModal(ERROR);
        }
    });
}