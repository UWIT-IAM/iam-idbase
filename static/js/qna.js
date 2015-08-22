var nsspr_api_checkqna = 'api/checkqna/';

var app = angular.module('qnaApp', []);

app.config(['$httpProvider', function ($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

// controller for the configure page
app.controller('QnaCtrl', ['$http', '$log', function ($http, $log) {
    var _this = this;
    // netid valid name characters
    this.valid_chars = /^[\w_]+$/;
    this.fieldMax = 64;

    $log.info('the model is qna ');

    this.qna = [];

    this.checkQnA = function () {
        $log.info('In qna.js, checkQnA');
        $log.info(_this.qna)
        for (i=0;i<_this.qna.length;i++) {
           $log.info('ans to ' + i + ' is ' + _this.qna[i]);
        }
        window.location = 'password';
    };


    this.checkQnAforreal = function () {
        $log.info('check qna');
        data = {'lname': _this.gate.lname, 'bdate': _this.gate.bdate, 'eid': _this.gate.eid, 'sid': _this.gate.sid};
        $log.info (data);
        $http.post(recover_api_checkgate + _this.netid.id, data )
            .success(function (data, status) {
                _this.getStatus = status;
            })
            .error(function (data, status) {
                $log.info('gate info status returned error, status ' + status);
                _this.getStatus = status;
            });
    };


}]);

