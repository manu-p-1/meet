def gather_form_errors(form):
    ll = []
    for field, errors in form.errors.items():
        for error in form.errors[field]:
            ll.append(error)
    return ll
