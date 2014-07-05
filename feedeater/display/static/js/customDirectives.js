var customDirectives = angular.module('FeedEaterApp');

//
//customDirectives.directive('keyBindings', function() {
//
//    return function (scope, element, attrs) {
//        element.bind("keydown keypress", function (event) {
//
//            if ($(".input_thing").is(":focus")) {  // check if we are in an input thing and don't change page if so
//                return;
//                }
//
//            var ch = event.keyCode || event.which;  //get keypress
//
//            switch(ch) {
//
//                case 37:
//                    event.preventDefault();
//                    scope.$apply(function (){
//                        console.log('left key detected!');
////                        scope.$eval(attrs.keyBindings);
//                    });
//
//                    break;
//
//                case 39:
//                    event.preventDefault();
//                    scope.$apply(function (){
//                        console.log('right key detected!');
////                        scope.$eval(attrs.keyBindings);
//                    });
//
//                    break;
//
//                default:
//                    break;
//            }
//
//        });
//    };
//
//});

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