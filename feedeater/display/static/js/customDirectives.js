var customDirectives = angular.module('FeedEaterApp');


customDirectives.directive('keyBindings', function() {

    return {
        restrict: "A",
        link: function(scope, element, attrs) {

            console.log('called outside', element);
            element.bind("keyup", function(event){

                // check if we are in an input thing and don't change page if so:
                if ($(".input_thing").is(":focus")) {
                    return;
                }

                scope.$apply(function() {

                    switch (event.which) {

                        case 37:
                            console.log('left was pressed');
                            scope.$broadcast('keypress', 'left');
                            event.preventDefault();
                            break;
                        case 39:
                            console.log('right was pressed');
                            scope.$broadcast('keypress', 'right');
                            event.preventDefault();
                            break;
                    }

                });
            })
        }
    }
});