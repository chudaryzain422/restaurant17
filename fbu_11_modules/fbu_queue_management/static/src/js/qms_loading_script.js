odoo.define('fbu_queue_management.web_client', function (require) {
    "use strict";

    const WebClient = require('web.AbstractWebClient');
    const ActionManager = require('web.ActionManager');

    class CustomWebClient extends WebClient {
        async show_application() {
            debugger;
            await this.action_manager.do_action("queue_ticket.ui");
        }
    }

    $(document).ready(function () {
        const webClient = new CustomWebClient();
        webClient.setElement($(document.body));
        webClient.start();
    });

    return CustomWebClient;
});
