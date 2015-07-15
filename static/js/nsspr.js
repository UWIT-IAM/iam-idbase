var nsspr_api_netid = 'api/netid/';

var app = angular.module('nssprApp', []);

app.config(['$httpProvider', function ($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

// controller for the netid
app.controller('NetidCtrl', ['$http', '$log', function ($http, $log) {
    var _this = this;
    // netid valid name characters
    this.valid_chars = /^[\w_]+$/;
    this.fieldMax = 64;

    this.netid_info = {
    };

    // forms
    this.show_idform = 1;
    this.show_id = 0;
    this.show_smsform = 0;
    this.show_emailform = 0;
    this.show_codeform = 0;

    this.sms_number = '***.***.*123';
    this.email_address = 'z***12@gm***.com';
    this.code = '';
    this.code_message = '';

    this.getStatus = null;
    this.getNetidInfo = function () {
        $log.info('about to get ' + nsspr_api_netid + _this.netid.id );
        $http.get(nsspr_api_netid + _this.netid.id )
            .success(function (data, status) {
                _this.netid_info = data;
                _this.getStatus = status;
                $log.info( _this.netid_info);
                _this.show_idform = 0;
                _this.show_id = 1;
                _this.show_smsform = 1;
            })
            .error(function (data, status) {
                $log.info('name get status returned error, status ' + status);
                _this.getStatus = status;
            });
    };

    this.sendSMS = function () {
        $log.info('send sms');
        _this.show_smsform = 0;
        _this.code_message = 'Secret code sent to ' + _this.sms_number;
        _this.show_codeform = 1;
    };
    this.skipSMS = function () {
        $log.info('skip sms');
        _this.show_smsform = 0;
        _this.show_emailform = 1;
    };
    this.sendEmail = function () {
        $log.info('send Email');
        _this.show_emailform = 0;
        _this.code_message = 'Secret code sent to ' + _this.email_address;
        _this.show_codeform = 1;
    };
    this.skipEmail = function () {
        $log.info('skip sms');
        _this.show_emailform = 0;
        // _this.show_emailform = 1;
    };
    this.setSMSCode = function () {
        $log.info('recv sms code: ' + _this.netid.code);
    };

}]);

