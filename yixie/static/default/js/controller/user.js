/* user控制器 */
function user_controller($scope, $http) {
    $scope.user = {
        'list': [
        ],
        'total': 10
    }

    $http.get("/user/list", {'params': {'pn': 1}}).success(function(response){
        if (0 == response.errno) {
            $scope.user = response;
        }
    });

    $scope.user_page = function(pn) {
        $http.get("/user/list", {'params': {'pn': pn}}).success(function(response){
            if (0 == response.errno) {
                $scope.user = response;
            }
        });
    }

    $scope.user_active = function(id) {
        $http.get("/user/active", {'params': {'id': id}}).success(function(response){
            alert(response.msg);
            if (0 == response.errno) {
                location.reload();
            }
        });
    }

    $scope.user_reset = function(id) {
        $http.get("/user/reset", {'params': {'id': id}}).success(function(response){
            alert(response.msg);
            if (0 == response.errno) {
                //location.reload();
            }
        });
    }

    $scope.user_remove = function(id) {
        $http.get("/user/remove", {'params': {'id': id}}).success(function(response){
            alert(response.msg);
            if (0 == response.errno) {
                location.reload();
            }
        });
    }

}
