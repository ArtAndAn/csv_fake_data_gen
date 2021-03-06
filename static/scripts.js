function new_schema_add_column_btn() {
    // Function for adding an EventListener to Add column button that
    // generates and adds a new row on the page
    const btn = document.getElementById('add-column-btn')
    const new_columns_div = document.getElementById('new-schema-columns')
    let new_row_number = new_columns_div.childElementCount

    btn.addEventListener('click', () => {
        new_columns_div.insertAdjacentHTML('beforeend',
            '<div class="new-schema-row" id="new-schema-row-' + new_row_number + '">' +
            '<div class="field column-name">' +
            '    <label for="column-name-' + new_row_number + '">Column name</label>' +
            '    <input type="text" name="column-name-' + new_row_number + '" id="column-name-' + new_row_number +
            '" placeholder="Name" required>' +
            '</div>' +
            '<div class="field column-type">' +
            '    <label for="column-type-' + new_row_number + '">Type</label>' +
            '    <select name="column-type-' + new_row_number + '" id="column-type-' + new_row_number + '">' +
            '        <option>Full name</option>' +
            '        <option>Job</option>' +
            '        <option>Email</option>' +
            '        <option>Domain name</option>' +
            '        <option>Phone number</option>' +
            '        <option>Company name</option>' +
            '        <option>Text</option>' +
            '        <option>Integer</option>' +
            '        <option>Date</option>' +
            '    </select>' +
            '</div>' +
            '<div class="field column-order">' +
            '    <label for="column-order-' + new_row_number + '">Order</label>' +
            '    <input type="number" name="column-order-' + new_row_number + '" id="column-order-' + new_row_number +
            '" placeholder="0" min="1" required>' +
            '</div>' +
            '<button type="button" class="new-schema-delete" id="row-delete-' + new_row_number + '">Delete</button>' +
            '</div>'
        )
        new_row_number++
        new_schema_delete_row_btn()
        new_schema_type_select()
    })
}

function new_schema_delete_row_btn() {
    // Function for adding an EventListener to Delete row button that
    // deletes single row on the page
    const delete_btns = document.getElementsByClassName('new-schema-delete')
    for (let i = 0; i < delete_btns.length; i++) {
        delete_btns[i].addEventListener('click', (event) => {
            event.path[1].remove()
        })
    }
}

function new_schema_type_select() {
    // Function for adding an EventListener to column type selects that
    // generates and adds range inputs on the column row
    const type_selects = document.getElementById('new-schema-columns')
        .getElementsByTagName('select')
    for (let i = 0; i < type_selects.length; i++) {
        type_selects[i].addEventListener('change', () => {
            const form_row = type_selects[i].parentElement.parentElement
            if (type_selects[i].value === 'Text' || type_selects[i].value === 'Integer') {
                if (form_row.childElementCount < 5) {
                    const row_number = form_row.id.slice(-1)
                    type_selects[i].parentElement.insertAdjacentHTML('afterend',
                        '<div class="range">' +
                        '<div class="field column-range">' +
                        '   <label for="column-range-from-' + row_number + '">From</label>' +
                        '   <input type="number" name="column-range-from-' + row_number + '" id="column-range-from-' +
                        row_number + '" min="1" max="100000" required="">' +
                        '</div>' +
                        '<div class="field column-range">' +
                        '   <label for="column-range-to-' + row_number + '">To</label>' +
                        '   <input type="number" name="column-range-to-' + row_number + '" id="column-range-to-' +
                        row_number + '" min="1" max="100000" required="">' +
                        '</div>' +
                        '</div>')
                }
            } else {
                if (form_row.childElementCount > 4) {
                    form_row.children[2].remove()
                }
            }
        })
    }
}

function create_new_data_set_btn(schema_name) {
    // Function for adding an EventListener to New dataset button that
    // redirects user on the data set creation page
    const create_btn = document.getElementById('create-new-data-set')
    const rows_quantity_input = document.getElementById('generate-rows')

    create_btn.addEventListener('click', () => {
        if (rows_quantity_input.value) {
            const rows_quantity = rows_quantity_input.value
            const url = '/new-data-set/' + schema_name + '/' + rows_quantity
            window.location.replace(url)
        }
    })
}

function no_header() {
    // Function for removing the header on login page
    document.querySelector('header').remove()
}