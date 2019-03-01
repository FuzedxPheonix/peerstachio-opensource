$(function() {
  // Reference to the chat messages area
  // console.log("User logged in as: ", username);
  let $app = $("#chat-app");
  let $chatWindow = $("#messages");
  let $threadMessageWindow = $("#thread-messages");
  let $onlineWindow = $(".peers");
  let $unansweredQuestions = $(".unanswered-qs-dropdown");

  let chatWindow = document.querySelector("#messages");
  let threadWindow = document.querySelector(".thread-wrapper");
  let threadScroll = document.querySelector(".thread-scroll");
  let onlineWindow = document.querySelector(".peers");
  let unansweredQuestions = document.querySelector(".unanswered-qs-dropdown");

  function insert_is_online(element) {
    let $peercontainer = $('<div class="peer">');

    let $peername = $(`<div class="peer-name">${element.username}</div>`);

    let $peeruni = $(`<div class="peer-uni"> ${element.grad_year === 0 ? "" :
      `Class of ${element.grad_year}`} </div>`);

    let $peerpic = $(
      '<img class="peer-pic" src="/static/images/specialist (1).png">'
    );

    // Contains all the universty student information
    $peercontainer.append($peerpic);
    $peercontainer.append($peername);
    $peercontainer.append($peeruni);

    $onlineWindow.append($peercontainer);
  }
  function update_is_online(data) {
    var parse_data = JSON.parse(data);
    $onlineWindow.empty();

    parse_data.forEach(insert_is_online);
  }

  function update_like(message_id) {
    // console.log("calls json");
  }

  // Loads all json files for the chat room
  $.getJSON(
    "chats/chat_message_json",
    {
      device: "browser",
      slug: room_name_slug
    },
    function(data) {
      load_chat_json(data);
    }
  );

  // loads all threads that are questions

  $.getJSON(
    "chats/all_answers",
    {
      device: "browser",
      slug: room_name_slug
    },
    function(data) {
      // Gets the container of the questions on the paragraph
      // This would be the top div to make the unanswered questions
      let $divTopQuestion = $(
        `<p onclick="showQs()" id="top-list-question" 
        data-qsnum="${data.length}">
        <span class="line-icon"></span>
        ${data.length} unanswered questions </p>`
      );

      let $onlineTop = $(".chat-top");
      $onlineTop.prepend($divTopQuestion);

      load_all_questions(data);
    }
  );

  // Loads online user for the files
  $.getJSON(
    "chats/chat_online_users",
    {
      device: "browser",
      slug: room_name_slug
    },
    function(data) {
      $onlineWindow.empty();
      data.forEach(insert_is_online);
    }
  );

  function load_all_questions(data) {
    data.forEach(function(element) {
      let $questionContainer = $('<div class="message-container">');

      let $userContainer = $('<span class="user">');
      let $userImage = $(
        '<img class="user-img" src="/static/images/specialist (1).png">'
      );
      let $userName = $(
        '<p class="user-name">' + element.fields.user[0] + "</p>"
      );

      $userContainer.append($userImage);
      $userContainer.append($userName);
      $questionContainer.append($userContainer);

      let $message = $(
        '<span class="message">' + element.fields.message + "</span>"
      );

      $questionContainer.append($message);

      let $messageResponseContainer = $('<span class="message-response">');

      let $iconContainer = $('<span class="line-icon"></span>');

      let $pContainer = $(
        "<p>" + "Respond to " + element.fields.user[0] + "'s question" + "</p>"
      );

      $pContainer.prop("value", element.pk);
      $pContainer.click(
        {
          username: element.fields.user[0],
          message: element.fields.message,
          messageid: element.pk,
          timestamp: element.fields.timestamp
        },
        get_thread_json
      );

      $messageResponseContainer.append($iconContainer);
      $messageResponseContainer.append($pContainer);

      $questionContainer.append($messageResponseContainer);

      $unansweredQuestions.append($questionContainer);
    });
  }

  function get_thread_json(event) {
    threadWindow.querySelector("h3").innerHTML =
      event.data.username + "'s question";
    // This loads in the json for threaded questions
    $.getJSON(
      "chats/chat_thread_message_json",
      {
        device: "browser",
        slug: this.value
      },
      function(data) {
        var json_obj = JSON.parse(data.response);

        if (current_thread_id == data.slug) {
          return;
        } else {
          current_thread_id = data.slug;
          remove_thread_messages();
        }

        $app.addClass("threaded");
        document.querySelector(".thread-wrapper").style.display = "flex";

        format_message(
          event.data.username,
          event.data.message,
          false,
          event.data.messageid,
          event.data.timestamp,
          $threadMessageWindow,
          true,
          null,
          true
        );

        if (json_obj && json_obj.length) {
          load_thread_json(event, json_obj);
        }
      }
    );
  }

  function load_thread_json(event, data) {
    data.forEach(function(message) {
      format_message(
        message.fields.user[0],
        message.fields.message,
        false,
        message.pk,
        message.fields.timestamp,
        $threadMessageWindow,
        false,
        null,
        true
      );
    });
  }

  function sendMessage(message, isThread, callback) {
    chatSocket.send(
      JSON.stringify({
        message: message,
        isThread: isThread,
        thread_obj: false
      })
    );
    // Adds the message to the window
    chatSocket.onmessage = function(e) {
      var data = JSON.parse(e.data);
      var json_response_message = JSON.parse(data["message_obj"]);
      if (data["thread_obj"]) {
        format_message(
          json_response_message[0].fields.user[0],
          json_response_message[0].fields.message,
          false,
          json_response_message[0].pk,
          time,
          json_response_message[0].fields.timestamp,
          false,
          0,
          data
        );
      } else {
        if (data.is_thread) {
          format_message(
            json_response_message[0].fields.user[0],
            json_response_message[0].fields.message,
            isThread,
            data.slug,
            json_response_message[0].fields.timestamp,
            $chatWindow,
            false,
            0,
            data
          );
        } else {
          format_message(
            json_response_message[0].fields.user[0],
            json_response_message[0].fields.message,
            isThread,
            json_response_message[0].pk,
            json_response_message[0].fields.timestamp,
            $chatWindow,
            false,
            0,
            data
          );

          update_is_online(data.all_online_users);
        }
      }
      if (callback) {
        callback();
      }
    };
  }

  function load_chat_json(message_json) {
    // this focuses on what data is going to be sent to the message item in chat
    message_json.forEach(function(data) {
      // This is a good print out section to debug anything with json response
      // console.log(data);

      format_message(
        data.fields.user[0],
        data.fields.message,
        data.fields.thread,
        data.pk,
        data.fields.timestamp,
        $chatWindow,
        null,
        data.fields.chat_thread_respose_total,
        data
      );
    });

    $("#loader").hide();
    $("#chat-app").css("display", "grid");
    // must come after display: grid else height won't be adjusted
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  let $message_form = $("#message-form");
  $message_form.on("submit", function(e) {
    e.preventDefault();
    var new_message = document.getElementById("message-input").value;
    var isThread = document.querySelector("#mark-qs input").checked;

    let $input = $("#message-input");

    if ($input.val().trim().length > 0) {
      sendMessage($input.val(), isThread, () => {
        // reset defaults
        $input.val("");
        document.querySelector("button").classList.remove("active");
        document.querySelector("#mark-qs input").checked = false;
        chatWindow.scrollTop = chatWindow.scrollHeight;
      });
    }
  });

  function sendThreadMessage(message) {
    chatSocket.send(
      JSON.stringify({
        message: message,
        thread_obj: true,
        slug: current_thread_id
      })
    );

    chatSocket.onmessage = function(e) {
      var data = JSON.parse(e.data);
      var json_response_message = JSON.parse(data["message_obj"]);
      if (data["thread_obj"]) {
        format_message(
          json_response_message[0].fields.user[0],
          json_response_message[0].fields.message,
          false,
          json_response_message[0].pk,
          json_response_message[0].fields.timestamp,
          $threadMessageWindow,
          null,
          null,
          data
        );
      } else {
        format_message(
          json_response_message[0].fields.user[0],
          json_response_message[0].fields.message,
          isThread,
          json_response_message[0].pk, //how are we gonna get the message id over here?
          json_response_message[0].fields.timestamp,
          $chatWindow,
          null,
          null,
          data
        );
      }
    };
  }

  let $thread_form = $("#thread-form");
  $thread_form.on("submit", function(e) {
    e.preventDefault();

    let $input = $("#thread-input");

    if ($input.val().trim().length > 0) {
      // console.log("Testing thread", this);
      sendThreadMessage($input.val());
      threadWindow.scrollTop = threadWindow.scrollHeight;
      $input.val("");
      // $thread_form.querySelector('button').classList.remove('active')
    }
  });


  /* 
  format_message: formats sent/received message on page
  @param fromUser: user that sent the message
  @param message: message content
  @param isThread: whether the message obj is a thread 
  @param messageid: id of message
  @param timestamp: time message is sent
  @param window: window that message is sent to ($chatWindow/$threadWindow)
  @param isThreadHeader: indicate if it is the question for the thread 
  @param total: total replies to thread
  @param data: entire data input
  */
  function format_message(
    fromUser,
    message,
    isThread,
    messageid,
    timestamp,
    window,
    isThreadHeader = false,
    total,
    data
  ) {
    // This formats how the message is printed when the json is loaded first
    let $user_name = $('<p class="user-name">' + fromUser + "</p>"); // This value is important for value
    // $user.prepend('<img class="user-img" src="/static/images/specialist (1).png" />');
    let $user_img = $(
      '<div class="user-img">' + fromUser[0].toUpperCase() + "</div>"
    );


    let $messageText = $('<p class="message-text">').text(message);
    $messageText.linkify({
      target: "_blank"
    });

    let $message = $('<div class="message">');
    $message.append($messageText);

    let $thanks_container = $('<div class="say-thanks">');

    let $say_thanks = $("<div onclick=showPopup(this)>")
      .append($(svg))
      .append("<p>Say thanks to " + fromUser + "</p>");

    let $you_said_thanks = $("<div style='cursor: auto;'>")
      .append($(svg))
      .append("<p>You said thanks to " + fromUser + "!</p>");

    // console.log(data)
    // if (data.test_bool) {
    //   $thanks_container.attr("booltest", true);
    // } else {
    //   $thanks_container.attr("booltest", false);
    // }

    if (data.thanked) {
      $say_thanks.addClass('no-show')
      $you_said_thanks.addClass('show')
    } else {
      $say_thanks.addClass('show')
      $you_said_thanks.addClass('no-show')
    }
    $thanks_container.append($say_thanks);
    $thanks_container.append($you_said_thanks);

    let $thanks_wrapper = $('<div class="thanks-wrapper">');
    $thanks_wrapper.append($thanks_container);

    let $timestamp = $('<div class="timestamp">');
    let date = new Date(timestamp);

    if (window.attr("id") == "messages") {
      $timestamp.append(
        date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      );
    } else {
      let dateArr = date.toLocaleDateString().split("/");
      let months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec"
      ];
      $timestamp.append(
        months[dateArr[0] - 1] +
        " " +
        dateArr[1] +
        ", " +
        dateArr[2] +
        " at " +
        date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      );
    }

    function msToTime(duration) {
      var milliseconds = parseInt((duration % 1000) / 100),
        seconds = parseInt((duration / 1000) % 60),
        minutes = parseInt((duration / (1000 * 60)) % 60),
        hours = parseInt((duration / (1000 * 60 * 60)) % 12);

      var antepost = parseInt((duration / (1000 * 60 * 60)) % 24);

      // hours = hours < 10 ? '0' + hours : hours
      minutes = minutes < 10 ? "0" + minutes : minutes;
      // seconds = (seconds < 10) ? "0" + seconds : seconds;

      return hours + ":" + minutes + (antepost > 12 ? " PM" : " AM");
    }

    let $container = $('<div class="message-container">');
    $container.hover(toggleSayThanksButton, toggleSayThanksButton);

    if (isThreadHeader) {
      $container.addClass("thread-header");
    }

    if (fromUser === username && !isThreadHeader) {
      $container.addClass("me");
    }

    $container
      .append($user_img)
      .append($timestamp)
      .append($user_name)
      .append($message)


    if (!isThread && fromUser != username && !isThreadHeader) {
      $container.append($thanks_wrapper);
    }

    if (isThread) {
      $container.addClass("question");
      // This checks if it is a thread or not and whether or not you want to reply to it
      let $reply_thread = $(
        `<div class="qs-details">
        <p>` +
        total +
        ` Replies</p>
        <div class="message-response">
            <span class="line-icon"></span>
            <p>Respond to ` +
        fromUser +
        `'s question</p>
        </div>
      </div>`
      );
      $reply_thread.prop("value", messageid);
      $reply_thread.click(
        {
          username: fromUser,
          message: message,
          messageid: messageid,
          timestamp: timestamp
        },
        get_thread_json
      );
      $message.append($reply_thread);
    }
    // console.log("[DEBUG] total thanks: ", data.total_thanks);
    // console.log("[DEBUG] data: ", data);
    update_thanks_badge(data.total_thanks, $messageText)


    $thanks_container.attr("uniqueid", messageid);

    window.append($container);

    window.scrollTop = window.scrollHeight;
  }
});


