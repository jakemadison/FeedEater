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

            var $target = uiScrollfixTarget && uiScrollfixTarget.$element || angular.element($window);



            function onScroll() {

              var id = scope.$eval(attrs['scrollActive']).id;
              var unread = scope.$eval(attrs['scrollActive']).unread;

              var top = elm[0].offsetTop;
              var bottom = top + elm[0].offsetHeight;
//                  extra = elm[0].offsetParent.scrollHeight;

                var offset = $window.pageYOffset;

//                console.log('offset: ', offset, (top-300), bottom);

                if (!elm.hasClass('reading_entry') && (offset+300) > top && (offset+300) < bottom) {
                    elm.addClass('reading_entry');

                    if (unread === true) {
                        scope.$apply("markAsRead("+id+")");  //this is ugly...
                    }




                }

                else if (elm.hasClass('reading_entry') && ((offset+300) < top) || (offset+300) > bottom) {
                    elm.removeClass('reading_entry');
                 }
            }

            $target.on('scroll', onScroll);


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

