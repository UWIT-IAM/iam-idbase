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

app.factory('TimeoutSvc', function(){
    var _this = this;
    _this.reloadFunc = function() {window.location.reload();};

    return {
        setReloadFunc: function(func) { _this.reloadFunc = func; },
        reload: function() {_this.reloadFunc();},
        showTimeout: function() {
            $('#timeoutModal')
                .modal('show')
                .on('shown.bs.modal', function() { $('#timeoutModal').find('button.btn-primary').focus();
            });
        }
    };
});

app.controller('TitleCtrl', ['TitleSvc', function(TitleSvc){
    var _this = this;
    this.Page = TitleSvc;
}]);

app.controller('TimeoutCtrl', ['TimeoutSvc', function(TimeoutSvc){
    this.reload = function() {
        TimeoutSvc.reload();
    };
}]);

app.directive('setFocus', function($timeout) {
  return function(scope, element, attrs) {
    scope.$watch(attrs.setFocus,
      function (conditional) {
        $timeout(function() {
            conditional && element[0].focus();
        });
      },true);
  };
});
