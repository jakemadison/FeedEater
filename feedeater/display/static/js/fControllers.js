
var fControllers = angular.module('fControllers', ['ngSanitize']);


fControllers.controller("MainController", function($scope){

    $scope.message = 'this is a message from scope!~';

    $scope.templates =
    [ { name: 'template1.html', url: '/static/angulartemplates/angularentries.html'},
      { name: 'template2.html', url: 'template2.html'} ];
    $scope.template = $scope.templates[0];


});



fControllers.controller("EntriesCtrl", ['$scope', '$http', function($scope, $http){

    $scope.user = USER_ID;
    $scope.page = PAGE_ID;

    $scope.message = 'this is the entries controller...';
    $scope.no_entries = false;
    $scope.compressed = "entrycontent fullview";  // "entrycontent compview"

    $scope.myData = {};
    $scope.myData.getEntries = function() {
        var responsePromise = $http.get("/recalculate_entries", {params: {
                page_id: PAGE_ID,
                star_only: false
            }});

        responsePromise.success(function(data, status, headers, config) {
            $scope.myData.fromServer = data;
            $scope.no_entries = data.e.length == 0;
            $scope.pager = data.pager;
            console.log(data);
        });

        responsePromise.error(function(data, status, headers, config) {
            alert("AJAX failed!");
        });
    };

    $scope.myData.getEntries();  // initialize entries on load

}]);



fControllers.controller("SubCtrl", ['$scope', '$http', function($scope, $http){

    $scope.message_new = 'this is the entrY! controller...';
    $scope.user = USER_ID;
    $scope.page = PAGE_ID;

    $scope.subData = {};
    $scope.subData.getSubs = function() {
        var responsePromise = $http.get("/get_user_subs", {params: {
            }});

        responsePromise.success(function(data, status, headers, config) {
            $scope.subData.fromServer = data;
            console.log(data);
        });

        responsePromise.error(function(data, status, headers, config) {
            alert("AJAX failed!");
        });
    };

    $scope.subData.toggleFeed = function(userFeedId) {

        var responsePromise = $http.get("/change_active", {params: {
                uf_id: userFeedId
            }});

        responsePromise.success(function(data, status, headers, config) {

            var sub_array = $scope.subData.fromServer.subs;

            for (var i=0; i<sub_array.length; i++) {
                if (sub_array[i].uf_id == userFeedId) {
                    sub_array[i].active = !sub_array[i].active;
                }
            }
        });

        responsePromise.error(function(data, status, headers, config) {
            alert("AJAX failed!");
        });

    };


    $scope.subData.getSubs();

}]);


fControllers.controller("PagerCtrl", ['$scope', function($scope){

    $scope.f_message = 'i am f_message!';

}]);