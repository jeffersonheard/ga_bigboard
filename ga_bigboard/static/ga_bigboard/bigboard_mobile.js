var map;
var bb;
var controls;
var initted = false;

$(document).ready(function() {
    var gm = new OpenLayers.Projection("EPSG:4326");
    var sm = new OpenLayers.Projection("EPSG:3857");
    var annotationLayer = new OpenLayers.Layer.Vector("Annotations");
    var participantsLayer = new OpenLayers.Layer.Vector("Participants");

    controls = {
        // DEBUG ONLY: layer_control : new OpenLayers.Control.LayerSwitcher(),
        navigate_control :new OpenLayers.Control.Navigation({ dragPanOptions: { enableKinetic: true}, zoomWheelEnabled: true}),
        keynav_control : new OpenLayers.Control.KeyboardDefaults(),
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
        attribution : new OpenLayers.Control.Attribution()
    };

    var lastCenter = undefined;
    var participants = {};
    var annotations = {};
    var geojson = new OpenLayers.Format.GeoJSON();
    var roles = null;
    var overlays = {};
    var personalViews = {};

    function init() { if(!initted) {
        initted = true;

        bb = BigBoard({
            room_name : room_name,
            user_id : $("#user_id").val(),
            user_name : user_name,
            api_key : api_key,
            debug : true,

            callbacks: {
                loginSuccessful: [
                    function(data) {
                        console.log('starting data streams');
                        bb.start();
                    }
                ],
                
                receivedAnnotations: [
                    function(data) {
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
                    }
                ],
    
                receivedChats: [
                    function(data) {
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
                    }
                ],
    
                receivedOverlays: [
                    function(data) {
                        iter(data, function(obj) {
                            // append overlays to the overlay tab.  We only support WMS right now.
                            if(!overlays.hasOwnProperty(obj.resource_uri)) {
                                overlays[obj.resource_uri] = new Overlay(map, obj, bb);
                            }
                        });
                        map.setLayerIndex(annotationLayer, 9999);
                        map.setLayerIndex(participantsLayer, 10000);
        
                    }
                ],
    
                receivedParticipants: [
                    function(data) {
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
                        //$(".username").click(function(k) {
                        //    var pt = participantsLayer.getFeatureBy('user', $(k.currentTarget).data('user')).geometry;
                        //    map.setCenter(new OpenLayers.LonLat(pt.x, pt.y));
                        //});
        
                        participantsLayer.redraw();
                    }
                ],
    
                receivedRoles: [
                    function(data) {
                        roles = data;
                    }
                ],
    
                receivedRoom: [
                    function(data) {
                        var baseLayer;
                        var newCenter;
        
                        if(!map) {
        
                            //
                            // setup the map
                            //
                            switch(data.base_layer_type) {
                                case "GoogleTerrain":
                                        baseLayer = new OpenLayers.Layer.Google("Google Terrain", {type: google.maps.MapTypeId.TERRAIN});
                                    break;
                                case "GoogleSatellite":
                                        baseLayer = new OpenLayers.Layer.Google("Google Satellite", {type: google.maps.MapTypeId.SATELLITE});
                                    break;
                                case "GoogleHybrid":
                                        baseLayer = new OpenLayers.Layer.Google("Google Streets", {type: google.maps.MapTypeId.HYBRID});
                                    break;
                                case "OSM":
                                        baseLayer = new OpenLayers.Layer.OSM("OpenStreetMap");
                                    break;
                                case "WMS":
                                        baseLayer = new OpenLayers.Layer.WMS(data.base_layer_wms.name, eval(data.base_layer_wms.default_creation_options));
                                    break;
                            }
                            map = new OpenLayers.Map({
                                div: "map",
                                theme : null,
                                projection: sm,
                                numZoomLevels: 20,
                                controls: values(controls),
                                layers: [baseLayer, annotationLayer, participantsLayer]
                            });
                            newCenter = new OpenLayers.LonLat(data.center.coordinates[0], data.center.coordinates[1]);
                            lastCenter = newCenter.clone();
        
                            map.maxExtent = baseLayer.maxExtent;
                            
                            // if a center has not been set in the url parameters, set to the room center, otherwise use the passed center
                            urldata = $.url();
                            if( typeof urldata.param('where') != 'undefined' && typeof urldata.param('zoom_level') != 'undefined' ) {
                                // a center has been specified in the url
                                var newC = new OpenLayers.LonLat(urldata.param('where').coordinates[0], urldata.param('where').coordinates[1])
                                newC.transform(gm, sm);
                                map.setCenter(newC, urldata.param('zoom_level')); 
                                
                            } else {
                                // use default room center
                                map.setCenter(newCenter, data.zoom_level);
                            }
                            
                            
                            annotationLayer.projection = sm;
                            annotationLayer.maxExtent = map.maxExtent;
                            participantsLayer.maxExtent = map.maxExtent;
        
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
                        else if(Math.abs(lastCenter.lon - data.center.coordinates[0]) > 0.0001 || Math.abs(lastCenter.lat - data.center.coordinates[1]) > 0.0001) {
                            newCenter = new OpenLayers.LonLat(data.center.coordinates[0], data.center.coordinates[1]);
                            lastCenter = newCenter.clone();
        
                            map.setCenter(newCenter, data.zoom_level);
        
                        }
                    }
                ],
    
                receivedSharedOverlays: [
                    function(data) {
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
        
                        map.setLayerIndex(annotationLayer, 9999);
                        map.setLayerIndex(participantsLayer, 10000);
                    }
                ],
                
                // adds the personal views to the list
                receivedPersonalViews: [
                    function(data) {
                        iter(data, function(obj) {
                            
                            // Check if personal view has already been added
                            if(!personalViews.hasOwnProperty(obj.resource_uri)) {
                                personalViews[obj.resource_uri] = obj;
                                
                                $('<li/>', {
                                                id: 'views_item_'+obj.id
                                            }).appendTo('#personal_views_list');
                                $('<div/>', {
                                                id: 'views_item_top_'+obj.id,
                                                html: "\
                                                    <span class='views-list-operations'>\
                                                        <span id='views_item_go_icon_"+obj.id+"' data-action='jump_to_personal_view' data-view-index='"+obj.resource_uri+"' class='views-item-go-icon'>Go</span>\
                                                        <span id='views_item_remove_icon_"+obj.id+"' data-action='remove_personal_view' data-view-index='"+obj.resource_uri+"' class='views-item-go-icon'>x</span>\
                                                    </span>\
                                                    "+obj.name+"<br />"
                                            }).appendTo('#views_item_'+obj.id);
                                $('<div/>', {
                                                id: 'views_item_extra_'+obj.id,
                                                class: 'views-item-extra'
                                            }).appendTo('#views_item_'+obj.id);
                                $('<span/>', {
                                                id: 'views_item_toggle_description_'+obj.id,
                                                class: 'views-item-toggle-description',
                                                html: 'Show Description'
                                            }).appendTo('#views_item_extra_'+obj.id);
                                $('<div/>', {
                                                id: 'views_item_description_'+obj.id,
                                                style: 'display: none;',
                                                html: obj.description
                                            }).appendTo('#views_item_extra_'+obj.id);
                                
                                // view description toggle
                                $('#views_item_toggle_description_'+obj.id).click(function() {
                                    if( $('#views_item_description_'+obj.id).css('display') == 'none' ) {
                                        $('#views_item_description_'+obj.id).show(150);
                                        $('#views_item_toggle_description_'+obj.id).html('Hide Description');
                                    } else {
                                        $('#views_item_description_'+obj.id).hide(150);
                                        $('#views_item_toggle_description_'+obj.id).html('Show Description');
                                    }
                                });
                                
                                // sets map center to chosen personal view
                                $('#views_item_go_icon_'+obj.id).click(function(e) {
                                    var uri = $(this).data('view-index');
                                    var center = personalViews[uri];
                                    
                                    var newCenter = new OpenLayers.LonLat(center.where.coordinates[0], center.where.coordinates[1])
                                    newCenter.transform(gm, sm);
                                    map.setCenter(newCenter, center.zoom_level); 
                                });
                                
                                // removes the chosen personal view
                                $('#views_item_remove_icon_'+obj.id).click(function(e) {
                                    // delete on server and remove from list
                                    var uri = $(this).data('view-index');
                                    var view = personalViews[uri];
                                    
                                    $('#views_item_'+view.id).remove();
                                    
                                    bb.deletePersonalView( view );
                                });
                            }
                        });
                        
                    }
                ]   // end receivedPersonalViews
            }
        });

        //
        // Make sure the user has enabled geolocation before tracking.
        //
        if(navigator.geolocation) {
            navigator.geolocation.watchPosition(function(position) {
                bb.location[0] = position.coords.longitude;
                bb.location[1] = position.coords.latitude;
            });
        }

        // leave when someone clicks the "leave" button
        $("#leave").click(function() {
            bb.leave();
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
    }}

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
        
        // overlays
        $('#overlays').height(contentHeight+25);
        
        // chat log
        var rest_of_height = contentHeight-502;
        $("#chat_log").height(rest_of_height);
        
        // personal views
        rest_of_height = contentHeight-305;
        $("#personal_views_list").height(rest_of_height);

        // Map zoom
        $("#plus").click(function() { map.zoomIn(); });
        $("#minus").click(function() { map.zoomOut(); });

        $(".help_text").height(contentHeight-20);
    }
    $(window).bind("orientationchange resize pageshow", fixContentHeight);
    document.body.onload = fixContentHeight;


    function menuSwitcher(evt) {
        var clicked = $(evt.currentTarget).attr('id').substring("show_".length);

        $(".navigator").each(function(index, elt) {
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

    function addAnnotation(annotation) {
        var kind = $("#annotation_kind").val();
        var file = $("#annotation_file")[0].files[0];
        var text = $("#annotation_text").val();
        bb.persistAnnotation(kind, kind==='text'||kind==='link' ? text : file, annotation);

        $("#annotation_file").val(null);
        $("#annotation_text").val('');
    }

    controls.point_control.featureAdded = addAnnotation;
    controls.path_control.featureAdded = addAnnotation;
    controls.polygon_control.featureAdded = addAnnotation;
    controls.select_control.onSelect = function(annotation) {
        iter(annotations, function(ann) {
            ann.selected = ann.selected || ann.attributes.resource_uri === annotation.attributes.resource_uri;
        });
    };
    controls.select_control.onUnselect = function(annotation) {
        iter(annotations, function(ann) {
            ann.selected = ann.selected && ann.attributes.resource_uri !== annotation.attributes.resource_uri;
        });
    };



    //$("#join_room").submit(function() {
    //    bb.join(
    //        $("#room").val(),
    //        $("#username").val(),
    //        $("#password").val()
    //    );
    //    return false;
    //});
    
    // add teh current center/zoom to personal views
    $('#bb_map_add_personal_view_form').submit(function(e) {
        var name = $('#bb_map_add_personal_view_name').val();
        var description = $('#bb_map_add_personal_view_description').val();;
        
        var c = map.getCenter();
        c.transform(sm, gm);
        bb.addPersonalView(name, description, c.lon, c.lat, map.getZoom());
        
        $('#bb_map_add_personal_view_name').val('');
        $('#bb_map_add_personal_view_description').val('');
        return false;
    });
    
    $('#bb_get_current_view_url').click(function() {
        var urlinfo = $.url();
        
        var c = map.getCenter();
        c.transform(sm, gm);
        //bb.addPersonalView(name, description, c.lon, c.lat, map.getZoom());
        
        var d = {
            room: bb.room,
            where: {
                coordinates: [c.lon, c.lat],
                type: 'Point'
            },
            zoom_level: map.getZoom()
        }
        
        var viewurl = urlinfo.attr('base')+urlinfo.attr('path')+'?'+$.param(d)
        $('#bb_current_view_url').val(viewurl);
    });

    $("#center_all_here").submit(function() {
        var c = map.getCenter();
        c.transform(sm, gm);
        bb.setRoomCenter(c.lon, c.lat, map.getZoom())
        return false;
    });

    $("#delete_control").click(function() {
        iter(annotations, function(ann) {
           if(ann.selected) {
               bb.deleteAnnotation(ann);
               annotationLayer.destroyFeatures(ann);
           }
        });
    });

    $("#reveal_control").click(function() {
        var first=false;

        iter(filter(annotations, function(ann) { return ann.selected; }), function(ann) {
            var info = $('<div></div>');
            info.append("<h3>Selected Feature</h3>"); // TODO when this is clicked, highlight the feature on the map if there are multiple selected
            var info_container = $("<ul data-role='listview'></ul>");
            info.append(info_container);
            $("#feature_info>*").detach();
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
                            info_container.append('<li>' + v + '</li>');
                            break;
                    }
                }
            });

            $("#feature_info").trigger('refresh');
        });
    });

    $("a.menuitem").click(menuSwitcher);
    $(".navigator").hide();
    $("#overlays").show();
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
        }
    });

    bb.join(0);  // delay start by 0ms
});