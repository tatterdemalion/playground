<html>
    <head>
        <meta charset="utf-8" />
        <title>Spotify Angular</title>
        <script src="//cdnjs.cloudflare.com/ajax/libs/angular.js/1.2.18/angular.min.js"></script>
        <script>
var app = angular.module('spotify', []);

app.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
});

app.controller('spotifyController', function($scope, $http){
    $scope.key = '';
    $scope.searchTrack = function(){
        $http.get('/search/'+$scope.key).success(
        function(data){
            $scope.tracks = data.tracks.items;
        });
    };
});
        </script>
    </head>
    
    <body ng-app="spotify">
        <div ng-controller="spotifyController">
        <form method="GET" name="spotifyForm" ng-submit="searchTrack()">
            <input type="text" ng-model="key" />
            <button type="submit">ara</button>
        </form>
        
        <div ng-repeat="track in tracks">
            <strong>[[ track.artists[0].name ]]</strong>
            <audio controls autoplay="false">
                <source ng-src="[[ track.preview_url ]]" type="audio/mpeg">
            </audio>
        <div>

        </div>
    </body>

</html>
