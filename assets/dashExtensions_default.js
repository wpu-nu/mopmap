window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(e, ctx) {
            ctx.setProps({
                actor: e.target.options.id,
                moveend: [e.latlng.lat, e.latlng.lng]
            })
        }
    }
});