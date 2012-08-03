var map;

function BigBoard(args) {
    var overlays;
    var shared_overlays;
    var participants;
    var room;
    var chats = [];
    var roles;
    var annotations;
    var last_chat_update = 0;

    var received_annotations = false;
    var received_chats = false;
    var received_overlays = false;
    var received_participants = false;
    var received_roles = false;
    var received_room = false;
    var received_shared_overlays = false;


    // TODO - all this stuff can be simplified now that room, username, and api_key are part of the global variable stack.
    var my_username = user_name;
    var my_password = api_key;
    var my_userid = either(args, 'user_id', null);
    var my_user = either(args, 'user', null);
    var debug = either(args, 'debug', false);
    var main_loop;
    var hash;

    var location = [0,0];

    console.log('creating bigboard object');

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
        either(args, 'receivedAnnotations', noop)(annotations, textStatus, jqXHR);
        received_annotations = true;
    }

    function receivedChats(data, textStatus, jqXHR) {
        if(data.objects) {
            //chats = sift(chats, data.objects, function(i) { i.when = new Date(i.when); return i.when; }); // should merge in the list with the "when" attribute used as key.
            chats = data.objects;
            if(debug) console.log("latest version of chats received");
            either(args, 'receivedChats', noop)(chats, textStatus, jqXHR);
            received_chats= true;
            if(chats.length > 0)
                last_chat_update = chats[chats.length-1].id;
        }
    }

    function receivedOverlays(data, textStatus, jqXHR) {
        overlays = data.objects;
        if(debug) console.log("latest version of overlays received");
        either(args, 'receivedOverlays', noop)(overlays, textStatus, jqXHR);
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
        either(args, 'receivedParticipants', noop)(participants, textStatus, jqXHR);
        received_participants = true;
    }
    
    function receivedRoles(data, textStatus, jqXHR) {
        roles = data.objects;
        if(debug) console.log("latest version of roles received");
        either(args, 'receivedRoles', noop)(roles, textStatus, jqXHR);
        received_roles = true;
    }

    function receivedRoom(data, textStatus, jqXHR) {
        room = data.objects[0];
        if(debug) { console.log("latest version of room received");}
        if(debug) { console.log(room);}
        either(args, 'receivedRoom', noop)(room, textStatus, jqXHR);
        received_room = true;
    }

    function receivedSharedOverlays(data, textStatus, jqXHR) {
        shared_overlays = data.objects;
        if(debug) { console.log("latest version of shared overlays received");}
        either(args, 'receivedSharedOverlays', noop)(shared_overlays, textStatus, jqXHR);
        received_shared_overlays = true;
    }

    function refreshAnnotations() {
        received_annotations = false;
        $.ajax({
            url : '../api/v4/annotation/',
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
            url : '../api/v4/chat/',
            data : { room : room.id, limit : 0, id__gt : when, format : 'json', username : user_name, api_key : api_key },
            accepts : 'application/json',
            success : receivedChats,
            error : errorHandler(either(args, 'refreshChatError', noop))
        });
    }

    function refreshOverlays() {
        received_overlays = false;
        var url = '../api/v4/overlay/?';
        iter(roles, function(r) {
            url += "roles__id__in=" + r.id + "&"
        });
        url = url.substring(0, url.length-1);

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
            url : '../api/v4/participant/',
            data : { room : room.id, limit : 0, format : 'json', username : user_name, api_key : api_key },
            accepts : 'application/json',
            success : receivedParticipants,
            error : errorHandler(either(args, 'refreshParticipantsError', noop))
        });
    }
    
    function refreshRoles() {
        received_roles = false;
        $.ajax({
            url : '../api/v4/role/',
            data : { users__id : my_userid, limit : 0, format : 'json', username : user_name, api_key : api_key },
            accepts : 'application/json',
            success : receivedRoles,
            error : errorHandler(either(args, 'refreshRolesError', noop))

        });
    }

    function refreshRoom() {
        received_room = false;
        $.ajax({
            url : '../api/v4/room/',
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
            url : '../api/v4/shared_overlay/',
            data : { name : room_name, limit : 0, format : 'json', username : user_name, api_key : api_key },
            accepts : 'application/json',
            success : receivedSharedOverlays,
            error : errorHandler(either(args, 'refreshSharedOverlaysError', noop)),
            beforeSend : function(xhr) { xhr.setRequestHeader('Authorization', hash)}
        });
    }

    function receivedLoginCredentials(data, textStatus, jqXHR) {
        my_userid = data.user_id;
        my_user = data.owner;
        room = data.room;

        $.ajax({
            async : false,
            url : '../api/v4/role/',
            data : { users__id : my_userid, limit : 0, format : 'json', username : user_name, api_key : api_key },
            accepts : 'application/json',
            success : receivedRoles,
            error : errorHandler(either(args, 'refreshRolesError', noop))
        });

        if(debug) { console.log("succesfully logged in"); }
        either(args, 'loginSuccessful', noop)(data, textStatus, jqXHR);
    }

    function join(room) {
        if(!room_name || !user_name || !api_key) {
            console.log("Please define the global variables room, username, and api_key in a script tag above bigboard_mainloop.js. (room, username, and api_key are listed subsequently)");
            console.log(room);
            console.log(user_name);
            console.log(api_key);
        }

        my_username = user_name;
        my_password = api_key;

        var tok = user_name + ':' + api_key;
        hash = "Basic " + tok;

        $.ajax({
            url : '../join/',
            data : { room : room_name },
            accepts : 'application/json',
            success : receivedLoginCredentials,
            error : errorHandler(either(args, 'failedLogin', noop))
        });

    }

    function resignedLoginCredentials(data, textStatus, jqXHR) {
        my_userid = null;
        if(debug) { console.log('succesfully logged out'); }
        either(args, 'logoutSuccesful', noop)(data, textStatus, jqXHR);
    }

    function leave() {
        $.ajax({
            async: false, // in case an implementor wants to go somewhere after leaving, this ensures that the function completes before the browser leaves.
            url : '../leave/',
            accepts : 'application/json',
            success : resignedLoginCredentials,
            error : errorHandler(either(args, 'failedLogout', noop))
        });

        my_userid = null;
    }

    function heartBeat() {
        $.ajax({
            url : '../heartbeat/',
            data : { x : location[0], y : location[1] },
            accepts : 'application/json',
            success : function() { if(debug) { console.log("heartbeat"); }},
            error : function(data, textStatus, errorThrown) { my_userid = null; }
        })
    }

    function persistAnnotation(feature) {
        var kind = $("#annotation_kind").val();
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
                file = $("#annotation_file")[0].files[0];
                wait = true;
                break;
            default:
                data[kind] = $("#annotation_text").val();
                break;
        }

        if(!wait) {
            $.ajax({
                url : '../api/v4/annotation/?username=' + user_name + "&api_key=" + api_key,
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
                data[kind] = { name : $("#annotation_file")[0].files[0].name, file : encoded };

                $.ajax({
                    url : '../api/v4/annotation/?username=' + user_name + "&api_key=" + api_key,
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
            url : '../api/v4/chat/?username=' + user_name + "&api_key=" + api_key,
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
            url : '../api/v4/shared_overlay/' + "?username=" + user_name + "&api_key=" + api_key,
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
            url : '../api/v4/shared_overlay/',
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
        }
    }

    function start() {

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

    return {
        room : room_name,
        user_id : my_userid,
        username : my_username,
        password : my_password,
        location : location,

        start : start,
        end : end,
        join: join,
        leave: leave,
        sendChat: sendChat,
        shareLayer: shareLayer,
        unshareLayer: unshareLayer,
        persistAnnotation: persistAnnotation
    };

}