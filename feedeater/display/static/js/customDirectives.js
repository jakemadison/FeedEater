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
                            console.log('left was pressedddd');
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


customDirectives.directive('scrollActive', function($window, $document) {

    return {
        require: '^?uiScrollfixTarget',
        restrict: 'A',
        link: function(scope, elm, attrs, uiScrollfixTarget) {

            var top = elm[0].offsetTop,
                $target = uiScrollfixTarget && uiScrollfixTarget.$element || angular.element($window);


            function onScroll() {

                var offset = $window.pageYOffset;
                console.log('offset: ', offset);

                if (!elm.hasClass('reading_entry') && offset > 100) {
                    elm.addClass('reading_entry');
                }

                else if (elm.hasClass('reading_entry') && offset < 100) {
                    elm.removeClass('reading_entry');
                 }
            }

            $target.on('scroll', onScroll);


            //raw.scrollTop + raw.offsetHeight >= raw.scrollHeight

//          element.on("mouseenter", function() {
//              console.log('mouseenter');
//          });

    }
};

});


customDirectives.directive('uiScrollfixTarget', function(){
   return {
        controller: ['$element', function($element) {
            this.$element = $element;
        }]
    };
});



//    return {
//        restrict: 'E',
//        transclude: true,
//        link: function(scope, element, attrs) {
//            console.log('anything?');
//
//            var window = angular.element($window),
//                parent = angular.element(element.parent()),
//                currentOffsetTop = element.offset().top;
//
//            handleScroll();
//
//            console.log('scroll directive: ', element, attrs);
//
//            window.bind("scroll", function() {
//                console.log('bind scroll works');
//               handleScroll();
//            });
//
//            element.bind("mouseenter", function() {
//               console.log('mouseenter happened');
//            });
//
//
//
//            function handleScroll() {
//                console.log('handleScroll');
//                if (window.scrollTop() > currentOffsetTop) {
//                    console.log('something happened: ', currentOffsetTop, parent, attrs);
//                }
//                else {
//                    console.log('else..');
//                }
//
//            }
//
//
//
//
//        }
//
//    };


//});