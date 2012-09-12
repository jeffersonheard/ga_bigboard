/**
 * Created with PyCharm.
 * User: jeffersonheard
 * Date: 5/16/12
 * Time: 1:19 PM
 * To change this template use File | Settings | File Templates.
 */

OpenLayers.Format.TastyPie = OpenLayers.Class(OpenLayers.Format.JSON, {
    geoJsonReader : new OpenLayers.Format.GeoJSON(),
    geometryField : null,

    read : function(json, type, filter) {
        var results = null;
        var obj = null;
        if (typeof json == "string") {
            obj = OpenLayers.Format.JSON.prototype.read.apply(this,
                    [json, filter]);
        } else {
            obj = json;
        }

        if(!obj) {
            OpenLayers.Console.error("Bad JSON: " + json);
        } else if(typeof(obj.type) != "string") {
            OpenLayers.Console.error("Bad GeoJSON - no type: " + json);
        } else if(this.isValidType(obj)) {
            return this.makeFeatureCollectionFromResultSet(obj);
        }
    },

    write: function(obj, pretty) {
        var output = null;

        if(OpenLayers.Util.isArray(obj)) {
            output = [];
            for(var i in obj) { if(obj.hasOwnProperty(i)) {
                if (!obj[i] instanceof OpenLayers.Feature.Vector) {
                    console.log('should have been a vector feature');
                    console.log(obj[i]);
                }
                var o = $.extend({}, obj[i].attributes);
                o[geometryField] = this.geoJsonReader.extract.geometry.apply(this, [obj.geometry]);
                output.push(o)
            }}
        }
        else {
            if (!obj instanceof OpenLayers.Feature.Vector) {
                console.log('should have been a vector feature');
                console.log(obj);
            }
            output = $.extend({}, obj.attributes);
            output[this.geometryField] = this.geoJsonReader.extract.geometry.apply(this, [obj.geometry]);
        }
        return OpenLayers.Format.JSON.prototype.write.apply(this,
                [output, pretty]);
    },

    isValidType: function(obj) {
        var geometryTypes = ['Feature','FeatureCollection','LineString','MultiLineString','Point','MultiPoint','Polygon','MultiPolygon','LinearRing','GeometryCollection'];
        var containsGeometry = false;
        if(!obj.objects) { return false; }
        else for(var i in obj.objects) {if(obj.hasOwnProperty(i)) {
            if(this.geometryField && obj[i][this.geometryField] && obj[i][this.geometryField].type && geometryTypes.indexOf(obj[i][this.geometryField]) != -1) {
                containsGeometry = true;
                break;
            }
            for(var f in obj[i]) {if(obj[i].hasOwnProperty(f)) {
                if(obj[i][f].type && geometryTypes.indexOf(obj[i][f].type) != -1) {
                    containsGeometry = true;
                    break;
                }
            }}
        }}
        return containsGeometry;
    },

    makeFeatureFromObject: function(obj) {
        if(!this.geometryField) {
            for(var f in obj) {if(obj.hasOwnProperty(f)) {
                if(obj[f].type && geometryTypes.indexOf(obj[f].type) != -1) {
                    this.geometryField = f;
                    break;
                }
            }}
        }

        if(obj.geometryField) {
            o = $.extend({}, obj);
            delete o[this.geometryField]
            return {
                "type" : "Feature",
                "properties" : o,
                "geometry" : obj[this.geometryField]
            }
        }
    },

    makeFeatureCollectionFromResultSet: function (data) {
        return {
            "type" : "FeatureCollection",
            "features" : mapping(data.objects, function(o) {
                return this.makeFeatureFromObject(o);
            })
        }
    }
});


