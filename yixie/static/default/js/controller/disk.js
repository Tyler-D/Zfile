/* disk控制器 */
function disk_controller($scope, $http) {
    /*$scope.disk = {
        'label': '所有文件',
        'path': '/算法/wiki/',
        'list': [
            {
                'server_filename': 'doc.doc',
                'size': 10241024,
                'path': '/test/doc.doc',
                'isdir': 0,
                'server_ctime': '2014-10-20 20:30:10',
                'server_mtime': '2014-10-20 23:10:01',
                'fs_id': 12,
                'category': 6
            },
            {
                'server_filename': 'prog',
                'path': '/test/prog',
                'isdir': 1,
                'server_ctime': '2013-11-20 10:30:10',
                'server_mtime': '2013-12-21 23:10:01',
                'category': 5
            }
        ]
    }
    // 生成面包屑
    crumbs($scope.disk.path);*/

    $http.get("/disk/list", {'params': {'path': '/'}}).success(function(response){
        if (0 == response.errno) {
            $scope.disk = response;
            // 生成面包屑
            crumbs($scope.disk.path);
            // 为hidden input添加值
            $('#file-form-path').val(response.path);
            $('#folder-form-path').val(response.path);
        }
    });

    $scope.disk_page = function(path) {
        $http.get("/disk/list", {'params': {'path': path}}).success(function(response){
            if (0 == response.errno) {
                $scope.disk = response;
                // 生成面包屑
                crumbs($scope.disk.path);
                // 为hidden input添加值
                $('#file-form-path').val(response.path);
                $('#folder-form-path').val(response.path);
            }
        });
    }

    $scope.disk_remove = function(path) {
        $http.get("/disk/remove", {'params': {'path': path}}).success(function(response){
            alert(response.msg);
            if (0 == response.errno) {
                location.reload();
            }
        });
    }

}
