// javascript file for demo purposes only
var app = angular.module('identityApp');

app.controller('MakeErrorCtrl', function(errorService){
    this.doIt = function() {
        errorService.showError();
    };
});


app.controller('MakeTimeoutCtrl', function(errorService){
    this.doIt = function() {
        errorService.showTimeout();
    };
});
