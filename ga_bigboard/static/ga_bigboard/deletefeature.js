OpenLayers.Control.DeleteFeature = OpenLayers.Class(OpenLayers.Control, {
    initialize: function(layer, options) {
        OpenLayers.Control.prototype.initialize.apply(this, [options]);
        this.layer = layer;
        this.handler = new OpenLayers.Handler.Feature(
                this, layer, {click: this.clickFeature}
        );
    },
    clickFeature: function(feature) {
        if(feature.attributes.resource_uri === undefined) {
            this.layer.destroyFeatures(feature);
        } else {
            //BB.Server.erase(function(e) {}, {room:BB.room, geohash:feature.attributes.geohash});
            $.ajax({
                type: "DELETE",
                url: feature.attributes.resource_uri
            });
            this.layer.destroyFeatures(feature);
        }
    },
    setMap: function(map) {
        this.handler.setMap(map);
        OpenLayers.Control.prototype.setMap.apply(this, arguments);
    },
    CLASS_NAME: "OpenLayers.Control.DeleteFeature"
});

