var fControllers = angular.module('fControllers', ['ngSanitize']);


fControllers.controller("messagebarCtrl", ['$scope', '$http', '$timeout', 'makeRequest',
                                                function($scope, $timeout, $http, makeRequest){

    $scope.pre_login = true;

    $scope.user = USER_ID;
    $scope.nickname = USER_NICKNAME;
    $scope.page = PAGE_ID;
    $scope.hash = USER_HASH;
    $scope.role = parseInt(USER_ROLE);
    $scope.avatar_size = '150';

    $scope.gravatar = 'http://www.gravatar.com/avatar/' + USER_HASH + '?d=mm&s=' + $scope.avatar_size;
    $scope.entry_progress = 0;
    $scope.total_entry = 0;

    //progress bar stuff:
    $scope.bar = {'progress': 100, 'remaining': 0};

    $scope.$on('progressbarUpdate', function(e, data) {
       console.log("received progressbarupdate notice", data);

        var portion = (parseInt(PAGE_ID))*data.page_len;
        var left_section = (portion/data.total_entry_count)*100;

        if (left_section >= 100) {
            $scope.bar.progress = 100;
            $scope.bar.remaining = 0;
        }
        else {
            $scope.bar.progress = left_section;
            $scope.bar.remaining = 100 - $scope.bar.progress;
        }


        $scope.total_entry = data.total_entry_count;
        $scope.entry_progress = portion;

        //page*len = number of total entries we've looked at
        //total = total number of entries

        //(page*len)/total * 100 = left side
        //100 - left side = right side
        //

    });




    $scope.$on('entryRefreshInit', function() {

        console.log('messagebar: I have detected a refresh occurring.  I should probably deal with it.');

//        $timeout(function() {
//            console.log('I am a timeout!!');
//        }, 1000);

    });




}]);




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

    $scope.markAsRead = function(id) {
        makeRequest.markAsRead(id);

        //and when complete, probably change the entry object unread status of the entry.
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



fControllers.controller("ToolbarCtrl", ['$scope', '$modal', '$timeout', 'makeRequest',
                                            function($scope, $modal, $timeout, makeRequest){

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

    $scope.modal_many_feeds = function() {

        var modalInstance = $modal.open({
            templateUrl: 'modalContent.html',
            controller: modalInstanceCtrl,
            resolve: {feeds: function() {return $scope.feeds;}}
        });

        modalInstance.result.then(function(item){
            console.log('result receieved: ', item, 'adding feed...');
            $scope.add_feed(item);
        });

    };

    var modalInstanceCtrl = function($scope, $modalInstance, feeds) {
        $scope.feeds = feeds;
        $scope.choice = function(item) {
            console.log('user chose', item);
            $modalInstance.close(item);
        };
    };

    $scope.userNotifications = function(result) {
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

            // deal with multiple feeds returned
            case "multi":
                $scope.infoMessage = true;
                $scope.messageText = result.msg;
                $scope.feeds = result.f;
                $scope.modal_many_feeds();
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

    };

    $scope.add_feed = function(item) {
      console.log("add_feed has begun!");
      var feed_item = item || this.inputText;
      console.log('input text: ', feed_item);
      makeRequest.addFeed(feed_item);

    };


    // listeners:
    $scope.$on("entriesUpdated", function() {

        console.log("toolbar heard about entries!");
        $scope.user_preferences = makeRequest.getUserPreferences();
        console.log("view status: ", $scope.user_preferences.compressed);

    });

    $scope.$on('notificationBroadcast', function(e, result){
        $scope.userNotifications(result);
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

    $scope.subData.unsubscribeFeed = function(userFeedId){
        console.log('unsubscribing feed...', userFeedId);
        makeRequest.unsubscribeFeed(userFeedId);
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