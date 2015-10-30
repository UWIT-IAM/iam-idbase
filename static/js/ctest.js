var nsspr_api_netid = 'api/netid/';
var apiRecoveryInfo = 'api/recoveryinfo/';
var nsspr_api_sendcode = 'api/sendcode/';
var nsspr_api_checkcode = 'api/checkcode/';
var nsspr_api_sendemail = 'api/sendemail/';
var nsspr_api_accepttnc = 'api/accepttnc/';

var app = angular.module('identityApp', ['ng']);

//this enables the html location hash magic
app.config(['$locationProvider', function($locationProvider) {
// Configure existing providers
    $locationProvider.html5Mode({
        enabled: true,
        hashPrefix: '!',
        requireBase: false
    });

}]);

app.directive('uwPhoneNumber', ['$filter', function($filter) {
    console.log('uwPhoneNumber init.');
    return {
       require: 'ngModel',
       scope: {
          sms_number: '=ngModel',
          sms_valid: '=uwPhoneValid',
       },
       link: function(scope, element, attrs, ctrl) {
          scope.$watch('sms_number', function(newValue) {
             num = String(newValue).replace(/[^0-9]+/g, '');
             fnum = $filter('phonenumber')(num);
             scope.sms_valid = 0;
             if (num.length==10) scope.sms_valid = 1;
             console.log('fnum = ' + fnum + ' v=' + scope.sms_valid);
             scope.sms_number = fnum;
          }, true);
       },
    };
}]).filter('phonenumber', function() {
    return function(num) {
       if (!num) return '';
       num = String(num);
       var fnum = num;
       var ac = num.substring(0,3);
       var n3 = num.substring(3,6);
       var n4 = num.substring(6,10);
       if (n3) fnum = ('(' + ac + ') ' + n3);
       if (n4) fnum += ('-' + n4);
       return fnum;
    };
});

pageno = 0;
lastpage = -1;

