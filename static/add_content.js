var false_alert = "";
console.log(form_values);
var id_val = 0;
var list_of_datasets = []
var list_of_dois = []
initiate(form_values)

//adds the datasets inside the input
function initiate(parsed_form_values){
    id_val = 0;
    list_of_dois = [];
    list_of_datasets = [];
    for(var key in parsed_form_values) {
        var value = parsed_form_values[key];
        console.log("key: "+key+" value: "+value);
        console.log(key[key.length - 1]); //last character in key
        console.log(!isNaN(key[key.length - 1])); // checking if key is number
        if (!isNaN(key[key.length - 1])){  //if the last character is a number then we add those datasets/doi's
            console.log("is_num");
            if (key.slice(0,4) ==="Data"){ 
                list_of_datasets.push(value)
            }
            if (key.slice(0,4) ==="DOI_"){
                list_of_dois.push(value)
            }
        }
    }
    list_of_datasets.forEach((dataset,index) => {
        const doi = list_of_dois[index]
        add_dataset(dataset);
        add_doi(doi);
    });
}

//adding an extra dataset title/doi field if there are none
if (list_of_datasets.length==0){
    add_dataset('');
    add_doi('');
}

function add_dataset(value){
    id_val++;
    var dataset =
    `<div class='form-group added'>
        <label>Dataset ${id_val}*</label>
        <div class='input-group mb-3'>
            <input
            type = "text"
            class = "form-control"
            id = ${id_val}
            name = "Dataset_Name_${id_val}"
            value = "${value}"
            placeholder = "Dataset Name ${id_val}"
            required
        />
            <div class="input-group-append">
                <button class="btn btn-secondary" type="button" id="del_${id_val}" onclick="delete_ds(this)"> - </button>
            </div>
        </div>
        <div class="valid-feedback">Looks good!</div>
    </div>`
    var add_dataset_btn = document.getElementById("add_dataset_btn");
    $(dataset).insertBefore('#add_dataset_btn');
}

function add_doi(value){
    var DOI =
    `<div class='form-group added'>
        <label>Dataset DOI ${id_val}*</label>
        <input
            type= "url"
            class= "form-control"
            id= "DOI${id_val}"
            name= "DOI_${id_val}"
            value= "${value}"
            placeholder= "DOI ${id_val}"
            required
        />
        <div class="valid-feedback">Looks good!</div>
    </div>`
    var add_dataset_btn = document.getElementById("add_dataset_btn");
    $(DOI).insertBefore('#add_dataset_btn');
}

function delete_ds(ele){
    console.log("deleting dataset");
    var id = ele.id[ele.id.length-1];
    console.log("id "+id);
    var doi =document.getElementById("DOI"+id);
    console.log("doi "+doi);

    var doi_to_del = doi.parentElement;
    doi_to_del.parentNode.removeChild(doi_to_del);
    var ele_to_del=ele.parentElement.parentElement.parentElement;
    ele_to_del.parentNode.removeChild(ele_to_del);

    var f = document.forms["form1"]
    console.log(f);
    f = $("form").serializeArray();
    console.log(f);
    formatted = {};
    for( var pair of f ){
        formatted[pair['name']] = pair['value']
    }
    console.log(formatted);
    $('.added').remove();
    initiate(formatted);
}

function autofill(){
    $('<input />').attr('type', 'hidden')
        .attr('name','autofill')
        .attr('value',true)
        .appendTo('#form1');
    console.log($('#form1'));
    form1.submit();
}

if (astatus == 'edit_application'){ //then append the prev app name 	
    $('<input />').attr('type', 'hidden')
        .attr('name','prev_app_site')
        .attr('value', site)
        .appendTo('#form1');
    console.log($('#form1'));
}

function add_topic(){
    var topic_to_add = $('#custom_topic').val(); 
    console.log(topic_to_add);
    $('#custom_topic').val('');//reset input field
    var topic_to_add_html = `<option value='${topic_to_add}' selected>${topic_to_add}</option>`
    $('#Topic').append(topic_to_add_html);
    $('#custom_topic_list').append(topic_to_add+', ');
}

(function () {
    'use strict'
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.querySelectorAll('.needs-validation')

    // Loop over them and prevent submission
    Array.prototype.slice.call(forms)
    .forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
            }
            form.classList.add('was-validated')
        }, false)
    })
})();
