var app = angular.module('identityApp', ['ng', 'ngCookies', 'ui.bootstrap', 'ngAnimate']);

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

app.service('errorService', function($log){
    var _this = this;
    _this.inactivity = {show: 0};
    _this.error = {show: 0};
    _this.showTimeout = function() {
        _this.inactivity.show++;
    };
    _this.showError = function() {
        _this.error.show++;
    };
    _this.handleError = function(response) {
        if(response.status === 401){
            $log.info('expired session');
            _this.showTimeout();
        }
        else if (response.status >= 500){
            $log.info('500 error from the server');
            _this.showError();
        }
    }
});

app.controller('TitleCtrl', ['TitleSvc', function(TitleSvc){
    var _this = this;
    this.Page = TitleSvc;
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

app.factory('LocationTabSvc', ['$location', '$window', function($location, $window){
    var _this = this;
    this.page = {name: '', history: [''], stepCounter: 1};
    this.pageBase = '';
    this.reloadPages = [];
    return {
        // Call this on successful location change. We inspect the url to see if
        // it's one of the pages in our history, and set the view accordingly.
        locationChange: function(newUrl){
            // this swallows up everything up to the last slash
            newPageName = newUrl.replace(/^.*\//, '');

            // this picks up events not handled by setPage (back/forward button or
            // visiting the link directly.
            if(newPageName != _this.page.name){
                // if the new page is in our history change the page and stepCounter
                if(_this.page.history.indexOf(newPageName) != -1) {
                    _this.page.stepCounter = _this.page.history.indexOf(newPageName) + 1;
                    _this.page.name = newPageName;
                }
            }
        },
        // Change the currently-active page, updating the history and stepCounter as necessary.
        setPage: function(name){
            // while the current page isn't the last page in our history, pop history until it is
            // before advancing.
            while(_this.page.history.indexOf(_this.page.name) != _this.page.history.length - 1){
                _this.page.history.pop();
            }

            _this.page.name = name;
            // call for a reload for any page in setReloadPages.
            if(_this.reloadPages.indexOf(name) != -1){ $window.location = _this.pageBase + name;}
            else {
                if(_this.page.history.indexOf(name) == -1){
                    _this.page.history.push(name);
                }
                _this.page.stepCounter = _this.page.history.indexOf(name) + 1;
                // this adjusts the url without reloading it.
                $location.path(_this.pageBase + name);
            }
        },
        // set the pages that, when set, will trigger a reload.
        setReloadPages: function(pages){ _this.reloadPages = pages; },
        // set the initial page, with initialPages being the collection
        // of pages allowed at load time (other than '', our main page).
        init: function(initialPages, pageBase){
            _this.pageBase = pageBase || '';
            // remove the leading /
            var locationPath = $location.path().replace(new RegExp('/' + _this.pageBase), '');
            if(initialPages && initialPages.indexOf(locationPath) != -1){
                _this.page.name = locationPath;
            }
            else if (locationPath){
                // if a path other than our initial ones, replace the current
                // url with our base.
                $location.path(_this.pageBase).replace();
            }
        },
        // This page represents the currently active page.
        page: _this.page
    };
}]);


// Usage: <uw-tooltip title="Optional Title">Tooltip description goes here</uw-tooltip>
app.directive('uwTooltip', ['$log', function($log){
    return {
        restrict: 'E',
        link: function(scope, element){
            $(element).find('a').popover();
        },
        template: function(element, attrs){
            var tooltip = $('<a href="" tabindex="0" role="button" data-placement="top" data-html="true" data-toggle="popover">' +
                '<i title="More help" class="fa fa-question-circle fa-lg uw-tooltip-icon" /></a>');
            tooltip.attr('data-content', $(element).html());
            tooltip.attr('title', attrs.title ? attrs.title : '');

            return tooltip;

        }
    };
}]);

var activateTab = function(text) {
    var tab = $("div.idbase-navbar ul li a").each(function(){
        if($(this).text().indexOf(text) > -1){
            $(this).parent().addClass('active');
        }
    });
};

app.directive('uwActiveTab', [function(){
    // Directive that will set the active tab in .idbase-navbar according
    // to the element's text.
    return {
        restrict: 'E',
        link: function(scope, element){
            activateTab($(element).text());
        }
    }
}]);


function LoginStatus($log, $http, errorService, config) {
    // Service returning information about an authenticated user.

    var loginInfo = {netid: null, name: null};
    var getNetidPromise = null;
    this.info = loginInfo;
    this.getNetid = function(){
        // return a promise for a netid. Null if not logged in.
        if(getNetidPromise) return getNetidPromise;  // only get once.
        getNetidPromise = $http.get(config.api)
            .then(function (response) {
                $log.info(response);
                loginInfo.netid = response.data.netid;
                loginInfo.name = response.data.name;
                return response.data.netid;
            })
            .catch(function (response) {
                if(response.status != 401) {
                    errorService.handleError(response);
                }
                return null;
            });
        return getNetidPromise;
    };
    if (config.defaultCheck){
        this.getNetid();
    }
}


app.provider('loginStatus', function loginStatusProvider() {
    // Provider to allow configuration of api endpoint and default service behavior
    var config = {api: 'api/loginstatus', defaultCheck: true};

    this.api = function (value) {
        config.api = value;
    };
    this.defaultCheck = function (value) {
        config.defaultCheck = value;
    };

    this.$get = ['$log', '$http', 'errorService',
        function loginStatusFactory($log, $http, errorService) {
            return new LoginStatus($log, $http, errorService, config);
        }];
});

app.controller('LoginStatusCtrl', ['loginStatus', function(loginStatus){
    this.info = loginStatus.info;
}]);

app.component('idbaseError', {
    bindings: {'show': '<'},
    controller: function(errorService){
        var ctrl = this;
        ctrl.$onInit = function() {
            ctrl.error = errorService.error;
        };
    },
    templateUrl: STATIC_ROOT + 'idbase/html/error.html'
});

app.component('idbaseTimeout', {
    controllerAs: 'timeout',
    controller: function(errorService, $window){
        var ctrl = this;
        ctrl.$onInit = function() {
            ctrl.inactivity = errorService.inactivity;
        };
        ctrl.restart = function() {
            $window.location.href = '.';
        };
    },
    templateUrl: STATIC_ROOT + 'idbase/html/timeout.html'
});

/**
 * idbase-modal creates a bootstrap modal with an id of name and an h2 title
 * of title. The modal is triggered by changes to the value pointed at by
 * show.
 */
app.component('idbaseModal', {
    bindings: {name: '@', title: '@', show: '<'},
    transclude: true,
    controllerAs: 'modal',
    controller: function($log, $timeout) {
        var ctrl = this;
        ctrl.showModal = function() {
            // wrapping in a $timeout ensures #ctrl.name will be in the DOM.
            $timeout(function(){
                var element = $('#' + ctrl.name);
                element
                    .modal('show')
                    .on('shown.bs.modal', function() {
                        var button = element.find('button.btn-primary');
                        if(button){
                            button.focus();
                        }
                    });
            });
        };
        ctrl.$onChanges = function(changes){
            if(changes.show && changes.show.currentValue){
                ctrl.showModal();
            }
        };
    },
    templateUrl: STATIC_ROOT + 'idbase/html/modal.html'
});