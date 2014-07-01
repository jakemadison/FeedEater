var eServices = angular.module('eServices', []);

eServices.factory('makeRequest', ['$http', '$rootScope', function($http, $rootScope) {

    var current_paging = {'has_next': false, 'has_prev': false};

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

    var getPager = function() {
        console.log('getting pager');
        return current_paging;
    }



    //private methods:
    function handleSuccess(data) {

        var paging_response = data.data.pager;

        if (paging_response.has_next != current_paging.has_next ||
            paging_response.has_prev != current_paging.has_prev) {
                current_paging = paging_response;
                console.log('i am firing a pagerUpdated broadcast!');
                $rootScope.$broadcast("pagerUpdated");
        }

        return data.data;
    }

    //public API of service:
    return({
        pullEntryData: getEntries,
        getPager: getPager
    });

}]);




