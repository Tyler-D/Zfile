/* file控制器 */
function file_controller($scope, $http) {
    /*$scope.file = {
        'list': [
        ],
        'total': 10
    }*/

    $http.get("/file/list", {'params': {'pn': 1}}).success(function(response){
        if (0 == response.errno) {
            $scope.file = response;
        }
    });

    $scope.file_page = function(pn) {
        $http.get("/file/list", {'params': {'pn': pn}}).success(function(response){
            if (0 == response.errno) {
                $scope.file = response;
            }
        });
    }

}