function Overlay(m, server_object, bb) {
    /* server_object contains:
        name,
        description,
        default_creation_options,
        kind,
        resource_uri,
        roles
     */

    var layer;
    var update_interval;
    var options = {};
    var share_button;
    var overlay_button;
    var overlay_elements;
    var overlay_opacity;
    var overlay_up;
    var overlay_down;
    var active = false;
    var sharing = false;
    var hold = false;

    evaluable_options = "options=" + server_object.default_creation_options + ";";
    switch(server_object.kind) {
        case 'WMS':
            eval(evaluable_options);
            layer = new OpenLayers.Layer.WMS(server_object.name, options.url, options, options);
            break;
        case 'WFS':case 'GeoJSON':
            eval(evaluable_options);
            options.renderers = ['Canvas','SVG','VML'];
            layer = new OpenLayers.Layer.Vector(server_object.name, options);
            break;
        default:
            console.log(server_object.kind);
    }

    function update() {
        switch(server_object.kind) {
            case 'WMS':
                layer.mergeNewParams({});
                break;
            default:
                layer.refresh();
        }
    }

    function markShared() {
        if(!sharing) activate();
        sharing = true;
        share_button.parent().addClass('ui-btn-active');
    }

    function markNotShared() {
        sharing = false;
        share_button.parent().removeClass('ui-btn-active');
    }


    function share() {
        if(!active) {
            // activate();
        }
        if(!sharing) {
            markShared();
            bb.shareLayer(server_object);
            activate();
        }
    }

    function unshare() {
        if(sharing) {
            markNotShared();
            bb.unshareLayer(server_object);
        }
    }

    function toggleSharing() {
        if(sharing)
            unshare();
        else
            share();
    }

    function adjustOrder(zorder) {
        m.raiseLayer(layer, zorder);
    }

    function activate() {
        active = true;
        layer.setVisibility(true);
        overlay_button.parent().addClass('ui-btn-active');
    }

    function deactivate() {
        active = false;
        layer.setVisibility(false);
        overlay_button.parent().removeClass('ui-btn-active');
    }

    function toggle() {
        if(active)
            deactivate();
        else
            activate();
    }

    function pause() {
        if(update_interval)
            clearInterval(update_interval);
    }

    function unpause() {
        if(options.update_interval)
            update_interval = setInterval(update(), options.update_interval);
    }

    function changeOpacity() {
        var value = overlay_opacity.val();
        layer.setOpacity(value / 100.0);
        return false;
    }

    function raise() {
        
        var elt = overlay_elements.prev();
        if(elt && elt.size() > 0) {
            layer.map.raiseLayer(layer, 1);
            overlay_elements.detach();
            overlay_elements.insertBefore(elt);
        }
    }

    function lower() {
        
        // it had been selecting the overlay_base element previously on the lowest element. The not prevents that.
        var elt = overlay_elements.next(':not(#overlay_base)');
        if(elt && elt.size() > 0) {
            layer.map.raiseLayer(layer, -1);
            overlay_elements.detach();
            overlay_elements.insertAfter(elt);
        }
    }

    // start animation if there is any.
    unpause();

    // add this overlay to the list of overlays
    overlay_elements = $("#overlay_base").clone();
    overlay_elements.show();
    overlay_elements.data('overlay_id', server_object.id);
    overlay_elements.attr('id',null);
    overlay_button = $(".overlay_name", overlay_elements);
    share_button = $(".overlay_share", overlay_elements);
    overlay_opacity = $(".overlay_opacity", overlay_elements);
    overlay_up = $(".overlay_up", overlay_elements);
    overlay_down = $(".overlay_down", overlay_elements);
    $('.ui-btn-text', overlay_button.parent()).html(server_object.name);
    overlay_elements.toggle('refresh');
    overlay_button.click(toggle);
    share_button.click(toggleSharing);
    overlay_up.click(raise);
    overlay_down.click(lower);

    overlay_opacity.change(changeOpacity);
    $("#overlays").prepend(overlay_elements);

    overlay_opacity.slider({mini:true, highlight:true});

    m.addLayers([layer]);
    deactivate();

    // Merging directly into server_object affects the original object up the callstack
    // It seems to work better to merge into a new object
    return $.extend({},server_object, {
        layer : layer,
        update: update,
        share:  share,
        unshare: unshare,
        markShared: markShared,
        markNotShared: markNotShared,
        adjustOrder: adjustOrder,
        pause: pause,
        unpause:unpause,
        activate: activate,
        deactivate: deactivate,
        toggle: toggle
    });
}
