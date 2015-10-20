/* u控制器 */
function u_controller($scope, $http) {
    uid = $('#userid').text();
    $http.get("/user/get", {'params': {'id': uid}}).success(function(response){
        if (0 == response.errno) {
            $scope.u = response;
        }
    });

    $http.get("/file/list", {'params': {'pn': 1, 'id': uid}}).success(function(response){
        if (0 == response.errno) {
            $scope.file = response;
        }
    });

    $scope.file_page = function(pn) {
        $http.get("/file/list", {'params': {'pn': pn, 'id': uid}}).success(function(response){
            if (0 == response.errno) {
                $scope.file = response;
            }
        });
    }

}
