describe('identity common tools', function() {

  beforeEach(module('identityApp'));

  // controller injector
  var $controller;
  beforeEach(inject(function(_$controller_) {
    $controller = _$controller_;
  }));

  describe('common controllers', function(){

    it('has title controller', function() {
      var ctrl = $controller('TitleCtrl');
      expect(ctrl).toBeDefined();
    });

    it('has timeout controller', function() {
      //spec body
      var ctrl = $controller('TimeoutCtrl');
      expect(ctrl).toBeDefined();
    });

    it('has error controller', function() {
      //spec body
      var ctrl = $controller('ErrorCtrl');
      expect(ctrl).toBeDefined();
    });

  });
});
