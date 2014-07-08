var eServices = angular.module('eServices', []);

eServices.factory('makeRequest', ['$http', '$rootScope', function($http, $rootScope) {

    var current_paging = {'has_next': false, 'has_prev': false};
    var entries = {};
    var user_preferences = {"compressed": false};

    var progress_data = {'total_entry_count': 0, 'current_offset': 0, 'page_len': 0};


    //public methods:


    //messageBar methods:
    var checkProgress = function() {

        var promise = $http({
           method: 'GET',
            url: '/get_progress'
        });

        return promise.then(
            function(data) {
              return data;
            }
        );
    };



    //toolbar methods:
    var getUserPreferences = function() {
      return user_preferences;
    };

    var refreshFeeds = function() {
      var promise = $http({
            method: 'GET',
            url: '/refreshfeeds'
      });

        return(promise.then(handleRefreshSuccess));

    };


    var addFeed = function(url) {
        console.log("addFeed service with url: ", url);

        var promise = $http({
            method: 'POST',
            url: '/add_feed',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            data: $.param({url: url})
        });

        return(promise.then(handleAddFeedResult));

    };

    var requestSubUpdate = function() {
      $rootScope.$broadcast("requestSubUpdate");
    };



    //Entry Methods:
    var getEntries = function(page_id, star_only) {
        console.log('getEntries method of makeRequest function running');

        var promise = $http({
            method: 'GET',
            url: '/recalculate_entries',
            params: {page_id: page_id, star_only: star_only}
        });

        return (promise.then(handleSuccess));
    };

    var requestCategoryFeed = function(category) {
        console.log('i am firing a requestCategory broadcast because of entries! data: ', category);
        $rootScope.$broadcast("requestCategoryFeed", category);
    };



    //Feed Methods:
    var toggleFeed = function(feed_id) {
        console.log('toggleFeed method of makeRequest function running');

        var promise = $http({
            method: 'GET',
            url: '/change_active',
            params: {uf_id: feed_id}
        });

        return (promise.then(handleFeedSuccess));
    };

    var allFeeds = function() {
            var promise = $http({
            method: 'GET',
            url: '/allfeeds'
        });

        $rootScope.$broadcast("toolbarFeedChange");

        return (promise.then(handleFeedSuccess));
    };



    var singleFeed = function(feed_id) {
        console.log('toggleFeed method of makeRequest function running');

        var promise = $http({
            method: 'GET',
            url: '/onefeedonly',
            params: {uf_id: feed_id}
        });

        return (promise.then(handleFeedSuccess));
    };

    var categoryFeed = function(category) {
        console.log('categoryFeed method of makeRequest function running');

        console.log(category);
        var promise = $http({
            method: 'GET',
            url: '/togglecategory',
            params: {catname: category}
        });

        return (promise.then(handleFeedSuccess));
    };



    //Pager Methods:
    var notifyPageChange = function() {
        console.log('i am firing a feedChange broadcast because of the pager!');
        $rootScope.$broadcast("feedChange");
        $rootScope.$broadcast('progressbarUpdate', progress_data);
    };


    // getters:
    var getPager = function() {
        console.log('getting pager');
        return current_paging;
    };

    var getUpdatedEntries = function() {
        console.log('getting updated entries');
        return entries;
    };



    //private methods:

    function handleAddFeedResult(result) {
        console.log("addFeed result happened!");
        console.log("result: ", result);

        return result.data;
    }

    function handleRefreshSuccess() {
        console.log("refresh has been successful!");
        $rootScope.$broadcast("feedChange");
        $rootScope.$broadcast("entryRefreshInit")
    }

    function handleFeedSuccess(data) {
        console.log('i am firing a feedChange broadcast!');
        $rootScope.$broadcast("feedChange");
        return data.data;
    }

    function handleSuccess(data) {
        var paging_response = data.data.pager;

        if (paging_response.has_next != current_paging.has_next ||
            paging_response.has_prev != current_paging.has_prev) {
                current_paging = paging_response;
                console.log('i am firing a pagerUpdated broadcast!');
                $rootScope.$broadcast("pagerUpdated");
        }
        entries = data.data;
        user_preferences.compressed = data.data.compressed_view;
        progress_data.total_entry_count = data.data.total_records;
        progress_data.page_len = data.data.e.length;

        console.log('i am firing a entriesUpdated broadcast!');
        $rootScope.$broadcast("entriesUpdated");
        $rootScope.$broadcast('progressbarUpdate', progress_data);
        return data.data;
    }


    //public API of service:
    return({
        pullEntryData: getEntries,
        getPager: getPager,
        getUpdatedEntries: getUpdatedEntries,
        toggleFeed: toggleFeed,
        notifyPageChange: notifyPageChange,
        singleFeed: singleFeed,
        categoryFeed: categoryFeed,
        requestCategoryFeed: requestCategoryFeed,
        getUserPreferences: getUserPreferences,
        refreshFeeds: refreshFeeds,
        allFeeds: allFeeds,
        addFeed: addFeed,
        requestSubUpdate: requestSubUpdate,
        checkProgress: checkProgress

    });

}]);




