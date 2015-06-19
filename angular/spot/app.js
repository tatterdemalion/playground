var app = angular.module('unifont', []);

app.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
});

app.controller('unitextController', function($scope){
  $scope.foo = function(){
    if ($scope.text) {
      return $scope.text.replace(/a/g, 'b');
    }
  };

});
