var fControllers = angular.module('fControllers', ['ngSanitize']);


fControllers.controller("EntriesCtrl", ['$scope', '$http', 'makeRequest', function($scope, $http, makeRequest){

    $scope.user = USER_ID;
    $scope.page = PAGE_ID;

    $scope.message = 'this is the entries controller...';
    $scope.no_entries = false;
    $scope.compressed = "entrycontent fullview";  // "entrycontent compview"

    $scope.myData = {};
    $scope.myData.getEntries = function() {

        makeRequest.pullEntryData(PAGE_ID, false)
            .then(function(data){
                console.log(data);
            });
    };

    $scope.$on('entriesUpdated', function(){
                var Edata = makeRequest.getUpdatedEntries();
                $scope.myData.fromServer = Edata;
                $scope.no_entries = Edata.e.length == 0;
                $scope.pager = Edata.pager;
    })

    $scope.$on('feedChange', function(){
                $scope.myData.getEntries();
    })


    $scope.myData.getEntries();  // initialize entries on load

}]);


fControllers.controller("SubCtrl", ['$scope', '$http', 'makeRequest', function($scope, $http, makeRequest){

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

        makeRequest.toggleFeed(userFeedId)
            .then(function(data){
                console.log(data);

                var sub_array = $scope.subData.fromServer.subs;

                for (var i=0; i<sub_array.length; i++) {
                    if (sub_array[i].uf_id == userFeedId) {
                        sub_array[i].active = !sub_array[i].active;
                    }
                }
            });

    };

    $scope.subData.singleFeed = function(userFeedId) {

        makeRequest.singleFeed(userFeedId)
            .then(function(data){
                console.log(data);

                var sub_array = $scope.subData.fromServer.subs;

                for (var i=0; i<sub_array.length; i++) {
                    if (sub_array[i].uf_id != userFeedId) {
                        sub_array[i].active = false;
                    }
                    else {
                        sub_array[i].active = true;
                    }
                }
            });

    };


    //init our subs:
    $scope.subData.getSubs();

}]);


fControllers.controller("PagerCtrl", ['$scope', 'makeRequest', function($scope, makeRequest){

    $scope.$on('pagerUpdated', function() {
        console.log('i detected that the pager was updated!');
        $scope.pager = makeRequest.getPager();
    });

    $scope.pager_functions = {};

    $scope.pager_functions.advance_page = function(amount) {

        console.log('this is page id: ');
        console.log(PAGE_ID);
        PAGE_ID = parseInt(PAGE_ID) + amount;
        makeRequest.notifyPageChange();
        $("html, body").animate({ scrollTop: 0 }, "fast");  // this might get annoying..
    };


}]);