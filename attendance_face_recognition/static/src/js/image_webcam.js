odoo.define('attendance_face_recognition.image_webcam', function (require) {
    "use strict";

    var basic_fields = require('web.basic_fields');
    var FieldBinaryImage = basic_fields.FieldBinaryImage;
    var Dialog = require('web.Dialog');
   
    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;

    FieldBinaryImage.include({
        events: _.extend({}, FieldBinaryImage.prototype.events, {
            'click button.o_web_cam_button': 'on_webcam_open',
        }),
        init: function(parent, options) {
            this._super.apply(this, arguments);
        },        

        on_webcam_open: function(){
            var self = this;
                self.on_webcam_uploaded();
        },
        on_webcam_uploaded: function(){
            var self = this;
            this.dialog = new Dialog(this, {
                size: 'medium',
                title: _t("Capture Snapshot"),
                $content: QWeb.render('WebCamDialog'),
                buttons: [
                    {
                        text: _t("Capture Snapshot"), classes: 'btn-primary captureSnapshot',                       
                    },
                    {
                        text: _t("Close"), classes:'btn-secondary captureClose', close: true,
                    }
                ]
            }).open();

            this.dialog.opened().then(function () {  
                var video = self.dialog.$('#video').get(0);
                navigator.getUserMedia = navigator.getUserMedia 
                    || navigator.webkitGetUserMedia 
                    || navigator.mozGetUserMedia;
                
                if (navigator.getUserMedia) {
                    var openRecognition = navigator.getUserMedia(
                        { video: {} },
                        function(stream) {                                             
                            video.srcObject = stream; 
                            video.play(); 
                            video.muted = true;                            
                        },
                        function(err) {
                            console.log("onloadedmetadata");
                        }
                    );
                }

                var $captureSnapshot = self.dialog.$footer.find('.captureSnapshot');
                var $closeBtn = self.dialog.$footer.find('.captureClose');

                $captureSnapshot.on('click', function (event){
                    var img64="";
                    var image = self.dialog.$('#image').get(0);
                    image.width = $(video).width();
                    image.height = $(video).height();
                    image.getContext('2d').drawImage(video, 0, 0, image.width, image.height);
                    var img64 = image.toDataURL("image/jpeg");
                    img64 = img64.replace(/^data:image\/(png|jpg|jpeg|webp);base64,/, "");

                    if (img64){
                        var file = {};
                        self.on_file_uploaded(file.size, "webcam.jpeg", "image/jpeg", img64);
                        $closeBtn.click();
                    }

                    $captureSnapshot.text("uploading....").addClass('disabled');
                });

            });
        },
    });
});