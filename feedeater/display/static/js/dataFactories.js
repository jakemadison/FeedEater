var dataFactories = angular.module('dataFactories', []);

//the purpose of these functions should be to hold all data which should be application-wide
//so: uf_ids, page, user info?
//anything that is shared by multiple controllers.
//that gets it out of the service logic, which should just deal with connecting to back-end

dataFactories.factory('getUfIds', function() {
    console.log('getUfIds is now running');
    return {s: 'test string'};
});
