odoo.define('fbu_queue_management.qms_display', function(require) {
    "use strict";
    var core = require('web.core');
    var ajax = require('web.ajax');
    var myVar;
    // Binds to the global ajax scope
    /*$( document ).ajaxStart(function() {
        $( "#loader" ).show();
    });

    $( document ).ajaxComplete(function() {
        $( "#loader" ).hide();
    });*/

    function showQueueStatus() {
        var offset = parseInt(document.getElementById('dept_offset').value);
        var company = parseInt(document.getElementById('dept_company').value);
        console.log(company);
        if(company != null ){
            debugger;
            ajax.jsonRpc("/qms/web/queue_status_update", 'call', {
                'offset': offset,
                'company': company,
            }).then(function(vals) {
                var div_ready = vals['div_content_ready'];
                var div_progress = vals['div_content_progress'];
                if (div_ready) {
                    var readyBody = $('.ready_content');
                    readyBody.empty().append(div_ready)
                }
                if (div_progress) {
                    var progressBody = $('.progress_content');
                    progressBody.empty().append(div_progress)
                }
            });
            myVar = setTimeout(showQueueStatus, 10000);
        }
    }
    $(document).ready(function() {
        showQueueStatus();

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
            //console.log('FullScreen');
            var elem = document.body;
            requestFullScreen(elem);
        });
    })
});