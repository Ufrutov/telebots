app.factory("global", function($location) {

	var g = {};

	g.url = $location.absUrl();

	g.enter = "sign";
	g.user = null;

	g.chats = [];
	g.bots = [];
	g.files = null;

	g.active = null;
	g.activeBot = null;
	g.activeBotName = null;

	// Controllers
	g.main = null; // Main controller
	g.enter = null; // Enter controller

	// Templates
	var tmp = {
		loading: "js/templates/main/util/loading.html",
		empty: "js/templates/main/util/empty.html",
		chat_list: "js/templates/main/list/chat.html",
		updates_list: "js/templates/main/list/update.html",
		messages_list: "js/templates/main/list/message.html",
		crons_list: "js/templates/main/list/cron.html",
		files_list: "js/templates/main/list/file.html"
	}

	g.tmp = tmp;

	return g;
});
