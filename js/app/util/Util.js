app.factory("util", function($http, $cookies, $filter, global) {
	var util = {};

	// Reqeust to server
	util.request = function(action, parameters, success, fail) {

		var arguments = {
			url: global.url+"/action.php",
			method: "GET",
			params: angular.extend({ action: action }, parameters)
		};

		console.log("[request]", action, parameters);

		$http(arguments).then(function(response) {
			if( !response.data.hasOwnProperty(action) )
				console.warn("[E] Request ", action, "failed: ", parameters, " response:", response.data);
			else
				if( angular.isFunction(success) ) {
					success(response.data[action]);
					console.log(response.data[action]);
				}
		}, function(response) {
			if( angular.isFunction(fail) )
				fail();
		});
	}

	util.switchView = function(view) {
		switch(view) {
			case "main":
				// Load empty templates before first update
				global.main.chats = [{}];
				global.main.url = global.url;

				global.main.view = "js/templates/main/index.html";
				global.main.actions = "js/templates/main/navigation/actions.html";
				global.main.modal = "js/templates/main/modal/modal.html";
				global.main.bot_item = "js/templates/main/navigation/bot.html";
				global.main.chat_list = "js/templates/main/util/loading.html";
				global.main.folder_item = "js/templates/main/navigation/folder.html";
				break;
			case "enter":
				global.main.view = "js/templates/about/index.html";
				global.main.actions = "js/templates/about/navigation/actions.html";
				global.main.modal = "js/templates/about/modal/sign-in.html";
				break;
		}
	}

	util.formatDate = function(time) {
		return $filter('date')(time, 'HH:mm dd/MM/yy');
	}

	util.getUnixDate = function(time, format) {
		return Date.parse(time);
	}

	util.updateCron = function(id, values, callback) {
		if( global.user != null && global.active != null )
			util.request("update_cron", { "bot_id": global.active.id, "cron_id": id, "values": JSON.stringify(values) }, function(response) {
				if( response.ok )
					if( angular.isFunction(callback) )
						callback(response.cron);
				else
					console.warn("[E] Cron update failed: cron_id:", idm, " values:", values);
			});
	}

	util.strf = function(format, args) {
		return format.replace(/{(\d+)}/g, function(match, number) {
			return typeof args[number] != 'undefined' ? args[number] : match;
		});
	}

	return util;
});
