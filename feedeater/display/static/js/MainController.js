app.controller("MainController", function($scope){

    $scope.message = 'this is a message from scope!~';

    $scope.templates =
    [ { name: 'template1.html', url: '/static/angulartemplates/angularentries.html'},
      { name: 'template2.html', url: 'template2.html'} ];
  $scope.template = $scope.templates[0];


});



app.controller("EntriesController", function($scope){

    $scope.message = 'this is the entries controller...';

});



app.controller("EntryController", function($scope){

    $scope.message2 = 'this is the entrY! controller...';

});