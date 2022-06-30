odoo.define('attendance_face_recognition.field_one2many_descriptor', function (require) {
    "use strict";

    var FieldOne2Many = require('web.relational_fields').FieldOne2Many;
    var framework = require('web.framework');

    var core = require('web.core');
    var _t = core._t;

    FieldOne2Many.include({
        init: function() {
            this._super.apply(this, arguments);
        },

        load_models: function(){
            var self = this;
            self.load_label = $.Deferred();
            return Promise.all([
                faceapi.nets.tinyFaceDetector.loadFromUri('/attendance_face_recognition/static/src/lib/weights'),
                faceapi.nets.faceLandmark68Net.loadFromUri('/attendance_face_recognition/static/src/lib/weights'),
                faceapi.nets.faceLandmark68TinyNet.loadFromUri('/attendance_face_recognition/static/src/lib/weights'),
                faceapi.nets.faceRecognitionNet.loadFromUri('/attendance_face_recognition/static/src/lib/weights'),
                faceapi.nets.faceExpressionNet.loadFromUri('/attendance_face_recognition/static/src/lib/weights'),
            ])
        }, 

        _openFormDialog: function (params) {
            if (this.model === "hr.employee" && this.view.arch.tag === 'kanban') {
                var self = this;
                
                var context = this.record.getContext(_.extend({},
                    this.recordParams,
                    { additionalContext: params.context }
                ));
                if (this.nodeOptions.no_open) {
                    return;
                }
                this.trigger_up('open_one2many_record', _.extend(params, {
                    domain: this.record.getDomain(this.recordParams),
                    context: context,
                    field: this.field,
                    fields_view: this.attrs.views && this.attrs.views.form,
                    parentID: this.value.id,
                    viewInfo: this.view,
                    deletable: this.activeActions.delete && params.deletable,
                    on_saved: async function (record) {
                        if (_.some(self.value.data, {id: record.id})) {
                            var image = $('#face_image div img')[0];
                            await self._setValue({ operation: 'UPDATE', id: record.id }).then(function () {                           
                                if (record.res_id){
                                    self.getDescriptor(record.res_id, image);
                                }
                            })
                        }else{
                            var image = $('#face_image div img')[0];
                            self._create_descriptor(self.res_id, image);
                        }
                    }
                }));
            }else{
                return this._super.apply(this, arguments);
            }
        },

        getDescriptor: async function(res_id, image){
            var self = this;
            if (image.src.indexOf("placeholder.png") > -1){
                return this.do_warn(_t("Error"), _t("Photo unavailable."));
            }            
            framework.blockUI();
            self.load_models().then(async function(){
                self.load_label.resolve();
                var has_Detection_model = self.isFaceDetectionModelLoaded();
                var has_Recognition_model = self.isFaceRecognitionModelLoaded();
                var has_Landmark_model = self.isFaceLandmarkModelLoaded();

                if (has_Detection_model && has_Recognition_model && has_Landmark_model){
                    var img = document.createElement('img');
                    img.src= image.src;

                    const faceResults = await faceapi.detectSingleFace(img, new faceapi.TinyFaceDetectorOptions())
                        .withFaceLandmarks()
                        .withFaceDescriptor();
                    
                    if (faceResults != undefined && faceResults && faceResults.descriptor){
                        var descriptor = self.formatDescriptor(faceResults.descriptor);                        
                        self._write_descriptor(descriptor, res_id, image);
                    }
                }else{
                    return setTimeout(() => self.getDescriptor(res_id, image))
                }
            })
        },
        _create_descriptor: async function(res_id, image){
            var self = this;
            if (image.src.indexOf("placeholder.png") > -1){
                return this.do_warn(_t("Error"), _t("Photo unavailable."));
            }
            framework.blockUI();
            self.load_models().then(async function(){
                self.load_label.resolve();
                var has_Detection_model = self.isFaceDetectionModelLoaded();
                var has_Recognition_model = self.isFaceRecognitionModelLoaded();
                var has_Landmark_model = self.isFaceLandmarkModelLoaded();
                
                if (has_Detection_model && has_Recognition_model && has_Landmark_model){
                    var img = document.createElement('img');
                    img.src= image.src;

                    const faceResults = await faceapi.detectSingleFace(img, new faceapi.TinyFaceDetectorOptions())
                        .withFaceLandmarks()
                        .withFaceDescriptor();                                            
            
                    if (faceResults != undefined && faceResults && faceResults.descriptor){
                        return self._rpc({
                            model: 'hr.employee.faces',
                            method: 'create',
                            args: [{
                                image: image.src.replace(/^data:image\/(png|jpg);base64,/, ""),
                                descriptor: self.formatDescriptor(faceResults.descriptor),
                                has_descriptor: true,
                                employee_id: res_id,                                                                                                            
                            }],
                        }).then(function(){
                            framework.unblockUI();
                            self.trigger_up('reload');
                        })
                    }
                }else{
                    return setTimeout(() => self._create_descriptor(res_id, image))
                }
            })
        },
        _write_descriptor: function(descriptor, res_id, image){
            var self = this;       
            image = image.src.replace(/^data:image\/(png|jpg);base64,/, "");     
            if (res_id){
                return self._rpc({
                    model: 'hr.employee.faces',
                    method: 'write',
                    args: [parseInt(res_id),{
                        'descriptor':descriptor,
                        'image' : image,
                    }],
                }).then(function(data){                    
                    framework.unblockUI();
                    self.trigger_up('reload');
                });
            }else{
                framework.unblockUI();
            }          
        },
        formatDescriptor: function (descriptor) {
            var self = this;
            let result = window.btoa(String.fromCharCode(...(new Uint8Array(descriptor.buffer))));
            return result;
        },

        getCurrentFaceDetectionNet: function() {
            var self = this;
            return faceapi.nets.tinyFaceDetector;
        },

        isFaceDetectionModelLoaded: function() {
            var self = this;
            return !!self.getCurrentFaceDetectionNet().params
        },

        getCurrentFaceRecognitionNet:function () {
            var self = this;
            return faceapi.nets.faceRecognitionNet;
        },

        isFaceRecognitionModelLoaded: function() {
            var self = this;
            return !!self.getCurrentFaceRecognitionNet().params
        },

        getCurrentFaceLandmarkNet: function() {
            var self = this;
            return faceapi.nets.faceLandmark68Net;
        },

        isFaceLandmarkModelLoaded: function() {
            var self = this;
            return !!self.getCurrentFaceLandmarkNet().params
        },
    });
});
