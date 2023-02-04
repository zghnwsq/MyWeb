function commonReturnMsg(data) {
    let message;
    let ret_layer = null;
    if (data) {
        if (typeof data == 'string') {
            message = data;
        }
        if (data.msg) {
            message = data.msg;
        }
        if (message) {
            ret_layer = layer.open({
                content: '<div style="padding: 20px 2em;">' + message + '</div>'
                , type: 1
                , title: '提示'
                , time: 5000
                , btn: '确定'
                , yes: function (idx) {
                    layer.close(idx);
                }
            });
            return ret_layer
        }
    }
    return ret_layer
}

