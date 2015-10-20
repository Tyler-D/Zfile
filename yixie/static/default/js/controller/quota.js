/* quota控制器 */
function quota_controller($scope, $http) {
    /*$scope.quota = {
        'total': 102903930,
        'used': 1029033
    }*/

    $http.get("/quota/").success(function(response){
        if (0 == response.errno) {
            $scope.quota = response;
        }
    });
}
