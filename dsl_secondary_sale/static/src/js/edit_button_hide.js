// alert("loaded")
// console.log("loaded")
odoo.define('dsl_secondary_sale.custom_form_view_edit_button', function (require) {
    "use strict";

    var core = require('web.core');
    var FormView = require('web.FormView');

    var web_client = require('web.web_client');
    var FormController = require('web.FormController');

    FormController.include({
        updateButtons: function () {
            if (!this.$buttons) {
                return;
            }
            console.log("-----------buttons")
            if (this.footerToButtons) {
                var $footer = this.renderer.$el && this.renderer.$('footer');
                if ($footer && $footer.length) {
                    this.$buttons.empty().append($footer);
                }
            }
            if (this.modelName === "sale.secondary") {
                if (this.renderer.state.data.state !== "draft") {
                    this.$buttons.find('.o_form_button_edit').toggleClass('o_hidden', true);
                } else {
                    this.$buttons.find('.o_form_button_edit').toggleClass('o_hidden', false);
                }
            } else {
                this.$buttons.find('.o_form_button_edit').toggleClass('o_hidden', false);
            }
            var edit_mode = (this.mode === 'edit');
            this.$buttons.find('.o_form_buttons_edit')
                .toggleClass('o_hidden', !edit_mode);
            this.$buttons.find('.o_form_buttons_view')
                .toggleClass('o_hidden', edit_mode);
            console.log(this)

        },
    });

    // var _t = core._t;
    // var QWeb = core.qweb;
    // console.log("------------------------------loaded1")
    // FormView.include({
    //     init: function () {
    //         this._super.apply(this, arguments);
    //         console.log(this.$buttons)
    //         // this.$el.removeClass('o_form_button_edit');
    //         if (this.model == 'sale.secondary') {
    //             if (this.get_fields_values().state != 'draft') {
    //                 this.$buttons.find('.o_form_button_edit').css({"display": "none"});
    //             } else {
    //                 this.$buttons.find('.o_form_button_edit').css({"display": ""});
    //             }
    //         }
    //
    //     }
    // });
});