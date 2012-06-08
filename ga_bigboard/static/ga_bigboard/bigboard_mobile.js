var map;
var bb;
var controls;


$(document).ready(function() {
    var gm = new OpenLayers.Projection("EPSG:4326");
    var sm = new OpenLayers.Projection("EPSG:3857");
    var annotationLayer = new OpenLayers.Layer.Vector("Annotations");
    var participantsLayer = new OpenLayers.Layer.Vector("Participants");

    controls = {
        navigate_control :new OpenLayers.Control.TouchNavigation({ dragPanOptions: { enableKinetic: true} }),
        point_control : new OpenLayers.Control.DrawFeature(annotationLayer, OpenLayers.Handler.Point),
        path_control : new OpenLayers.Control.DrawFeature(annotationLayer, OpenLayers.Handler.Path),
        polygon_control : new OpenLayers.Control.DrawFeature(annotationLayer, OpenLayers.Handler.Polygon),
        select_control : new OpenLayers.Control.SelectFeature(annotationLayer),
        distance_control : new OpenLayers.Control.Measure(OpenLayers.Handler.Path, {
            persist: true
        }),
        area_control :    new OpenLayers.Control.Measure(OpenLayers.Handler.Polygon, {
            persist: true
        }),
        attribution : new OpenLayers.Control.Attribution(),
        layer_switcher : new OpenLayers.Control.LayerSwitcher()
    };

    var lastCenter = undefined;
    var myLocation = [0,0];
    var participants = {};
    var annotations = {};
    var geojson = new OpenLayers.Format.GeoJSON();
    var roles = null;
    var overlays = {};

    function init() {
        bb = BigBoard({
            room_name : $("#room_name").val(),
            username : $("#username").val(),
            password : $("#password").val(),
            user_id : $("#user_id").val(),
            debug : true,

            loginSuccessful : function(data) {
                console.log('starting data streams');
                bb.start();
            },

            receivedAnnotations: function(data) {
                var feature;
                var untouched = keyset(annotations);
                iter(data, function(ann) {
                    delete untouched[ann.resource_uri];
                    if(!annotations.hasOwnProperty(ann.resource_uri)) {
                        feature = geojson.read(ann.geometry)[0];

                        feature.attributes = $.extend(ann, {});
                        annotationLayer.addFeatures(feature);
                        annotations[ann.resource_uri] = feature;
                    }
                    else if(annotations[ann.resource_uri].attributes.when != ann.when) {
                        annotationLayer.destroyFeatures(annotations[ann.resource_uri]);
                        feature = geojson.read(ann.geometry)[0];
                        feature.attributes = $.extend(ann, {});
                        annotationLayer.addFeatures(feature);
                        annotations[ann.resource_uri] = feature;
                    }
                });
                enumerate(untouched, function(resource_uri) {
                    annotationLayer.destroyFeatures(annotations[resource_uri]);
                });
                annotationLayer.redraw();
            },

            receivedChats: function(data) {
                //$("#chat_log>*").detach();
                iter(data, function(chat) {
                    // for each non-private or me-directed chat in the log:
                    if(!chat.private || chat.at.indexOf(user_id) != -1) {
                    //      scan the text for the names in participants.  If the name exists, update it so that it's got <span class='$participant'></span> around it.
                    // collect the "ats" from each non-private chat.  for each "at":
                    //      update the css temporarily to highlight the participant for 5 seconds.
                    //      append a temporary LineString from chat.user to each chat.at
                    //      highlight the participant on the participants layer.
                    //      append the chat text to the log.
                    // if the chat is not private or is "at" this user:
                    //      if the chat is private update the css so that it's marked as such in the log.
                    //      append (when) user: to the
                        var timestamp = new Date(chat.when);
                        var chat_record = $("<div class='chat_item'></div>");
                        chat_record.append("<span class='chat_time'>" + timestamp.toTimeString().substring(0,6) + "</span>");
                        chat_record.append("<span class='chat_username'>" + participants[chat.user].user.username + "</span>");
                        chat_record.append("<span class='chat_text'>" + chat.text + "</span>");
                        $("#chat_log").append(chat_record);
                    }
                });
                if(data.length > 0) {
                    $("#chat_log").scrollTop($("#chat_log").scrollTop() + $("#chat_log>*").last().position().top);
                }
                participantsLayer.redraw();
            },

            receivedOverlays: function(data) {
                console.log("overlays:");
                console.log(data);

                iter(data, function(obj) {
                    // append overlays to the overlay tab.  We only support WMS right now.
                    if(!overlays.hasOwnProperty(obj.resource_uri)) {
                        overlays[obj.resource_uri] = new Overlay(map, obj);
                    }
                });
            },

            receivedParticipants: function(data) {
                participants = {};
                $("#participant_list>*").detach();

                iter(data, function(participant) {
                    participants[participant.user.resource_uri] = participant;
                    var f = participantsLayer.getFeatureBy('user', participant.user.resource_uri); // for each participant in the room, update their position on the map
                    if(f) {
                        var pt = new OpenLayers.Geometry.Point(
                            participant.where.coordinates[0],
                            participant.where.coordinates[1]
                        ).transform(gm, sm);

                        f.geometry.x = pt.x;
                        f.geometry.y = pt.y;
                    }
                    else {
                        f = new OpenLayers.Feature.Vector(
                            new OpenLayers.Geometry.Point(
                                participant.where.coordinates[0],
                                participant.where.coordinates[1]
                            ).transform(gm, sm), participant);

                        f.style = {
                            fill : true,
                            fillColor : '#ff6666',
                            strokeColor : '#ff6666',
                            strokeWidth : 1,
                            fillOpacity : 0.6,
                            graphic : true,
                            graphicName : 'cross',
                            fontColor : '#000000',
                            fontWeight : 'bold',
                            fontFamily : 'Helvetica, Arial, sans-serif',
                            fontSize : '9pt',
                            pointRadius : 5,
                            label : participant.user.username,
                            labelAlign : 'l',
                            labelXOffset : 7
                        };
                        f.attributes = participant;
                        f.user = participant.user.resource_uri;
                        participantsLayer.addFeatures([f]);
                    }

                    var display_name = participant.user.first_name ? (participant.user.first_name + ' ' + participant.user.last_name)  : participant.user.username;
                    var heartbeat_time = new Date(participant.last_heartbeat);
                    var email_link = $("<a class='user_email' data-role='button' data-mini='true' href='mailto:" + participant.user.email + "'>email</a>");

                    var participant_name = $("<li></li>")
                            .append($("<a class='username' href='#'>" + display_name + "</span>").data('user', participant.user.resource_uri))
                            .append($("<span class='user_heartbeat'>" + heartbeat_time.toTimeString().substring(0,5) + "</span>"))
                            .append(email_link);

                    $("#participant_list").append(participant_name);
                });

                // TODO - click on user name in participant list to center on that user.
                $(".username").click(function(k) {
                    var pt = participantsLayer.getFeatureBy('user', $(k.currentTarget).data('user')).geometry;
                    map.setCenter(new OpenLayers.LonLat(pt.x, pt.y));
                })

                participantsLayer.redraw();
            },

            receivedRoles: function(data) {
                roles = data;
            },

            receivedRoom: function(data) {
                var baseLayer;
                var newCenter;

                if(!map) {

                    //
                    // setup the map
                    //
                    switch(data.base_layer_type) {
                        case "GoogleTerrain":
                                baseLayer = new OpenLayers.Layer.Google("Google Terrain", {type: google.maps.MapTypeId.TERRAIN, numZoomLevels: 20});
                            break;
                        case "GoogleSatellite":
                                baseLayer = new OpenLayers.Layer.Google("Google Satellite", {type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 20});
                            break;
                        case "GoogleHybrid":
                                baseLayer = new OpenLayers.Layer.Google("Google Streets", {type: google.maps.MapTypeId.HYBRID, numZoomLevels: 20});
                            break;
                        case "OSM":
                                baseLayer = new OpenLayers.Layer.Google("OpenStreetMap");
                            break;
                        case "WMS":
                                baseLayer = new OpenLayers.Layer.WMS(data.base_layer_wms.name, data.base_layer_wms.default_creation_options);
                            break;
                    }
                    map = new OpenLayers.Map({
                        div: "map",
                        theme : null,
                        projection: sm,
                        numZoomLevels: 18,
                        controls: values(controls),
                        layers: [baseLayer, annotationLayer, participantsLayer]
                    });
                    newCenter = new OpenLayers.LonLat(data.center.coordinates[0], data.center.coordinates[1]);
                    lastCenter = newCenter.clone();

                    map.maxExtent = baseLayer.maxExtent;
                    map.setCenter(newCenter, data.zoom_level);
                    annotationLayer.projection = sm;
                    annotationLayer.maxExtent = map.maxExtent;

                    //
                    // setup all the drawing controls
                    //
                    $(".control").click(function(e) {
                        var clicked = $(this).attr('id');
                        enumerate(controls, function(name, ctrl) {
                            if(name === clicked) {
                                ctrl.activate();
                            }
                            else {
                                ctrl.deactivate();
                            }
                        });

                        $(".control").each(function(i, elt) {
                            if($(elt).attr('id') == clicked) {
                                $(elt).addClass('ui-btn-active');
                            }
                            else {
                                $(elt).removeClass('ui-btn-active');
                            }
                            $(elt).trigger('refresh');
                        });
                    });

                    //
                    // setup the map-centering control using google geocoder
                    //
                    var geocoder = new google.maps.Geocoder();
                    $("#recenter_on_addr").submit(function() {
                        var address = $("#center_on_addr").val();
                        if(address) {
                            geocoder.geocode({ address : address}, function(results, statusCode) {
                                if(statusCode === google.maps.GeocoderStatus.OK) {
                                    var ll = results[0].geometry.location;
                                    var realCenter = new OpenLayers.LonLat(ll.lng(), ll.lat());
                                    realCenter.transform(gm, sm);
                                    map.setCenter(realCenter,11);
                                }
                                else {
                                    alert('Cannot find address');
                                }
                            });
                        }
                        return false;
                    });

                }
                else if(lastCenter.lon != data.center.coordinates[0] || lastCenter.lat != data.center.coordinates[1] ) {
                    newCenter = new OpenLayers.LonLat(data.center.coordinates[0], data.center.coordinates[1]);
                    lastCenter = newCenter.clone();

                    map.setCenter(newCenter, data.zoom_level);

                }
            },

            receivedSharedOverlays: function(data) {
                var untouched = keyset(overlays);

                iter(data, function(o) {
                    if(overlays.hasOwnProperty(o.overlay.resource_uri)) {
                        delete untouched[o.overlay.resource_uri];
                        overlays[o.overlay.resource_uri].share();
                    }
                });
                enumerate(untouched, function(k) {
                    overlays[k].unshare();
                });

            }
        });

        if(navigator.geolocation) {
            navigator.geolocation.watchPosition(function(position) {
                bb.location[0] = position.coords.longitude;
                bb.location[1] = position.coords.latitude;
            });
        }

        // leave when someone clicks the "leave" button
        $("#leave").click(function() {
            bb.leave();
            return false;
        });

        // send chats when someone clicks the > button
        $("#chat_form").submit(function() {
            var chatText = $("#chat_entry").val();
            if(chatText) {
                bb.sendChat(chatText);
                $("#chat_entry").val("");
            }
            return false;
        });
    }

    // fix height of content
    function fixContentHeight() {
        var footer = $("div[data-role='footer']:visible"),
            content = $("div[data-role='content']:visible:visible"),
            viewHeight = $(window).height(),
            contentHeight = viewHeight - footer.outerHeight();

        if ((content.outerHeight() + footer.outerHeight()) !== viewHeight) {
            contentHeight -= (content.outerHeight() - content.height() + 1);
            content.height(contentHeight);
        }

        if (map && map instanceof OpenLayers.Map) {
            map.updateSize();
        } else {
            init(function(feature) {
                selectedFeature = feature;
                $.mobile.changePage("#popup", "pop");
            });
        }


        var rest_of_height = contentHeight-360;
        $("#chat_log").height(rest_of_height);

        // Map zoom
        $("#plus").click(function() { map.zoomIn(); });
        $("#minus").click(function() { map.zoomOut(); });

        $(".help_text").height(contentHeight-20);
    }
    $(window).bind("orientationchange resize pageshow", fixContentHeight);
    document.body.onload = fixContentHeight;


    function menuSwitcher(evt) {
        var clicked = $(evt.currentTarget).attr('id').substring("show_".length);

        $("ul.navigator").each(function(index, elt) {
            if($(elt).attr('id') == clicked) {
                $(elt).show();
            }
            else {
                $(elt).hide()
            }
        });
        return false;
    }

    init();

    controls.point_control.featureAdded = function(annotation) { bb.persistAnnotation(annotation); };
    controls.path_control.featureAdded = function(annotation) { bb.persistAnnotation(annotation); };
    controls.polygon_control.featureAdded = function(annotation) { bb.persistAnnotation(annotation); };
    controls.select_control.onSelect = function(annotation) {
        iter(annotations, function(ann) {
            ann.selected = ann.selected || ann.attributes.resource_uri === annotation.attributes.resource_uri;
        });
    }
    controls.select_control.onUnselect = function(annotation) {
        iter(annotations, function(ann) {
            ann.selected = ann.selected && ann.attributes.resource_uri !== annotations.attributes.resource_uri;
        });
    }


    $("#join_room").submit(function() {
        bb.join(
            $("#room").val(),
            $("#username").val(),
            $("#password").val()
        );
        return false;
    });

    $("#center_all_here").submit(function() {
        var c = map.getCenter();
        c.transform(sm, gm);

        $.get('center', {
            x:c.lon,
            y:c.lat,
            z:map.getZoom()
        });
        return false;
    });

    $("#delete_control").click(function() {
        iter(annotations, function(ann) {
           if(ann.selected) {
               $.ajax({
                   url: ann.attributes.resource_uri,
                   type: 'DELETE'
               });
               annotationLayer.destroyFeatures(ann);
           }
        });
    });

    $("#reveal_control").click(function() {
        var first=false;

        iter(filter(annotations, function(ann) { return ann.selected; }), function(ann) {
            var info = $('<div data-role="collapsible"></div>');
            info.append("<h3>Selected Feature</h3>"); // TODO when this is clicked, highlight the feature on the map if there are multiple selected
            var info_container = $("<ul data-role='listview'></ul>");
            info.append(info_container);
            $("#feature_info").append(info);

            enumerate(ann.attributes, function(k, v) {
                if(v && k != 'geometry' && k != 'id') {
                    info_container.append("<li>" + k + "</li>");

                    switch(k) {
                        case 'text':
                            info_container.append('<li>' + ann.attributes.text + '</li>');
                            break;
                        case 'video':
                            info_container.append('<li><a href="' + ann.attributes.video + '">play video</a></li>');
                            break;
                        case 'link':
                            info_container.append('<li><a href="' + ann.attributes.link + '">follow link</a></li>');
                            break;
                        case 'audio':
                            info_container.append('<li><a href="' + ann.attributes.audio + '">play video</a></li>');
                            break;
                        case 'media':
                            info_container.append('<li><a href="' + ann.attributes.media + '">download media</a></li>');
                            break;
                        case 'image':
                            info_container.append('<li><img src="' + ann.attributes.image + '"/></li>');
                            break;
                        default:
                            info_container.append('<li>' + v + '<li>');
                            break;
                    }
                }
            });

            $("#feature_info").trigger('refresh');
        });
    });

    $(".overlay_share").click(function() {

    });

    $("a.menuitem").click(menuSwitcher);
    $("ul.navigator").hide();
    $("#join").show();
    $("#overlay_base").hide();

    $("#annotation_file").hide();
    $("label[for=annotation_file]").hide();

    $("#annotation_kind").change(function() {
        if($("#annotation_kind option:selected").val() === 'text') {
            $("#annotation_file").hide();
            $("label[for=annotation_file]").hide();
            $("#annotation_text").show();
            $("label[for=annotation_text]").show();
        }
        else {
            $("#annotation_text").hide();
            $("label[for=annotation_text]").hide();
            $("#annotation_file").show();
            $("label[for=annotation_file]").show();
        };
    });
});