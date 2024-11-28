function getRemote(remote_url, method = "GET", request_data = null, response_type = "json", convertapi = true, process_data = false, content_type = 'application/x-www-form-urlencoded; charset=UTF-8') {
    var resp = $.ajax({ type: method, data: request_data, dataType: response_type, url: remote_url, async: false, processData: process_data, contentType: content_type }).responseText;
    if (convertapi) { return JSON.parse(resp); }
    return resp;
}