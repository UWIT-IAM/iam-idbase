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
          if ($('h1') && $('h1')[0]){
              if($('h1')[0].innerText){ return $('h1')[0].innerText;}
              if($('h1')[0].textContent){ return $('h1')[0].textContent;}
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

// Our service to handle general errors (401 - invalid session, 500 - server error)
app.factory('ErrorSvc', ['$log', 'TimeoutSvc', function($log, TimeoutSvc){
    var _this = this;
    this.state = {isErrorSet: false};
    this.handleError = function(data, status) {
        if (status == 401) {
            $log.info('expired session, ', data);
            TimeoutSvc.showTimeout();
        } else if (status == 500) {
            $log.info('500 error from server,', data);
            _this.state.isErrorSet = true;
        }
    };

    return {
        handleError: _this.handleError,
        state: _this.state
    };
}]);

app.controller('ErrorCtrl', ['ErrorSvc', function(ErrorSvc){
    this.errorState = ErrorSvc.state;
}]);

// This only works well when there's only one set-focus directive in the DOM (which we do through ng-if)
// This could probably be made better or supposedly get declared differently with HTML5.
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
