window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(e, ctx) {
            ctx.setProps({
                actor: e.target.options.id,
                moveend: [e.latlng.lat, e.latlng.lng]
            })
        },
        function1: function(e, ctx) {
            ctx.setProps({
                actor: e.target.options.id,
                n_clicks: (ctx.n_clicks == undefined ? 1 : ctx.n_clicks + 1)
            })
        }
    }
});