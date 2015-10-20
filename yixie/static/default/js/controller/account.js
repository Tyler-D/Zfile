/* account控制器 */
function account_controller($scope, $http) {
    /*$scope.account = {
        'id': 1,
        'name': 'zixie1991',
        'email': 'zixie1991@163.com'
    }*/

    $http.get("/settings/account").success(function(response){
        if (0 == response.errno) {
            $scope.account = response;
        }
    });
}
