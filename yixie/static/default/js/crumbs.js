function crumbs(path) {
    items = path.split('/');
    crumb = "";
    path2 = "";
    $('#bar_name').siblings().remove();
    for (var i = 0; i < items.length; i++) {
        if ("" == items[i]) {
            continue;
        }
        path2 += '/' + items[i];
        crumb += '<span>></span><i>'+items[i]+'</i>';
    }
    $('#bar_name').after(crumb);
}
