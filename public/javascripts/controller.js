var secretApp = angular.module('secretApp', []);

secretApp.controller('alerter', function($scope, $http) {
    $http.get('/api/alerts').then(function (result) {
        $scope.alerts = result.data;
        console.log(result.data)
    });
    console.log($scope.alerts)
});
