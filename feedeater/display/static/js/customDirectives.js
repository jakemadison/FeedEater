var customDirectives = angular.module('FeedEaterApp');


//this directive controls how scroll activates read/unread state:
//this whole function should get changed.  There should always be an active entry.
customDirectives.directive('scrollActive', function($window, $document) {

    return {
        require: '^?uiScrollfixTarget',
        restrict: 'A',
        link: function(scope, elm, attrs, uiScrollfixTarget) {

            var $target = uiScrollfixTarget && uiScrollfixTarget.$element || angular.element($window);

            function onScroll() {

              // get entry id/unread/title id from directive params:
              var id = scope.$eval(attrs['scrollActive']).id;
              var unread = scope.$eval(attrs['scrollActive']).unread;
              var titleElement = angular.element(document.getElementById('title'+id));

              console.log('title'+id, "\n", titleElement);


              var top = elm[0].offsetTop;
              var bottom = top + elm[0].offsetHeight;
//                  extra = elm[0].offsetParent.scrollHeight;

                var offset = $window.pageYOffset;

//                console.log('offset: ', offset, (top-300), bottom);

                //if our element is not currently being read, and it's in our reading threshold
                //add the "reading entry" class:
                if (!elm.hasClass('reading_entry') && (offset+300) > top && (offset+300) < bottom) {

//              if (!elm.hasClass('reading_entry') && (offset+60) > top && (offset+60) < bottom) {

                    elm.addClass('reading_entry');
                    titleElement.addClass('reading_title');


                    //also, if entry was unread, fire off a mark as read for the id:
                    if (unread === true) {
                        scope.$apply("markAsRead("+id+")");  //this is ugly...
                    }
                }

                //otherwise, if we were reading it and are outside of threshold now, remove "reading" state:
                else if (elm.hasClass('reading_entry') && ((offset+300) < top) || (offset+300) > bottom) {
                    elm.removeClass('reading_entry');
                    titleElement.removeClass('reading_title');
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

