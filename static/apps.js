$(function(){
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
        $('.tt').tooltip({
            placement: "top"
        })
    })
    $('.dropdown-menu-right').click(function(e) {
        e.stopPropagation();
    });
    $(function () {
        $('.popover-dismiss').popover({
            trigger: 'focus'
        })
        $('[data-toggle="popover"]').popover()
    })
})

function edit_application(ev, app_site){
    var payload = {"app_site" : app_site, "type":"edit_application"};
    var form = document.createElement('form');
    form.style.visibility = 'hidden'; // no user interaction is necessary
    form.method = 'POST'; // forms by default use GET query strings
    form.action = ev.getAttribute('data-add-relationship-url');
    for (var key in payload) {
        console.log(key);
        var input = document.createElement('input');
        input.name = key;
        input.value = payload[key];
        form.appendChild(input); // add key/value pair to form
    }
    document.body.appendChild(form); // forms cannot be submitted outside of body
    form.submit(); // send the payload and navigate
}

function add_annotation_form(e){
    var annotation_form = '<form class="form annotation_form" name="form1" action="' + e.getAttribute('data-add-annotation-url') + `" method="post"><div class="form-group">
      <label>Annotation: </label>
      <textarea
        class="form-control"
        id="exampleFormControlTextarea1"
        name="annotation"
        rows="3"
        /></textarea>
  <button id="submit_btn" type="submit" class="btn btn-primary">Submit</button>
    </div>
</form>`
    $(annotation_form).insertBefore(e);
    $(e).remove();
}

function resolve_annotation(ev){
    window.location.href = ev.getAttribute('data-resolve-url');
}