// controller for the configure page
app.controller('ConfigureCtrl', ['$http', '$log', '$location', '$rootScope', 'ErrorSvc',
                    function ($http, $log, $location, $rootScope, ErrorSvc) {
    var _this = this;
    // netid valid name characters
    this.valid_chars = /^[\w_]+$/;
    this.fieldMax = 64;

    $log.info('configure model loaded ');

    newPage = function(n) {
       pageno += 1;
       console.log('set hash page to ' + pageno + ' page=' + n);
       $location.hash(n);
    };

    this.sms_number = '';
    this.sms_valid = 0;

    this.netid = '';
    this.email_address = '';
    this.email_address_unconfirmed =0;

    // views
    this.codeform_err = 0;
    this.show_ev = 0;

    this.code = '';
    this.code_message = '';

    this.bad_sms = 0;
    this.need_tnc = 0;
    this.tnc_box = 0;
    this.tnc_checked = function() {
        console.log('tnc = ' + this.tnc_box);
        if (!this.tnc_box) return;
        data = '';
        $http.put(nsspr_api_accepttnc, data )
            .success(function (data, status) {
                $log.info( 'put tnc accept = ' + status);
            })
            .error(function (data, status) {
                $log.info('tnc accept returned error, status ' + status);
                _this.errorFunc(data, status);
            });
    };

    this.errorFunc = ErrorSvc.handleError;
  
    /* Handle the back button.
     * The app doesn't really change pages.  It only shows different views.
     * We set a hash on each view change and use this method to determins
     * the sensible thing to do for 'BACK'.
     */

    $rootScope.$on('$locationChangeSuccess', function(event, newUrl, oldUrl) {
      var hashno = $location.hash();
      var oldHash = oldUrl.substr(oldUrl.length - 1);
      console.log('location change, hash = ' + $location.hash());

      if (pageno == lastpage) {
         console.log('BACK BUTTON');

         if (oldHash == '2') {   // user asked for email/sms code
           console.log('switch back to code sms number page');
           _this.show_smsForm = 1;
         } else if (hashno == '#/3') {   // user asked for email addr
           console.log('switch back to code email addr page');
           _this.show_emailForm = 1;
         } else {
            console.log('switch back to main page');
            _this.showMain();
         }
      } else {
         console.log('LOC-was a new page button');
         lastpage = pageno;
         console.log('page now ' + _this.page );
      }
    });

    this.getStatus = null;

    this.getRecoveryInfo = function(){
        _this.recoveryInfo = {sms: null, sms_unverified: null, email: null, email_unverified: null, need_tnc: null};
        _this.recoveryInfoStatus = null;
        $log.info('about to get ' + apiRecoveryInfo);
        $http.get(apiRecoveryInfo)
            .success(function (data, status) {
                _this.recoveryInfo = data;
                _this.recoveryInfoStatus = status;
                 $log.info( _this.recoveryInfo, status);
            })
            .error(function(data, status) {
                _this.recoveryInfoStatus = status;
                _this.errorFunc(data, status);
            });
    };

    // show main page.  Needs refresh of recovery info
    this.showMain = function () {
        _this.getRecoveryInfo();
        _this.page = 'main';
        if(/^email_verify_/.test(nsspr_initstate)){
            _this.page = 'emailVerified';
            _this.emailVerifiedStatus = nsspr_initstate == 'email_verify_success' ? 'success' : 'failure';
            nsspr_initstate = '';
        }
    };

    this.askDelete = function(type){
        _this.aboutToDelete = {
            type: type,
            value: _this.recoveryInfo[type]
        };
        $('#deleteModal')
            .modal('show')
            .on('shown.bs.modal', function() {
                $('#deleteModal').find('button.btn-primary').focus();});
    };

    this.deleteRecoveryInfo = function(type) {
        $log.info('about to delete ' + apiRecoveryInfo + type);
        $http.delete(apiRecoveryInfo+type)
            .success(function(data, status) {
                $log.info('successfully deleted');
                _this.showMain();
            })
            .error(function(data, status) {
                $log.info('couldn\'t delete');
                _this.deleteStatus = status;
                _this.errorFunc(data, status);
            });
    };

    this.showSMSForm = function () {
        $log.info('show sms');
        _this.page = 'sms';
        _this.sms_number = _this.recoveryInfo.sms;
        newPage(1);
        
    };
    this.showEmailForm = function () {
        $log.info('show email');
        _this.page = 'email';
        _this.email_address = _this.recoveryInfo.email;
        newPage(1);
    };

    this.showCodeForm = function(){
        _this.page = 'code';
        _this.code = '';
        newPage(1);
    };

    this.sendSMS = function () {
        // note: the submit button is not active until 10 digits
        $log.info('send sms:'+_this.sms_number);
        num = _this.sms_number.replace(/[^0-9]/g,'');
        data = {'sms_number': num};
        $http.post(nsspr_api_sendcode, data )
            .success(function (data, status) {
                _this.getStatus = status;
                $log.info( _this.getStatus);
                _this.code_message = 'Recover code sent to ' + _this.sms_number;
                _this.showCodeForm();
            })
            .error(function (data, status) {
                $log.info('name get status returned error, status ' + status);
                _this.getStatus = status;
                _this.errorFunc(data, status);
            });
    };
    this.sendEmail = function () {
        $log.info('send Email');
        data = {'email_address': _this.email_address};
        $http.post(nsspr_api_sendemail, data )
            .success(function (data, status) {
                _this.getStatus = status;
                $log.info( _this.getStatus);
                _this.page = 'emailSent';
                _this.email_address_unconfirmed = 1;
                newPage(3);
            })
            .error(function (data, status) {
                $log.info('name get status returned error, status ' + status);
                _this.emailForm.$setPristine();
                _this.getStatus = status;
                $log.info(_this.getStatus);
                _this.errorFunc(data, status);
            });
    };
    this.verifyCode = function () {
        $log.info('verify the code: ' + _this.code.trim());
        data = {'code': _this.code};
        $http.post(nsspr_api_checkcode, data )
            .success(function (data, status) {
                _this.getStatus = status;
                $log.info( _this.getStatus);
                _this.page = 'codeVerified';
            })
            .error(function (data, status) {
                $log.info('name get status returned error, status ' + status);
                _this.getStatus = status;
                _this.codeform_err = 1;
                _this.errorFunc(data, status);
            });
    };

   // clear the error messages on input focus
   this.clearErrors = function() {
       _this.codeform_err = 0;
   };

    $log.info('configure: initstate = ' + nsspr_initstate);
    _this.showMain();

}]);
