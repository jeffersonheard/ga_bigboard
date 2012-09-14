function BigBoard(args) {
    var overlays;
    var shared_overlays;
    var participants;
    var room;
    var chats = [];
    var roles;
    var annotations;
    var personal_views;
    var notifications;
    var last_chat_update = 0;
    
    var started = false;    // Whether this bigboard instance has been started

    var received_annotations = false;
    var received_chats = false;
    var received_overlays = false;
    var received_participants = false;
    var received_roles = false;
    var received_room = false;
    var received_shared_overlays = false;
    var received_personal_views = false;
    var received_notifications = false;


    var my_username = args.user_name; // DEPRECATED
    var my_password = args.api_key; // DEPRECATED
    var my_userid = either(args, 'user_id', null);
    var my_user = either(args, 'user', null);
    var debug = either(args, 'debug', false);
    var main_loop;
    var hash;
    var api_key = args.api_key;
    var user_name = args.user_name;
    var room_name = args.room_name;

    var bb_api_center = either(args, 'bb_api_center', '../center/');
    var bb_api_room = either(args, 'bb_api_room', '../api/v4/room/');
    var bb_api_annotations = either(args, 'bb_api_annotations', '../api/v4/annotation/');
    var bb_api_chats = either(args, 'bb_api_chats', '../api/v4/chat/');
    var bb_api_overlays = either(args, 'bb_api_overlays', '../api/v4/overlay/');
    var bb_api_sharedoverlays = either(args, 'bb_api_sharedoverlays', '../api/v4/shared_overlay/');
    var bb_api_participants = either(args, 'bb_api_participants', '../api/v4/participant/');
    var bb_api_roles = either(args, 'bb_api_roles', '../api/v4/role');
    var bb_api_join = either(args, 'bb_api_joins', '../join/');
    var bb_api_leave = either(args, 'bb_api_leave', '../leave/');
    var bb_api_heartbeat = either(args, 'bb_api_heartbeat', '../heartbeat/');
    var bb_api_personalviews = either(args, 'bb_api_personalviews', '../api/v4/personal_views/');
    var bb_api_notifications = either(args, 'bb_api_notifications', '../api/v4/notification/');

    var location = [0,0];
    
    
    /* callbacks has the structure:
        
        callbacks = {
            receivedRoom: [
                roomcallback1,
                ...
            ],
            receivedRoles: [
                rolescallback1,
                ...
            ],
            receivedParticipants: [
                participantscallback1,
                ...
            ],
            receivedChats: [
                chatscallback1,
                ...
            ],
            receivedOverlays: [
                overlayscallback1,
                ...
            ],
            receivedSharedOverlays: [
                shared_overlayscallback1,
                ...
            ],
            receivedAnnotations: [
                annotationscallback1,
                ...
            ]
        }
        
    */
    
    // Check if callbacks included in args
    if(args.hasOwnProperty('callbacks')) {
        var callbacks = args.callbacks;
    } else {
        var callbacks = {};
    }
    
    // adds the provided callback function to the callbacks object under the desired type
    function registerCallback(type, func) {
        if( callbacks.hasOwnProperty(type) == false ) {
            callbacks[type] = [];
        }
        callbacks[type].push(func);
    }
    
    // runs all callbacks of the given type, passing obj, textStatus and jqXHR
    function runCallbacks(type,obj,textStatus,jqXHR) {
        if(callbacks.hasOwnProperty(type)) {
            for( i in callbacks[type] ){
                if( callbacks[type].hasOwnProperty(i) ){
                    callbacks[type][i](obj, textStatus, jqXHR);
                }
            }
        } else if(debug) {
            console.log('No callbacks of type: '+type);
        }
    }
    

    if(debug) console.log('creating bigboard object');

    function errorHandler(func) {
        return function(data, textStatus, thrownError) {
            if(debug) {
                console.log(data);
                console.log(textStatus);
                console.log(thrownError);
            }
            return func(data, textStatus, thrownError);
        }
    }

    function receivedAnnotations(data, textStatus, jqXHR) {
        annotations = data.objects;
        if(debug) console.log("latest version of annotations received");
        
        runCallbacks('receivedAnnotations', annotations, textStatus, jqXHR);
        
        //either(args, 'receivedAnnotations', noop)(annotations, textStatus, jqXHR);
        received_annotations = true;
    }

    function receivedChats(data, textStatus, jqXHR) {
        if(data.objects) {
            chats = data.objects;
            if(debug) console.log("latest version of chats received");
            
            runCallbacks('receivedChats', chats, textStatus, jqXHR);
            
            //either(args, 'receivedChats', noop)(chats, textStatus, jqXHR);
            received_chats= true;
            if(chats.length > 0)
                last_chat_update = chats[chats.length-1].id;
        }
    }

    function receivedOverlays(data, textStatus, jqXHR) {
        overlays = data.objects;
        if(debug) console.log("latest version of overlays received");
        
        runCallbacks('receivedOverlays', overlays, textStatus, jqXHR);
        
        //either(args, 'receivedOverlays', noop)(overlays, textStatus, jqXHR);
        received_overlays = true;
    }

    function receivedParticipants(data, textStatus, jqXHR) {
        participants = mergeLeft(participants, data.objects);
        iter(participants, function(p) {
            if(typeof(p.user) !== 'object') {
                $.ajax({
                    async:false,
                    url: p.user,
                    data: {format:'json'},
                    dataType: 'json',
                    success: function(data) {
                        p.user = data;
                    }
                });
            }
        });
        if(debug) console.log("latest version of participants received");
        
        runCallbacks('receivedParticipants', participants, textStatus, jqXHR);
        
        //either(args, 'receivedParticipants', noop)(participants, textStatus, jqXHR);
        received_participants = true;
    }
    
    function receivedRoles(data, textStatus, jqXHR) {
        roles = data.objects;
        if(debug) console.log("latest version of roles received");
        
        runCallbacks('receivedRoles', roles, textStatus, jqXHR);
        
        //either(args, 'receivedRoles', noop)(roles, textStatus, jqXHR);
        received_roles = true;
    }

    function receivedRoom(data, textStatus, jqXHR) {
        room = data.objects[0];
        if(debug) { console.log("latest version of room received");}
        if(debug) { console.log(room);}
        
        runCallbacks('receivedRoom', room, textStatus, jqXHR);
        
        //either(args, 'receivedRoom', noop)(room, textStatus, jqXHR);
        received_room = true;
    }

    function receivedSharedOverlays(data, textStatus, jqXHR) {
        shared_overlays = data.objects;
        if(debug) { console.log("latest version of shared overlays received");}
        
        runCallbacks('receivedSharedOverlays', shared_overlays, textStatus, jqXHR);
        
        //either(args, 'receivedSharedOverlays', noop)(shared_overlays, textStatus, jqXHR);
        received_shared_overlays = true;
    }
    
    function receivedPersonalViews(data, textStatus, jqXHR) {
        personal_views = data.objects;
        if(debug) { console.log("latest version of personal views received"); }
        
        runCallbacks('receivedPersonalViews', personal_views, textStatus, jqXHR);
        
        received_personal_views = true;
    }
    
    function receivedNotifications(data, textStatus, jqXHR) {
        notifications = data.objects;
        if(debug) { console.log("latest version of notifications received"); }
        
        runCallbacks('receivedNotifications', notifications, textStatus, jqXHR);
        
        received_notifications = true;
    }

    function refreshAnnotations() {
        received_annotations = false;
        $.ajax({
            url : bb_api_annotations,
            data : { room : room.id, limit : 0, format : 'json', username : user_name, api_key : api_key },
            accepts : 'application/json',
            success : receivedAnnotations,
            error : errorHandler(either(args, 'refreshAnnotationsError', noop))
        })
    }
    
    function refreshChats() {
        received_chats = false;
        var when = last_chat_update;
        $.ajax({
            url : bb_api_chats,
            data : { room : room.id, limit : 0, id__gt : when, format : 'json', username : user_name, api_key : api_key },
            accepts : 'application/json',
            success : receivedChats,
            error : errorHandler(either(args, 'refreshChatError', noop))
        });
    }

    function refreshOverlays() {
        received_overlays = false;
        var url = bb_api_overlays;
        var data = {
            room__name : room_name,
            limit : 0,
            format : 'json',
            username : user_name,
            api_key : api_key,
            roles__id__in : []
        };

        iter(roles, function(r) {
            data.roles__id__in.push(r.id);
        });

        $.ajax({
            url : url,
            data : {
                room__name : room_name,
                limit : 0,
                format : 'json',
                username : user_name,
                api_key : api_key
            },
            accepts : 'application/json',
            success : receivedOverlays,
            error : errorHandler(either(args, 'refreshOverlaysError', noop))
        });
    }
    
    function refreshParticipants() {
        received_participants = false;
        $.ajax({
            url : bb_api_participants,
            data : { room : room.id, limit : 0, format : 'json', username : user_name, api_key : api_key },
            accepts : 'application/json',
            success : receivedParticipants,
            error : errorHandler(either(args, 'refreshParticipantsError', noop))
        });
    }
    
    function refreshRoles() {
        received_roles = false;
        $.ajax({
            url : bb_api_roles,
            data : { users__id : my_userid, limit : 0, format : 'json', username : user_name, api_key : api_key },
            accepts : 'application/json',
            success : receivedRoles,
            error : errorHandler(either(args, 'refreshRolesError', noop))

        });
    }

    function refreshRoom() {
        received_room = false;
        $.ajax({
            url : bb_api_room,
            data : { name : room_name, format : 'json', username : user_name, api_key : api_key },
            accepts : 'application/json',
            success : receivedRoom,
            error : errorHandler(either(args, 'failedRoomGet', noop)),
            beforeSend : function(xhr) { xhr.setRequestHeader('Authorization', hash)}
        });
    }
    
    function refreshSharedOverlays() {
        received_shared_overlays = false;
        $.ajax({
            url : bb_api_sharedoverlays,
            data : { name : room_name, limit : 0, format : 'json', username : user_name, api_key : api_key },
            accepts : 'application/json',
            success : receivedSharedOverlays,
            error : errorHandler(either(args, 'refreshSharedOverlaysError', noop)),
            beforeSend : function(xhr) { xhr.setRequestHeader('Authorization', hash)}
        });
    }
    
    // Refreshes the personal views list
    function refreshPersonalViews() {
        received_personal_views = false;
        $.ajax({
            url : bb_api_personalviews,
            data : { user__username: user_name, room : room.id, limit : 0, format : 'json', username : user_name, api_key : api_key },
            accepts : 'application/json',
            success : receivedPersonalViews,
            error : errorHandler(either(args, 'refreshPersonalViewsError', noop))
        });
    }
    
    // Refreshes the notifications list
    function refreshNotifications() {
        received_notifications = false;
        $.ajax({
            url : bb_api_notifications,
            data : { get_notifications_for_user: true, room : room.id, limit : 0, format : 'json', username : user_name, api_key : api_key },
            accepts : 'application/json',
            success : receivedNotifications,
            error : errorHandler(either(args, 'refreshNotificationsError', noop))
        });
    }

    function receivedLoginCredentials(data, textStatus, jqXHR) {
        my_userid = data.user_id;
        my_user = data.owner;
        room = data.room;

        $.ajax({
            async : false,
            url : bb_api_roles,
            data : { users__id : my_userid, limit : 0, format : 'json', username : user_name, api_key : api_key },
            accepts : 'application/json',
            success : receivedRoles,
            error : errorHandler(either(args, 'refreshRolesError', noop))
        });

        if(debug) { console.log("succesfully logged in"); }
        
        runCallbacks('loginSuccessful', data, textStatus, jqXHR);
        
        //either(args, 'loginSuccessful', noop)(data, textStatus, jqXHR);
    }

    function join(delay) {
        
        // default delay of 0ms before starting bigboard instance.
        delay = typeof delay !== 'undefined' ? delay : 0;
        
        // the room has been set to start, so other references to this instance
        // should check the started bool and not try to start it.
        started = true;
        
        // delays the starting of the room by delay amount of millisecs
        setTimeout(function() {
            if(!room_name || !user_name || !api_key) {
                console.log("Please define the global variables room, username, and api_key in a script tag above bigboard_mainloop.js. (room, username, and api_key are listed subsequently)");
                console.log(user_name);
                console.log(api_key);
            }
    
            my_username = user_name;
            my_password = api_key;
    
            var tok = user_name + ':' + api_key;
            hash = "Basic " + tok;
    
            $.ajax({
                url : bb_api_join,
                data : { room : room_name },
                accepts : 'application/json',
                success : receivedLoginCredentials,
                error : errorHandler(either(args, 'failedLogin', noop))
            });
        }, delay);

    }

    function resignedLoginCredentials(data, textStatus, jqXHR) {
        my_userid = null;
        if(debug) { console.log('succesfully logged out'); }
        either(args, 'logoutSuccesful', noop)(data, textStatus, jqXHR);
    }

    function leave() {
        $.ajax({
            async: false, // in case an implementor wants to go somewhere after leaving, this ensures that the function completes before the browser leaves.
            url : bb_api_leave,
            accepts : 'application/json',
            success : resignedLoginCredentials,
            error : errorHandler(either(args, 'failedLogout', noop))
        });

        my_userid = null;
    }

    function heartBeat() {
        $.ajax({
            url : bb_api_heartbeat,
            data : { x : location[0], y : location[1] },
            accepts : 'application/json',
            success : function() { if(debug) { console.log("heartbeat"); }},
            error : function(data, textStatus, errorThrown) { my_userid = null; }
        })
    }

    function deleteAnnotation(ann) {
        $.ajax({
            url: ann.attributes.resource_uri + "?username=" + user_name + "&api_key=" + api_key,
            type: 'DELETE',
            error : errorHandler(either(args, 'failedDeleteAnnotation', noop))
        });
    }

    function persistAnnotation(kind, value, feature) {
        var data = {};
        var wkt = JSON.parse(new OpenLayers.Format.GeoJSON().write(feature));
        var file, encoded;
        var wait = false;
        console.log(wkt);

        var reader = new FileReader();

        feature.attributes.sent = true;

        data = {
            associated_overlay: null,
            room : room.resource_uri,
            kind : kind,
            geometry : wkt.geometry,
            text : null,
            media : null,
            audio : null,
            video : null,
            link : null,
            image : null
        };

        switch(kind) {
            case 'audio':
            case 'video':
            case 'image':
            case 'media':
                wait = true;
                file = value;
                break;
            case 'label':
                data.text = value;
                break;
            default:
                data[kind] = value;
                break;
        }

        if(!wait) {
            $.ajax({
                url : bb_api_annotations + '?username=' + user_name + "&api_key=" + api_key,
                type : 'POST',
                data: JSON.stringify(data),
                cache: false,
                contentType: 'application/json',
                processData: false,
                error: errorHandler(noop),
                success: function(data) { console.log('success'); console.log(data); }
            });
            $("#annotation_file").val(null);
            $("#annotation_text").val('');

        }
        else {
            reader.onload = function(event) {
                encoded = btoa(event.target.result);
                data[kind] = { name : file.name, file : encoded };

                $.ajax({
                    url : bb_api_annotations + '?username=' + user_name + "&api_key=" + api_key,
                    type : 'POST',
                    data: JSON.stringify(data),
                    cache: false,
                    contentType: 'application/json',
                    processData: false,
                    error: errorHandler(noop),
                    success: function(data) { console.log('success'); console.log(data); }
                });

            };
            reader.readAsBinaryString(file);
        }

    }

    function sendChat(chat_text, success, fail) {
        var has_at = /@[A-z_0-9]+/;
        var has_whisper = /^\/msg [A-z_0-9]+/;
        var at = [];
        var priv = false;

        if(has_at.test(chat_text)) {
            at = [has_at.exec(chat_text).substring(1)];
        }

        if(has_whisper.test(chat_text)) {
            priv = true;
            at = [has_whisper.exec(chat_text).substring(4)];
        }

        var data = {
            text: chat_text,
            at: at,
            "private" : priv,
            user : my_user,
            room : room.resource_uri,
            where : { coordinates: [location[0], location[1]], type:'Point' }
        };

        $.ajax({
            url : bb_api_chats + '?username=' + user_name + "&api_key=" + api_key,
            success : success,
            contentType: 'application/json',
            error : fail,
            type: "POST",
            data: JSON.stringify(data),
            dataType: 'json',
            processData: false
        });
    }

    function shareLayer(overlay) {
        $.ajax({
            type : 'POST',
            contentType: 'application/json',
            dataType: 'json',
            processData: false,
            url : bb_api_sharedoverlays + "?username=" + user_name + "&api_key=" + api_key,
            data : JSON.stringify({
                room: room.resource_uri,
                user: my_user,
                shared_with_all: true,
                shared_with_roles: [],
                shared_with_users: [],
                overlay : overlay.resource_uri
            })
        });
    }

    function unshareLayer(overlay) {
        $.ajax({
            async: false,
            url : bb_api_sharedoverlays,
            data : {
                username : user_name,
                api_key : api_key,
                overlay__id : overlay.id
            },
            success: function(data) {
                iter(data.objects, function(o) {
                    $.ajax({ type: 'DELETE', url: o.resource_uri + "?username=" + user_name + "&api_key=" + api_key });
                })
            }
        });
    }

    function setRoomCenter(lon, lat, zoom) {
        $.get(bb_api_center, {
            x:lon,
            y:lat,
            z:zoom
        }, errorHandler(noop));
    }
    
    function getRoomCenter() {
        return $.extend({},room.center,{zoom_level:room.zoom_level});
    }

    var once = true;
    function mainLoop() {
        if(my_userid) {
            if(room) {
                heartBeat();
                if(once) {
                    refreshAnnotations();
                    refreshRoles();
                    refreshOverlays();
                    refreshParticipants();
                    refreshSharedOverlays();
                    refreshChats();
                    refreshPersonalViews();
                    refreshNotifications();
                    once = false;
                }
            }

            if(received_annotations) { refreshAnnotations(); }
            if(received_chats) { refreshChats(); }
            if(received_overlays) { refreshOverlays(); }
            if(received_participants) { refreshParticipants(); }
            if(received_roles) { refreshRoles(); }
            if(received_shared_overlays) { refreshSharedOverlays(); }
            if(received_room) { refreshRoom(); }
            if(received_personal_views) { refreshPersonalViews(); }
            if(received_notifications) { refreshNotifications(); }
        }
    }

    function start(delay) {
        
        if(navigator.geolocation) {
            navigator.geolocation.watchPosition(function(position) {
               location = [position.coords.longitude, position.coords.latitude];
            });
            if(debug) console.log('watching location');
        }

        if(debug) console.log('starting main loop');
        refreshRoom();
        main_loop = setInterval(mainLoop, 3000);
    }

    function end() {
        clearInterval(main_loop);
    }
    
    function isStarted() {
        return started;
    }
    
    // Add a personal view to the server
    function addPersonalView(name, description, lon, lat, zoom) {
        var data = {
            name: name,
            description: description,
            user : my_user,
            room : room.resource_uri,
            zoom_level: zoom,
            where : { coordinates: [lon, lat], type:'Point' }
        };
        
        $.ajax({
            url : bb_api_personalviews + '?username=' + user_name + "&api_key=" + api_key,
            type : 'POST',
            data: JSON.stringify(data),
            cache: false,
            contentType: 'application/json',
            processData: false,
            error: errorHandler(noop),
            success: function(data) { console.log('success'); console.log(data); }
        });
    }
    
    // Remove the personal view from the server
    function deletePersonalView(view) {
        $.ajax({
            url: view.resource_uri + "?username=" + user_name + "&api_key=" + api_key,
            type: 'DELETE',
            error : errorHandler(either(args, 'failedDeleteAnnotation', noop))
        });
    }
    
    // Add a bbnotification to the server
    function addNotification(subject, body, level, shared_with_roles, shared_with_all, lon, lat, zoom) {
        var data = {
            subject: subject,
            body: body,
            level: level,
            shared_with_roles: shared_with_roles,
            shared_with_all: shared_with_all,
            user : my_user,
            room : room.resource_uri,
            zoom_level: zoom,
            where : { coordinates: [lon, lat], type:'Point' }
        };
        
        $.ajax({
            url : bb_api_notifications + '?username=' + user_name + "&api_key=" + api_key,
            type : 'POST',
            data: JSON.stringify(data),
            cache: false,
            contentType: 'application/json',
            processData: false,
            error: errorHandler(noop),
            success: function(data) { console.log('success'); console.log(data); }
        });
    }

    return {
        room : room_name,
        user_id : my_userid,
        username : my_username, // DEPRECATED
        password : my_password, // DEPRECATED
        location : location,
        
        isStarted: isStarted,

        start : start,
        end : end,
        join: join,
        leave: leave,
        sendChat: sendChat,
        shareLayer: shareLayer,
        unshareLayer: unshareLayer,
        persistAnnotation: persistAnnotation,
        deleteAnnotation: deleteAnnotation,
        setRoomCenter: setRoomCenter,
        getRoomCenter: getRoomCenter,
        addPersonalView: addPersonalView,
        deletePersonalView: deletePersonalView,
        addNotification: addNotification,
        
        registerCallback: registerCallback
    };

}