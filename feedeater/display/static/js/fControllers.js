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


    $scope.myData.requestCategoryFeed = function(category) {
        console.log('-- request for category initiated, data: ', category);
        makeRequest.requestCategoryFeed(category);
    };


    //listeners:
    $scope.$on('entriesUpdated', function(){
                var Edata = makeRequest.getUpdatedEntries();
                $scope.myData.fromServer = Edata;
                $scope.no_entries = Edata.e.length == 0;
                $scope.pager = Edata.pager;
    });

    $scope.$on('feedChange', function(){
                $scope.myData.getEntries();
    });


    //init our entries:
    $scope.myData.getEntries();  // initialize entries on load

}]);



fControllers.controller("ToolbarCtrl", ['$scope', '$timeout', 'makeRequest', function($scope, $timeout, makeRequest){

    $scope.userId = parseInt(USER_ID);

    $scope.message = "I am the toolbar Ctrl!";

    $scope.refreshFeeds = function() {
      console.log("refreshFeeds activated, page: ", PAGE_ID);

        makeRequest.refreshFeeds()
        .then(function(){
                console.log("refresh feeds completed! Let's update Entries!");
            });



    };


    $scope.all_feeds = function() {
      console.log("allFeeds activated, page: ", PAGE_ID);

        makeRequest.allFeeds()
        .then(function(){
                console.log("all feeds completed! Let's update Entries!");
            });

    };

    $scope.inputText = '';
    $scope.errorMessage = false;
    $scope.infoMessage = false;
    $scope.successMessage = false;
    $scope.messageText = '';

    $scope.add_feed = function() {
      console.log("add_feed has begun!");
      console.log('input text: ', this.inputText);

        makeRequest.addFeed(this.inputText)
            .then(function(result) {
                console.log("controller received: ", result);


                switch (result.category){
                    case "error":
                        $scope.errorMessage = true;
                        $scope.messageText = result.msg;
                        break;

                    case "info":
                        $scope.infoMessage = true;
                        $scope.messageText = result.msg;
                        break;

                    case "success":
                        $scope.successMessage = true;
                        $scope.messageText = result.msg;
                        makeRequest.requestSubUpdate();  //notify subs that feeds have changed
                        makeRequest.notifyPageChange();  //notify entries that feeds have updated
                        break;

                    default:
                        console.log("message type was not understood by controller");
                }

                $timeout(function() {
                    $scope.errorMessage = false;
                    $scope.infoMessage = false;
                    $scope.successMessage = false;
                    $scope.messageText = '';
                }, 3000);

            });

    };



    // listeners:
    $scope.$on("entriesUpdated", function() {

        console.log("toolbar heard about entries!");
        $scope.user_preferences = makeRequest.getUserPreferences();
        console.log("view status: ", $scope.user_preferences.compressed);

    });



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


    $scope.isOn = function(cat) {

        var sub_array = $scope.subData.fromServer.subs;
        var category_on = false;
        var result;

        if (typeof sub_array === 'undefined') {
            result = 'label-default';
            return result;
        }

        for (var i=0; i<sub_array.length; i++) {
            if (sub_array[i].category == cat) {
                if (sub_array[i].active === true) {
                    category_on = true;
                    break;
                }
            }
        }

        if (category_on) {
            result = 'label-success';
        }

        return result;

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

    $scope.subData.categoryFeed = function(category) {

        console.log('categoryFeed function started: ', category);

        var sub_array = $scope.subData.fromServer.subs;

        makeRequest.categoryFeed(category)
            .then(function(data){
                console.log('categoryFeed request finished: ', data);

                for (var i=0; i<sub_array.length; i++) {
                    if (sub_array[i].category == category) {
                        sub_array[i].active = data.all;
                    }
                }
            });
    };


    //listeners:
    $scope.$on("requestCategoryFeed", function(event, c) {
       console.log("i detect a requestCategory broadcast! data: ", c);
        $scope.subData.categoryFeed(c);
    });

    $scope.$on("toolbarFeedChange", function() {

        var sub_array = $scope.subData.fromServer.subs;
        for (var i=0; i<sub_array.length; i++) {
            sub_array[i].active = true;
        }
    });

    $scope.$on("requestSubUpdate", function() {
       console.log("sub update was requested");
        $scope.subData.getSubs();
    });


    //init our subs:
    $scope.subData.getSubs();

}]);


fControllers.controller("PagerCtrl", ['$scope', 'makeRequest', function($scope, makeRequest){

    $scope.pager_functions = {};

    $scope.pager_functions.advance_page = function(amount) {

        console.log('this is page id: ');
        console.log(PAGE_ID);
        PAGE_ID = parseInt(PAGE_ID) + amount;
        makeRequest.notifyPageChange();
        $("html, body").animate({ scrollTop: 0 }, "fast");  // this might get annoying..
    };


    //listeners:
    $scope.$on('pagerUpdated', function() {
        console.log('i detected that the pager was updated!');
        $scope.pager = makeRequest.getPager();
    });


    $scope.$on('keypress', function(e, type){
        console.log("detected keypress: ", type);

        if (type === "left" && $scope.pager.has_prev) {
            $scope.pager_functions.advance_page(-1);
        }
        else if (type === "right" && $scope.pager.has_next) {
            $scope.pager_functions.advance_page(1);
        }

    });


}]);