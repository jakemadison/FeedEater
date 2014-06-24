app.controller("MainController", function($scope){

    $scope.message = 'this is a message from scope!~';

    $scope.templates =
    [ { name: 'template1.html', url: '/static/angulartemplates/angularentries.html'},
      { name: 'template2.html', url: 'template2.html'} ];
  $scope.template = $scope.templates[0];


});

