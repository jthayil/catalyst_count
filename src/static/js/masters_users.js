var mt_group_company, mt_company, mt_complaint_category, mt_fraud_category, mt_fraud_subcategory, mt_fraud_subcategory, mt_root_cause, mt_functional, mt_action, mt_relation_to_company, mt_gender, mt_source_of_complaint, mt_users;


function load_users() {
    mt_users = new DataTable('#mt_users', {
        ajax: {
            url: masters_getusers_url,
            dataSrc: ''
        },
        columns: [
            { data: 'id' },
            { data: 'username' },
            { data: 'first_name' },
            { data: 'last_name' },
            { data: 'email' },
            {
                data: "is_active",
                render: function (data, type, row) {
                    if (row['is_active'] == true) { return 'Active'; }
                    else { return 'Inactive'; }
                }
            },
        ],
        createdRow: function (row, data, dataIndex) {
            $(row).addClass('masters_index palm_cursor').attr('data-id', data.id).attr('data-email', data.email).attr('data-type', 'users').attr('data-username', data.username).attr('data-first_name', data.first_name).attr('data-last_name', data.last_name).attr('data-role', data.role);
        }
    });
}

load_users()

function resp_action(r, m) {
    if (r.status == true) {
        $("#master_reset").trigger('click');
        $("#master_reset, #master_add").show();
        $("#master_update").hide();
        $('#mt_users').DataTable().ajax.reload();
    }
}

$(document).on("click", ".add", function () {
    var master_add_form = new FormData($("#id_mt_form")[0]);
    var mastertype = $(this).data('master');
    var resp = getRemote($(this).attr('form-action'), "POST", master_add_form, 'json', true, false, false);
    resp_action(resp, mastertype)
});

$(document).on("click", ".update", function () {
    var master_edit_form = new FormData($("#id_mt_form")[0]);
    var mastertype = $(this).data('master');
    var resp = getRemote($(this).attr('form-action'), "POST", master_edit_form, 'json', true, false, false);
    resp_action(resp, mastertype)
});

$(document).on("click", ".reset", function () {
    location.reload(true);
});

$(document).on("click", ".masters_index", function () {
    $("#master_username").val($(this).data('username'));
    $("#master_first_name").val($(this).data('first_name'));
    $("#master_last_name").val($(this).data('last_name'));
    $("#master_email").val($(this).data('email'));
    $("#master_role").val($(this).data('role'));
    var url = masters_uptdusers_url.slice(0, -2) + $(this).data('id') + '/'
    $("#master_update").data('master', 'user').attr('form-action', url);
    $("#master_reset, #master_update").show();
    $("#master_add, #passwd").hide();
});
