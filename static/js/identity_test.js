describe('identity common tools', function() {

  beforeEach(module('identityApp'));

  // controller injector
  var $controller;
  beforeEach(inject(function(_$controller_) {
    $controller = _$controller_;
  }));

  beforeEach(inject(function() {
    var $injector = angular.injector(['identityApp']);
    TitleSvc = $injector.get('TitleSvc');
    ErrorSvc = $injector.get('ErrorSvc');
    TimeoutSvc = $injector.get('TimeoutSvc');
  }));

  beforeEach(inject(function (_$http_, _$log_, _$location_, _$rootScope_, _ErrorSvc_) {
        $http = _$http_;
        $log = _$log_;
        $location = _$location_;
        $rootScope = _$rootScope_;
        ErrorSvc = _ErrorSvc_;
    }));

  describe('common controllers', function(){

    it('title controller returns default title', function() {
      var ctrl = $controller('TitleCtrl', { TitleSvc: TitleSvc} );
      expect(ctrl).toBeDefined();
      expect(ctrl.Page.title()).toEqual('Identity.UW');
    });

    it('has timeout controller', function() {
      var ctrl = $controller('TimeoutCtrl', {TimeoutSvc: TimeoutSvc});
      expect(ctrl).toBeDefined();
    });

    it('error factory sets error state', function() {
      var ctrl = $controller('ErrorCtrl', {ErrorSvc: ErrorSvc});
      expect(ctrl).toBeDefined();
      ErrorSvc.handleError('aaa', 404);
      expect(ErrorSvc.state.isErrorSet).not.toBeTruthy();
      ErrorSvc.handleError('aaa', 500);
      expect(ErrorSvc.state.isErrorSet).toBeTruthy();
    });


  });
});
