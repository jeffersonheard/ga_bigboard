// Chat widget for the bigboard

$(document).ready(function() {
    
    $('head').append('<scr'+'ipt type="text/javascript" src="'+STATIC_URL+'ga_bigboard/functools.js"></scr'+'ipt>');
    $('head').append('<scr'+'ipt type="text/javascript" src="'+STATIC_URL+'ga_bigboard/bigboard_mainloop.js"></scr'+'ipt>');
    
    
    $('#'+viewid).html('');
    var chatarea = $('<div/>', {
                        id: 'chat_log'
                    }).appendTo('#'+viewid);
    
    var bb = BigBoard({
        room_name : 'room1',
        username: 'admin',
        password: 'admin',
        user_id: undefined,
        debug: true,
        
        loginSuccessful : function(data) {
            console.log('starting data streams');
            bb.start();
        },
        receivedRoles: function(data) {
            roles = data;
        },
        receivedParticipants: function(data) {
                participants = {};

                iter(data, function(participant) {
                    participants[participant.user.resource_uri] = participant;
                });
        },
        
        receivedChats: function(data) {
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
                    chat_record.append("<span class='chat_time'>" + timestamp.toTimeString().substring(0,6) + "</span> ");
                    chat_record.append("<span class='chat_username'>" + participants[chat.user].user.username + "-</span> ");
                    chat_record.append("<span class='chat_text'>" + chat.text + "</span>");
                    $("#chat_log").append(chat_record);
                }
            });
            if(data.length > 0) {
                $("#chat_log").scrollTop($("#chat_log").scrollTop() + $("#chat_log>*").last().position().top);
            }
        }
        
    });
    
    
    
    bb.join('room1','admin','admin');
    
    

});


