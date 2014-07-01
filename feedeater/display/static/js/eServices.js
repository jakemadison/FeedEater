var eServices = angular.module('eServices', []);

eServices.factory('makeRequest', ['$http', '$rootScope', function($http, $rootScope) {

    var current_paging = {'has_next': false, 'has_prev': false};
    var entries = {};

    //public methods:
    var getEntries = function(page_id, star_only) {
        console.log('getEntries method of makeRequest function running');

        var promise = $http({
            method: 'GET',
            url: '/recalculate_entries',
            params: {page_id: page_id, star_only: star_only}
        });

        return (promise.then(handleSuccess));
    }


    var toggleFeed = function(feed_id) {
        console.log('toggleFeed method of makeRequest function running');

        var promise = $http({
            method: 'GET',
            url: '/change_active',
            params: {uf_id: feed_id}
        });

        return (promise.then(handleFeedSuccess));
    }

    var notifyPageChange = function() {
        $rootScope.$broadcast("feedChange");
    }


    // getters:
    var getPager = function() {
        console.log('getting pager');
        return current_paging;
    }

    var getUpdatedEntries = function() {
        console.log('getting updated entries');
        return entries;
    }



    //private methods:
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
        console.log('i am firing a entriesUpdated broadcast!');
        $rootScope.$broadcast("entriesUpdated");
        return data.data;
    }


    //public API of service:
    return({
        pullEntryData: getEntries,
        getPager: getPager,
        getUpdatedEntries: getUpdatedEntries,
        toggleFeed: toggleFeed,
        notifyPageChange: notifyPageChange

    });

}]);




