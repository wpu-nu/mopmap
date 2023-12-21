window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(e, ctx) {
            ctx.setProps({
                actor_id: e.target.options.id,
                move_end_pos: [e.latlng.lat, e.latlng.lng]
            })
        },
        function1: function(e, ctx) {
            console.log(e.target.options.id);
            ctx.setProps({
                point_id: e.target.options.id,
                n_clicks: (ctx.n_clicks == undefined ? 1 : ctx.n_clicks + 1)
            })
        }
    }
});