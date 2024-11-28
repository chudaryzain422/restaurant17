odoo.define('fbu_queue_management.main', function(require) {
    "use strict";
    var core = require('web.core');
    var ajax = require('web.ajax');
    $(document).ready(function() {
        $('#list_refr').on('click', function() {
            var offset = document.getElementById('list_refr').value;
            var qsession = document.getElementById('q_session').value;
            var newOffset = parseInt(offset) * 7;
            debugger;
            ajax.jsonRpc("/today/tokens/", 'call', {
                'offset': newOffset,
                'session': qsession
            }).then(function(vals) {
                var tbody = vals['tbody'];
                var moreRec = vals['more'];
                if (moreRec) {
                    var tkBody = $('#token_body');
                    tkBody.replaceWith(tbody);
                }
            });
        });
        $('#list_left').on('click', function() {
            var offset = document.getElementById('list_left').value;
            var rightOffset = document.getElementById('list_right').value;
            var refOffset = document.getElementById('list_refr').value;
            var qsession = document.getElementById('q_session').value;
            var newOffset = parseInt(offset) * 7;
            if (newOffset >= 0) {
                debugger;
                ajax.jsonRpc("/today/tokens/", 'call', {
                    'offset': newOffset,
                    'session': qsession
                }).then(function(vals) {
                    var tbody = vals['tbody'];
                    var moreRec = vals['more'];
                    if (moreRec) {
                        document.getElementById('list_refr').value = parseInt(refOffset) - 1;
                        document.getElementById('list_left').value = parseInt(offset) - 1;
                        document.getElementById('list_right').value = parseInt(rightOffset) - 1;
                        var tkBody = $('#token_body');
                        tkBody.replaceWith(tbody);
                    }
                });
            }
        });
        $('#list_right').on('click', function() {
            var offset = document.getElementById('list_right').value;
            var leftOffset = document.getElementById('list_left').value;
            var refOffset = document.getElementById('list_refr').value;
            var qsession = document.getElementById('q_session').value;
            var newOffset = parseInt(offset) * 7;
            debugger;
            ajax.jsonRpc("/today/tokens/", 'call', {
                'offset': newOffset,
                'session': qsession
            }).then(function(vals) {
                var tbody = vals['tbody'];
                var moreRec = vals['more'];
                if (moreRec) {
                    document.getElementById('list_refr').value = parseInt(refOffset) + 1;
                    document.getElementById('list_right').value = parseInt(offset) + 1;
                    document.getElementById('list_left').value = parseInt(leftOffset) + 1;
                    var tkBody = $('#token_body');
                    tkBody.replaceWith(tbody);
                }
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