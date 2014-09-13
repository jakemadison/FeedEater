var eServices = angular.module('eServices', []);

eServices.factory('makeRequest', ['$http', '$rootScope', '$timeout', function($http, $rootScope, $timeout) {
    //this factory deals with holding client "state": entries, preferences, progress and the like
    //so that controllers can access when needed.
    //It also has functions for communicating with the DB.


    var current_paging = {'has_next': false, 'has_prev': false};
    var entries = {};
    var subscriptions = {};
    var feed_ids = [];
    var user_preferences = {"compressed": false};

    //used for progress bar and entry scrolling:
    var progress_data = {'total_entry_count': 0, 'current_offset': 0, 'page_len': 0};


    ///////
    //public methods:

    //entry/offset services:
    var getProgress = function() {
        //return the current #entries/page
        //and our current offset.

        return {
            'progress': progress_data
        }
    };

    var setOffset = function(change) {

      var predicted_result = progress_data.current_offset + change;

      if (predicted_result >= 0 && predicted_result <= progress_data.page_len) {
            progress_data.current_offset = predicted_result;
      }

        console.log(progress_data);
    };




    //messageBar methods:
    var checkProgress = function() {

        var current_fin = [];
        var poller = function() {$http({
            method: 'GET',
            url: '/get_progress'
            }).then(function(response) {
                console.log(response.data);
                current_fin = response.data.fin;

                $rootScope.$broadcast('refreshUpdate',
                    {current_fin: current_fin, feed_ids: feed_ids});  // send refresh update to progressbar
                                                                      // and sub controllers
                if (current_fin.length!==feed_ids.length) {
                    $timeout(poller, 1000);
                }
                else {
                    $rootScope.$broadcast('refreshDone');  //notify sub and progressbar refresh is done

                    //all feeds should optionally take a page number, so that this sets back to
                    //page 1 on refresh of feeds.
                    allFeeds();
                }
            });
        };

        poller();

        return {
              current_fin: current_fin
            }
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

    var markAsRead = function(entry_id) {
        console.log('make request received entry id: ', entry_id);
        var promise = $http({
          method: 'POST',
          url: '/mark_as_read',
          headers: {'Content-Type': 'application/x-www-form-urlencoded'},
          data:$.param({entry_id: entry_id})
      }); //do we really care if this returns?  could be extra overhead..

    };


    //Feed Methods:

    var getSubs = function() {
        var responsePromise = $http.get("/get_user_subs", {params: {
            }});

        return(responsePromise.then(handleSubUpdate))
    };

    var unsubscribeFeed = function(feed_id) {
      var promise = $http({
          method: 'POST',
          url: '/unsubscribe',
          headers: {'Content-Type': 'application/x-www-form-urlencoded'},
          data:$.param({ufid: feed_id})
      });

      return(promise.then(handleAddFeedResult))

    };

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
        //these are initialized on page load, so this getter should be available at any time
        //to controllers that want it.
        console.log('getting updated entries');
        return entries;
    };

    var getFeedIds = function() {
        return feed_ids;
    };



    //private methods:

    function manageProgress() {
        //this function should repeatedly poll server progress
        //check fin_q vs users feeds until they match
        //send updates to progressbar and sub_ctrl controller
        //and then wrap everything up when done.
        checkProgress();

    }




    //Success Handlers:
    function handleSubUpdate(result){
        subscriptions = result.data;
        feed_ids = [];
        for (var i=0; i < subscriptions.subs.length; i++) {
            feed_ids.push(subscriptions.subs[i].feed_id);
        }
        return subscriptions;
    }

    function handleAddFeedResult(result) {
        console.log("addFeed/remove result happened!");
        console.log("result: ", result);
        $rootScope.$broadcast('notificationBroadcast', result.data);
    }

    function handleRefreshSuccess() {
        console.log("refresh has been successful!");
        console.log("current feed_ids: ", feed_ids);

        // polling service should start here.
        manageProgress();

        //$rootScope.$broadcast("feedChange");  //notify entry controller to update entries
        //$rootScope.$broadcast("entryRefreshInit") //notify progressbar of refresh
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
        checkProgress: checkProgress,
        unsubscribeFeed: unsubscribeFeed,
        markAsRead: markAsRead,
        getFeedIds: getFeedIds,
        getSubs: getSubs,

        //entry scrolling:
        getProgress: getProgress,
        setOffset: setOffset

    });

}]);