function update_thanks_badge(total, container = null) {
  let chatWindowPosition = document.querySelector("#messages").scrollTop;
  let threadWindowPosition = document.querySelector(".thread-wrapper").scrollTop;
  container.children('.bottom-right-badge').remove();
  if (total > 0) {
    let $svg_thanks = $(svg);
    let $thanks_display = $(
      `<div class="bottom-right-badge">`).append($svg_thanks)
    $thanks_display.append(` ${total}</div>`)
    container.append($thanks_display)
  }

  document.querySelector("#messages").scrollTop = chatWindowPosition;
  document.querySelector(".thread-wrapper").scrollTop = threadWindowPosition;
}

function update_thanks_button(thanked, container = null) {
  let chatWindowPosition = document.querySelector("#messages").scrollTop;
  let threadWindowPosition = document.querySelector(".thread-wrapper").scrollTop;

  if (thanked) {
    container.children[0].classList.add('no-show')
    container.children[0].classList.remove('show')
    container.children[1].classList.remove('no-show')
    container.children[1].classList.add('show')
  } else {
    container.children[1].classList.add('no-show')
    container.children[1].classList.remove('show')
    container.children[0].classList.remove('no-show')
    container.children[0].classList.add('show')
  }
  container.children[0].style.display = "";
  container.children[1].style.display = "";

  document.querySelector("#messages").scrollTop = chatWindowPosition;
  document.querySelector(".thread-wrapper").scrollTop = threadWindowPosition;
}

