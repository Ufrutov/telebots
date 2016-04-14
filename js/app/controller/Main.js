app.controller("Main", ['$scope','$cookies', '$cookieStore', '$location', 'global', 'util',
	// Launch Bot application
	function($scope, $cookies, $cookieStore,  $location, global, util) {
		global.main = $scope;

		// Switch Login/Sign form at the Enter modal dialog 
		$scope.openLogin = function(e) {
			global.enter = e;
			if( e == "login" ) {
				$(".sign-tab a.log-in-tab").tab("show");
				$("#sign-in-tab").hide();
				$("#log-in-tab").show();
			} else {
				$(".sign-tab a.sign-in-tab").tab("show");
				$("#log-in-tab").hide();
				$("#sign-in-tab").show();
			}
			return;
		}

		$scope.logOut = function() {
			$cookies.remove("user");
			util.switchView("enter");
		}

		$scope.getUpdates = function() {
			$scope.resetList(["chats", "updates", "messages", "crons"], "loading");

			if( global.user != null && global.active != null ) {
				util.request("get_updates", { "bot_id": global.active.id }, function(response) {
					$scope.updateList("chats", response.chats);
					$scope.updateList("updates", response.updates);

					global.chats = response.chats;
				});
				util.request("get_messages", { "bot_id": global.active.id }, function(response) {
					$scope.updateList("messages", response);
				});
				util.request("get_crons", { "bot_id": global.active.id, "cron_id": "all" }, function(response) {
					$scope.updateList("crons", response);
				});
			} else {
				console.log("[getUpdates] error");
				$scope.resetList(["chats", "updates", "messages", "crons"], "empty");
			}
		}

		$scope.resetList = function(target, tmp) {
			var reset = function(el){
				switch(el) {
					case "chats":
						$scope.chats = [{}];
						$scope.chat_list = global.tmp[tmp];
						break;
					case "updates":
						$scope.updates = [{}];
						$scope.updates_list = global.tmp[tmp];
						break;
					case "messages":
						$scope.messages = [{}];
						$scope.messages_list = global.tmp[tmp];
						break;
					case "crons":
						$scope.crons = [{}];
						$scope.crons_list = global.tmp[tmp];
						break;
				}
			}
			if( typeof target != "string" )
				$.each(target, function(i, el) {
					reset(el);
				});
			else
				reset(target);
		}

		$scope.updateList = function(target, data) {
			var empty = ( data.length > 0 ) ? false : global.tmp.empty;
			switch(target) {
				case "chats":
					$scope.chat_list = ( !empty ) ? global.tmp.chat_list : empty;
					if( data.length > 0 )
						$.each(data, function(i, item) {
							item.username = (item.username.indexOf("@") != 0) ? "@"+item.username : item.username;
						});
					$scope.chats = data;
					break;
				case "updates":
					if( data.length > 0 )
						$.each(data, function(i, item) {
							item.date = util.formatDate(new Date(item.message.date*1000));
							item.username = "@"+item.message.chat.username;
						});
					$scope.updates_list = ( !empty ) ? global.tmp.updates_list : empty;
					$scope.updates = ( data.length > 0 ) ? data : [{}];
					break;
				case "messages":
					if( data.length > 0 )
						$.each(data, function(i, msg) {
							msg.date = util.formatDate(new Date(msg.date*1000));
							var chats = [];
							$.each( msg.chat.split(","), function(i, c) { chats.push("@"+c) } );
							msg.chat = chats.join(", ");
						});
					$scope.messages_list = ( !empty ) ? global.tmp.messages_list : empty;
					$scope.messages = ( data.length > 0 ) ? data : [{}];
					break;
				case "crons":
					$.each( data, function(i, cron) {
						var dts = [];
						$.each( cron.date.split(","), function(i, c){ dts.push( util.formatDate(new Date(c*1000)) ) } );
						cron.dts = dts.join(", ");
						
						cron.enable = (cron.enable) ? true : false;
						chats = [];
						$.each( cron.chat_id.split(","), function(i, c) { ( c.indexOf("@") != 0 ) ? chats.push("@"+c) : chats.push(c) } );
						cron.chat = chats.join(", ");
					});
					$scope.crons_list = ( !empty ) ? global.tmp.crons_list : empty;
					$scope.crons = ( data.length > 0 ) ? data : [{}];
					break;
			}
		}

		// Switch main view for new selected bot
		$scope.activateBot = function(botId) {
			// Selected active bot
			if( global.active != null && global.active.id == botId )
				return;

			angular.forEach(global.user.bots, function(bot, i) {
				if( bot.id == botId ) {
					global.active = bot;
					global.user.active = bot;
					$scope.activeBotName = bot.username;
					$cookies.putObject("user", global.user);
					$scope.getUpdates();
					return;
				}
			});
		}

		$scope.addBot = function(token, user_id) {
			if( token.length > 0 ) {
				if( token.length < 10 ) {
					$('#add-bot-token').parent('.form-group').addClass("has-error");
			    	$('#add-bot-token').prev('.control-label').html("Wow, Your bots token is so cool!");
					return false; }
				
				util.request("add_bot", { "user_id": user_id, "token": token }, function(response) {
					if( response.ok && response.bot.length > 0 ) {
						// Set active bot and run updates
						global.user.bots = response.bots;
						$scope.bots = response.bots;
						$scope.activateBot(response.bot[0].id);
					} else {
						$('#add-bot-token').parent('.form-group').addClass("has-error");
						var error = ( response ) ? response.status : "Unauthorized token or communicate error";
			    		$('#add-bot-token').prev('.control-label').html(error);
					}
				});
			}
		}

		$scope.addChannel = function(channel, user_id) {
			console.log(channel, user_id, global.active);
			if( channel.length > 0 && global.active != null ) {
				channel = ( channel.indexOf("@") != 0 ) ? "@"+channel : channel;
				util.request("add_channel", { "user_id": user_id, "channel": channel, "bot_id": global.active.id }, function(response) {
					console.log(response);
				});
			}
		}

		$scope.enableCron = function(enable, cron_id) {
			util.updateCron(cron_id, {"enable": ( enable ) ? 1 : 0 }, function(response) {
				console.log(response);
			});
		}

		// Switch main tab panes
		$scope.switchTab = function(tab) {
			var id = tab+"-tab";
			$(".main-tab .tab-pane").each(function(i, el) {
				if( $(el).attr("id") == id )
					$(el).show();
				else
					$(el).hide();
			});
		}

		$scope.sendMessage = function() {
			console.log("[sendMessage]", global.active);
			// Check if is selected any chat
			var message = $("#input-message").val(),
				chat_ids = $("#chats input[type=checkbox]:checked").map(function(){
					return this.name; }).get(),
				callback = function(response) {
					if( response != null && response.ok ) {
						if( response.saved )
							util.request("get_messages", { "bot_id": global.active.id }, function(response) {
								$scope.updateList("messages", response);
							});
						$("#input-message").val("");
						$("#submit-message").html("Message sent");
						setTimeout(function() { $("#submit-message").html("Send message") }, 2000);
					}
				};

			console.log(message, chat_ids);

			if( !chat_ids.length > 0 )
				$("#all-chats").parent("label").addClass("error");

			if( !message.length > 0 )
				$("#input-message").parent(".form-group").addClass("error");

			if( chat_ids.length > 0 && message.length > 0 )
				if( global.user != null && global.active != null )
					util.request("send_message", {
						"text": message,
						"chats_id": chat_ids,
						"bot_id": global.active.id,
						"tz": new Date().getTimezoneOffset() / 60
					}, callback);
		}

		// Message textarea change handler (main content)
		$scope.updateMessage = function(msg) {
			if( $("#input-message").parent(".form-group").hasClass("error") && msg.length > 0 )
				$("#input-message").parent(".form-group").removeClass("error");
		}

		$scope.selectAllMessage = function(check) {
			$("#all-chats").parent("label").removeClass("error");
			if( $("#all-chats").prop("checked") )
				$("#chats input[type=checkbox]").prop("checked", true);
			else
				$("#chats input[type=checkbox]").prop("checked", false);
		}

		$scope.modalForm = function(mode, argument) {
			switch(mode) {
				case "cron":
					switch( argument ) {
						case 'new':
							$scope.cronId = 0;
							$("#delete-cron").hide();
							break;
						default:
							console.log("[cron]", argument);
							$scope.cronId = argument;
							$("#delete-cron").show();
							$("#save-cron").html("Update").addClass("btn-success");
							$("#cron-modal").modal();
					}
					break;
				case "bot":
					console.log("[bot]", argument);
					break;
				case "channel":
					console.log("[bot]", argument);
					break;
				case "files":
					util.request("list_files", {
						"user_id": argument
					}, function(list) {
						global.files = list.files;
						$scope.folders = list.folders;
						$scope.activeFolder = (typeof $scope.activeFolder === "undefined") ? list.folders[0] : $scope.activeFolder;
						$scope.files = ( global.files[$scope.activeFolder].length > 0 ) ? global.files[$scope.activeFolder] : [{}];
						$scope.file_item = ( global.files[$scope.activeFolder].length > 0 ) ? global.tmp.files_list : global.tmp.empty;
					});
					break;
			}
		}

		$scope.selectFolder = function(folder) {
			$scope.activeFolder = folder;
			$scope.file_item = ( global.files[folder].length > 0 ) ? global.tmp.files_list : global.tmp.empty;
			$scope.files = ( global.files[folder].length > 0 ) ? global.files[folder] : [{}];
		}

		$scope.selectPhoto = function(folder, file) {
			console.log("[selectPhoto]", folder, file);
		}

		$scope.saveCron = function(id, date) {
			var message = $("#cron-input-message").val(),
				chat_ids = $("#modal-chats input[type=checkbox]:checked").map(function(){
					return this.name; }).get(),
				validateForm = function() {
					if( !message.length > 0 )
						$("#cron-input-message").parent(".form-group").addClass("error");
					else
						$("#cron-input-message").parent(".form-group").removeClass("error");

					if( !chat_ids.length > 0 )
						$("#cron-all-chats").parent("label").addClass("error");
					else
						$("#cron-all-chats").parent("label").removeClass("error");
				},
				cron_action = ( id == "0" ) ? "save_cron" : "update_cron";

			if( typeof date != "undefined") {
				var time = date.split(" ")[0],
					dt = date.split(" ")[1].split("/"),
					tz = 0,
					repeat = $("input[name=repeat]:checked").val();

				$(".datepicker").parent(".form-group").removeClass("error");
				validateForm();

				date = util.getUnixDate(util.strf("{0} {1}/{2}/{3}", [time, dt[1], dt[0], dt[2]]));
				tz = new Date(date).getTimezoneOffset() / 60;
				date = (date/1000).toFixed(0);

				if( message.length > 0 && chat_ids.length > 0 ) {
					console.log("[saveCron] id:", id, date, message, chat_ids, tz);
					var attributes = {
						bot_id: global.active.id,
						cron_id: id },
						parameters = {
							text: message,
							chats_id: chat_ids.join(),
							date: date,
							tz_offset: tz,
							repeat: repeat,
							cron: "null"
						};

					if( cron_action == "save_cron" )
						$.extend(attributes, parameters);
					else {
						parameters.enable = 1;
						attributes.values = JSON.stringify(parameters);
					}

					util.request( cron_action, attributes, function(response) {
						switch(cron_action) {
							case "save_cron":
								if( response.ok ) {
									$scope.cronId = response.cron[0]['id'];
									$scope.updateList("crons", response.cron);
									$("#save-cron").html("Cron saved");
									setTimeout(function() { $("#save-cron").html("Update").addClass("btn-success") }, 2000);
									$("#delete-cron").show();
								}
								break;
							case "update_cron":
								console.log(response);
								break;
						}
					});
				}
			} else {
				$(".datepicker").parent(".form-group").addClass("error");
				validateForm();
			}
		}

		$scope.deleteCron = function(id) {
			if( global.user != null && global.active != null )
				if( window.confirm("Confirm cron delete?") )
					util.request("delete_cron", {'bot_id': global.active.id, 'cron_id': id}, function(response) {
						if( response.ok ) {
							$scope.updateList("crons", response.cron);
							$("#cron-modal").modal('hide');
						}
					});
		}

		//console.log($cookies.getObject("user"));

		// Check user cookie
		if( typeof $cookies.getObject("user") != "undefined" ) {
			global.user = $cookies.getObject("user");
			global.active = global.user.active;

			console.log(global.user);
			
			$scope.userName = global.user.user.name;
			$scope.userId = global.user.user.id;
			$scope.activeBotName = ( global.active != null ) ? global.active.username : "Add new bot";
			$scope.bots = global.user.bots;

			util.switchView("main");

			$scope.getUpdates();
		} else
			util.switchView("enter");
	}
]);
