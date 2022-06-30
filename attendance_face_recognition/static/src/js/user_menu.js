odoo.define("attendance_face_recognition.report_menu", function (require) {
    "use strict";

    var UserMenu = require("web.UserMenu");
    var session = require("web.session");

    var CustomUserMenu = UserMenu.include({
        template: 'UserMenu',
    
        _onMenuFacerecognition: function() {
            var self = this;
            this.trigger_up('clear_uncommitted_changes', {
                callback: function () {
                    self._rpc({
                        route: "/web/action/load",
                        params: {
                            action_id: "attendance_face_recognition.action_simple_face_recognition"
                        },
                    })
                    .then(function (result) {
                        result.res_id = session.uid;
                        self.do_action(result);
                    });
                },
            });
        },
    });

    return CustomUserMenu;
});
