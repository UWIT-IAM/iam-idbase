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
        $log.info('checkQnA');
        $log.info(_this.qna)
        for (i=0;i<_this.qna.length;i++) {
           $log.info('ans to ' + i + ' is ' + _this.qna[i]);
        }
    };

}]);

