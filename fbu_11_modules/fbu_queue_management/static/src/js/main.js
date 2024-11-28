odoo.define('fbu_queue_management.main', function(require) {
    "use strict";
    var core = require('web.core');
    var ajax = require('web.ajax');
    // Binds to the global ajax scope
    $( document ).ajaxStart(function() {
        $( "#loader" ).show();
    });

    $( document ).ajaxComplete(function() {
        $( "#loader" ).hide();
    });

/*    function showQueueStatus() {
        var offset = parseInt(document.getElementById('dept_offset').value);
        console.log(offset);
        ajax.jsonRpc("/qms/web/queue_status_update", 'call', {
            'offset': offset
        }).then(function(vals) {
            var div_ready = vals['div_content_ready'];
            var div_progress = vals['div_content_progress'];
            console.log('div_ready'+div_ready);
            console.log('div_progress'+div_progress);
            if (div_ready) {
                var readyBody = $('.ready_content');
                console.log('readyBody'+readyBody);
                readyBody.empty().append(div_ready)
                //readyBody.replaceWith(div_ready);
            }
            if (div_progress) {
                var progressBody = $('.progress_content');
                console.log('progressBody'+div_progress);
                progressBody.empty().append(div_progress)
                //progressBody.replaceWith(div_progress);
            }
        });
        myVar = setTimeout(showQueueStatus, 7000);
    }*/

    $(document).ready(function() {
        function errorBarcode() {
            debugger;
            clearBarcode();
            debugger;
            document.getElementById('token_status_container').style.display = 'block';
            document.getElementById('token_status').innerHTML = "Cannot Scan Error On Barcode!!";
        }
        function clearBarcode() {
            document.getElementById('token_no_container').style.display = "none";
            document.getElementById('token_number').innerHTML = '';
            document.getElementById('barcode').value = "";
            document.getElementById('barcode').focus();
            document.getElementById('token_status_container').style.display = 'none';
            document.getElementById('token_status').innerHTML = '';
            $("#order_name > p").text('');
            document.getElementById('order_id').value = '';
            document.getElementById('wk_print_button').style.display = "none";
            document.getElementById('wk_print_button').style.width = "99%";
            document.getElementById('customer_name').style.display = "none";
            $("#customer_name > p").text('');
        }
        function scanBarcode(barcode) {
            debugger;
            var qsession = document.getElementById('session_id').value;
            var company = document.getElementById('company_id').value;
            console.log('companycompany',company);
            debugger;
            ajax.jsonRpc("/qms/order/details", 'call', {
                'barcode': barcode,
                'session': qsession,
                'company': company
            }).then(function(data) {
                var order_name = data['order_name'];
                var order_id = data['order_id'];
                var customer_name = data['customer_name'];
                var token_no = data['token_number'];
                var order_barcode = data['order_barcode'];
                var token_status = data['token_status'];
                if (token_no) {
                    document.getElementById('token_no_container').style.display = "inherit";
                    document.getElementById('token_number').innerHTML = token_no;
                    document.getElementById('barcode').value = "";
                    document.getElementById('barcode').focus();
                    document.getElementById('token_status_container').style.display = 'block';
                    document.getElementById('token_status').innerHTML = data['token_status'].toUpperCase();

                    $("#order_name > p").text(order_name);
                    document.getElementById('order_id').value = order_id;
                    document.getElementById('wk_print_button').style.display = "inherit";
                    document.getElementById('wk_print_button').style.width = "99%";

                }
                if (customer_name) {
                    document.getElementById('customer_name').style.display = "inherit";
                    $("#customer_name > p").text(customer_name);
                }
                //setTimeout(clearBarcode(),10000);
            }).fail(function () {
                debugger;
                errorBarcode();
            });

        }
         /* Temp Solution */
        $(document).scannerDetection({
            timeBeforeScanTest: 200,
            avgTimeByChar: 40,
            preventDefault: true,
            endChar: [13],
            onComplete: function(barcode, qty){
                debugger;
                scanBarcode(barcode);
                debugger;
            },
            onError: function(string, qty) {
                debugger;
                errorBarcode();
                /*$.when(errorBarcode()).then(function () {
                        setTimeout(clearBarcode(),10000);
                });  */
            }
        });


        $('#barcode').on('change', function() {
            var barcode = document.getElementById('barcode').value;
            debugger;
            scanBarcode(barcode);
            debugger;
        });

        $('#process_order').on('click', function() {
            var qsession = document.getElementById('session_id').value;
            var order_id = document.getElementById('order_id').value;
            var barcode = document.getElementById('barcode').value;
            var token_number = document.getElementById('token_number').innerHTML;
            debugger;
            ajax.jsonRpc("/qms/order/token/create", 'call', {
                'order_id': order_id,
                'session_id': qsession,
                'token_number': token_number,
                'order_barcode': barcode
                }
                ).done(function(data) {
                    document.getElementById('barcode').value = "";
                    document.getElementById('barcode').focus();
                    document.getElementById('token_status_container').style.display = 'block';
                    document.getElementById('token_status').innerHTML = data['token_status'].toUpperCase();
            });
        });



        $('#ready').on('click', function() {
            var qsession = document.getElementById('session_id').value;
            var order_id = document.getElementById('order_id').value;
            var token_number = document.getElementById('token_number').innerHTML;
            debugger;
            ajax.jsonRpc("/qms/order/token/ready", 'call', {
                'order_id': order_id,
                'session_id': qsession,
                'token_number': token_number
            }).done(function(data) {
                document.getElementById('barcode').value = "";
                document.getElementById('barcode').focus();
                document.getElementById('token_status_container').style.display = 'block';
                document.getElementById('token_status').style.color = 'green!important';
                document.getElementById('token_status').innerHTML = data['token_status'].toUpperCase();
            });
        });

        $('#delivery').on('click', function() {
            var qsession = document.getElementById('session_id').value;
            var order_id = document.getElementById('order_id').value;
            var token_number = document.getElementById('token_number').innerHTML;
            debugger;
            ajax.jsonRpc("/qms/order/token/delivery", 'call', {
                'order_id': order_id,
                'session_id': qsession,
                'token_number': token_number
            }).done(function(data) {
                document.getElementById('barcode').value = "";
                document.getElementById('barcode').focus();
                document.getElementById('token_status').innerHTML = data['token_status'].toUpperCase();
            });
        });


        function requestFullScreen(element) {
            var requestMethod = element.requestFullScreen || element.webkitRequestFullScreen || element.mozRequestFullScreen || element.msRequestFullScreen;
            var isInFullScreen = (document.fullscreenElement && document.fullscreenElement !== null) || (document.webkitFullscreenElement && document.webkitFullscreenElement !== null) || (document.mozFullScreenElement && document.mozFullScreenElement !== null) || (document.msFullscreenElement && document.msFullscreenElement !== null);
            var docElm = document.documentElement;
            if (!isInFullScreen) {
                if (docElm.requestFullscreen) {
                    docElm.requestFullscreen();
                } else if (docElm.mozRequestFullScreen) {
                    docElm.mozRequestFullScreen();
                } else if (docElm.webkitRequestFullScreen) {
                    docElm.webkitRequestFullScreen();
                } else if (docElm.msRequestFullscreen) {
                    docElm.msRequestFullscreen();
                }
                var enter = document.getElementById('qms_enter');
                enter.style.display = 'none';
                var leave = document.getElementById('qms_leave');
                leave.style.display = 'initial';
                var close = document.getElementById('qms_close');
                close.style.display = 'none';
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                } else if (document.webkitExitFullscreen) {
                    document.webkitExitFullscreen();
                } else if (document.mozCancelFullScreen) {
                    document.mozCancelFullScreen();
                } else if (document.msExitFullscreen) {
                    document.msExitFullscreen();
                }
                var enter = document.getElementById('qms_enter');
                enter.style.display = 'initial';
                var leave = document.getElementById('qms_leave');
                leave.style.display = 'none';
                var close = document.getElementById('qms_close');
                close.style.display = 'initial';
            }
        }
        $('.qms_fs').on('click', function() {
            var elem = document.body;
            requestFullScreen(elem);
        });
        $('.print_token_pdf').on('click', function() {
            var tokenId = document.getElementById('token_id').value;
            var tokenSession = document.getElementById('session_id').value;
            var attachmentId = document.getElementById('attachment_id').value;
            var isPrinter = document.getElementById('is_printer').value;
            var redirect = "/web/content/" + attachmentId + "/token_" + tokenId;
            window.location = redirect;
            if (isPrinter === 'yes') {
                var redirect_url = "/qms/web/session/" + tokenSession;
                window.location = redirect_url;
            } else {
                setTimeout(function() {
                    var redirect_url = "/qms/web/session/" + tokenSession;
                    window.location = redirect_url;
                }, 200);
            }
        });


    })
});
