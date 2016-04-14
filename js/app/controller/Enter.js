app.controller("Enter", function($scope, $cookies, md5, global, util) {
	global.enter = $scope;

	// Enter the system from Sign/Login modal form
	$scope.enter = function() {
		switch( global.enter ) {
			case "login":
				$scope.submitLogin();
				break;
			case "sign":
				$scope.submitSign();
				break;
		}

		return false;
	}

	// Submit Sign in form
	$scope.submitSign = function() {
		var $inputs = $("#sign-in-form :input"),
			empty = false;

		var values = {};
		$inputs.each(function() {
			values[this.name] = $(this).val();
			if( !($(this).val().length > 0) ) {
				empty = true;
				$(this).parent('.form-group').addClass("has-error"); }

			// Validate inputs
			switch(this.name) {
				case 'name':
					if( $(this).val().length < 5 )
						$(this).prev('.control-label').html("Wow, so short name..");
					break;
				case 'email':
					var re_email = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
					if( !re_email.test($(this).val()) )
						$(this).prev('.control-label').html("You can receive letters with this?..");
					break;
				case 'hash':
					if( $(this).val().length < 7 )
						$(this).prev('.control-label').html("qwerty");
					else
						values[this.name] = md5.createHash($(this).val());
					break;
			}
		});

		if( empty ) return false;

		util.request("sign_in", values, function(response) {
			if( response.sign_in.ok )
				log_in_success(response.sign_in.log_in);
			else
			if( response.sign_in.status == 'exists' ) {
				$('#sign-in-email').parent('.form-group').addClass("has-error");
				$('#sign-in-email').prev('.control-label').html("This address is already used");
			}
		});
	}

	// Submit Login form
	$scope.submitLogin = function() {
		var $inputs = $("#log-in-form :input"),
			empty = false;

	    var values = {};
	    $inputs.each(function() {
	        values[this.name] = $(this).val();
	        if( !($(this).val().length > 0) ) {
	        	empty = true;
	        	$(this).parent('.form-group').addClass("has-error"); }

	        switch(this.name) {
	        	case 'hash':
	        		values[this.name] = md5.createHash($(this).val());
	        		break;
	        }
	    });

	    if( empty ) return false;

		util.request("log_in", values, function(response) {
	    	if( response.ok && response.user.length > 0 )
				$scope.logInSuccess(response);
	    	else {
	    		if( response.log_in.hasOwnProperty('hash') && !response.log_in.hash ) {
	    			$('#log-in-password').parent('.form-group').addClass("has-error");
	    			$('#log-in-password').prev('.control-label').html("Your password is not so correct"); }
	    		if( response.log_in.hasOwnProperty('email') && !response.log_in.email ) {
	    			$('#log-in-email').parent('.form-group').addClass("has-error");
	    			$('#log-in-email').prev('.control-label').html("Wow, I don't know who You are!"); }
	    	}
	    });

		return false;
	}

	$scope.logInSuccess = function(success) {
		$cookies.putObject("user", { "user": success.user[0], "bots": success.bots, "active": ( success.bots.length > 0 ) ? success.bots[0] : null });

		global.user = $cookies.getObject("user");
		global.active = ( success.bots.length > 0 ) ? success.bots[0] : null;
		global.bots = success.bots;

		$("#sign-modal").modal("hide");
		
		util.switchView("main");
		global.main.userName = success.user[0].name;
		global.main.activeBotName = ( success.bots.length > 0 ) ?  success.bots[0].username : "Add new bot";
		global.main.bots = success.bots;
		global.main.getUpdates();
	}
});
