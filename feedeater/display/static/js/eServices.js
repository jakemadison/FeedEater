var eServices = angular.module('eServices', []);

eServices.factory('getEntries',
    function() {
        console.log('i am a factory!');
        var test = {};
        test.message = 'I am a test message in the factory';
        return test;
    });

