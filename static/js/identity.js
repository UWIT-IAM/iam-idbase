var app = angular.module('identityApp', []);


// disable security checks on html
//app.config(function($sceProvider) {
//	$sceProvider.enabled(false);
//    });

// add xsrf protection as needed
app.config(['$httpProvider', function ($httpProvider) {
	    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
	    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
	}]);


app.factory('TitleSvc', function(){
  return {
      title: function() {
          if ($('h1') && $('h1')[0] && $('h1')[0].innerText) {
              return $('h1')[0].innerText;
          }
          return 'Identity.UW';
      }
  };
});

app.controller('TitleCtrl', ['TitleSvc', function(TitleSvc){
    var _this = this;
    this.Page = TitleSvc;
}]);