function toggleSayThanksButton(e) {
  // if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|BB|PlayBook|IEMobile|Windows Phone|Kindle|Silk|Opera Mini/i.test(navigator.userAgent)) {
  //   // Take the user to a different screen here.
  // } else {
  let chatWindowPosition = document.querySelector("#messages").scrollTop;
  let threadWindowPosition = document.querySelector(".thread-wrapper").scrollTop;
  if (this.querySelector(".show")) {
    if (e.type == "mouseenter") {
      this.querySelector(".show").style.display = "flex";
    } else {
      this.querySelector(".show").style.display = "";
    }
  }
  document.querySelector("#messages").scrollTop = chatWindowPosition;
  document.querySelector(".thread-wrapper").scrollTop = threadWindowPosition;
  // }
}

var svg = `<svg class="logo-svg" height="17px" viewBox="0 0 42 37" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <!-- Generator: Sketch 51.3 (57544) - http://www.bohemiancoding.com/sketch -->
  <title>Peerstachio Logo</title>
  <desc>Created with Sketch.</desc>
  <defs></defs>
  <g id="Symbols" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
      <g id="Artboard" transform="translate(-13.000000, -17.000000)">
          <g id="Group-2" transform="translate(15.000000, 18.000000)">
              <g id="Group" transform="translate(0.000000, 1.000000)" fill-rule="nonzero">
                  <path d="M6.19687928,0.826843686 L18.401212,16.1118352 L30.5343913,0.764067869 C34.3768335,4.13662151 36.8024241,9.08444122 36.8024241,14.598788 C36.8024241,24.7614968 28.5639208,33 18.401212,33 C8.23850325,33 0,24.7614968 0,14.598788 C0,9.11855696 2.39567051,4.19786478 6.19687928,0.826843686 Z" id="Combined-Shape" stroke="#1EA348" stroke-width="3" fill="#FFFFFF"></path>
                  <path d="M10,3.76868462 L18.0390589,15.3202889 L26.372973,3.76868462 C24.127248,1.76560679 21.3984192,0.764067869 18.1864865,0.764067869 C14.9745538,0.764067869 12.245725,1.76560679 10,3.76868462 Z" id="Path" fill="#1EA348"></path>
              </g>
          </g>
      </g>
  </g>
</svg>`