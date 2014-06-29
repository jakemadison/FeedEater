FeedEaterApp.controller("MainController", function($scope){

    $scope.message = 'this is a message from scope!~';

    $scope.templates =
    [ { name: 'template1.html', url: '/static/angulartemplates/angularentries.html'},
      { name: 'template2.html', url: 'template2.html'} ];
    $scope.template = $scope.templates[0];


});

FeedEaterApp.factory('generateEntries', ['$http', function($http) {

    var getEntries = function() {

        return {e: "entry!"};
    }

    return function(item, event) {

        var responsePromise = $http.post("/recalculate_entries", {
            current_page: 1,
            active_list: [1],
            star_only: false
        });

        responsePromise.success(function(data, status, headers, config) {
            return data;

            });

        responsePromise.error(function(data, status, headers, config) {
            alert("AJAX failed!");
            });
        }

    }]);




FeedEaterApp.controller("EntriesCtrl", ['$scope', '$http', function($scope, $http){

    $scope.user = USER_ID;
    $scope.page = PAGE_ID;

    $scope.message = 'this is the entries controller...';
    $scope.no_entries = false;
    $scope.compressed = "entrycontent fullview";  // "entrycontent compview"

    $scope.myData = {};
    $scope.myData.doClick = function() {
        var responsePromise = $http.get("/recalculate_entries", {params: {
                page_id: PAGE_ID,
                star_only: false
            }});

        responsePromise.success(function(data, status, headers, config) {
            $scope.myData.fromServer = data;
            console.log(data);
        });

        responsePromise.error(function(data, status, headers, config) {
            alert("AJAX failed!");
        });
    }


}]);



FeedEaterApp.controller("EntryController", function($scope){

    $scope.message_new = 'this is the entrY! controller...';

});