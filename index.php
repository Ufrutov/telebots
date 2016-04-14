<!doctype html>
<html>
   
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
		<title>TeleBots</title>

		<!-- JavaScript resources -->
		<script src = "js/lib/ng/angular.min.js"></script>
		<script src = "js/lib/ng/angular-cookies.min.js"></script>
		<script src = "js/lib/ng/angular-md5.min.js"></script>
		<script src = "js/lib/ng/angularjs-datetime-picker.js"></script>
		<script src = "js/lib/jquery/jquery-1.10.2.js"></script>
		<script src = "js/lib/bootstrap/bootstrap.min.js"></script>

		<!-- Uncompressed JavaScript resources -->
		<script src = "js/index.js"></script>
		<script src = "js/app/util/Global.js"></script>
		<script src = "js/app/util/Util.js"></script>
		<script src = "js/app/controller/Main.js"></script>
		<script src = "js/app/controller/Enter.js"></script>

		<!-- CSS resources -->
		<link rel="stylesheet" href="css/bootstrap.min.css">
		<link rel="stylesheet" href="css/angularjs-datetime-picker.css">
		<link rel="stylesheet" href="css/style.css">

	</head>

	<body ng-app="bot" ng-controller="Main">
		<header>
			<nav class="navbar navbar-default">
				<div class="container">
			    	<!-- Brand and toggle get grouped for better mobile display -->
			    	<div class="navbar-header">
			    		<a href="#" class="navbar-brand-logo" id="logo" ng-click="getUpdates()" title="@TeleBots"></a>
				    	<!-- <a href="#">Get updates</a> -->
			    		<div class="navbar-actions" id="navbar-buttons">
						<div ng-include="actions"></div>
					</div>
			    	</div>
				</div>
			</nav>
		</header>
		<div class="container body">
			<div class="row" id="content">
				<div ng-include="view"></div>
			</div>
		</div>
		
		<div ng-include="modal"></div>
	</body>
</html>