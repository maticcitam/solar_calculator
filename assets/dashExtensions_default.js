window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(e, ctx) {
            ctx.setProps({
                click_lat_lng: [e.latlng.lat, e.latlng.lng]
            })
        }
    }
});