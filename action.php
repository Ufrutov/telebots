<?php
	// Arguments:
	// URL: host.com?command=action&command=action
	
	header('Content-Type: text/javascript; charset=UTF-8');

	$arguments = [];
	$method = ["action", "text", "chats_id", "cron_id", "date", "repeat", "name", "email", "hash", "token", "user_id", "id", "bot_id", "tz", "tz_offset", "values", "channel", "cron"];
	if( count($_REQUEST) > 0 ) {
		foreach ($_REQUEST as $key => $value) {
			if( strlen($value) > 0 && in_array($key, $method) ) {
				switch ($key) {
					case 'action':
						$arguments[$key] = $value;
						switch ($value) {
							case 'thumb':
								// Create thumb for image (action=thumb)
								// file - image path
								// width, height - image dimensions (opt)
								$img = ( array_search('file', array_keys($_REQUEST)) === FALSE ) ? 'ng/img/empty.png' : $_REQUEST['file'];
								$height = ( array_search('height', array_keys($_REQUEST)) === FALSE ) ? 120 : $_REQUEST['height'];
								$width = ( array_search('width', array_keys($_REQUEST)) === FALSE ) ? 120 : $_REQUEST['width'];
								$ext = pathinfo($img)['extension'];

								$x = 0;
								$y = 0;

								list($w, $h) = getimagesize($img);

								if( $w > $h )
									$x = ceil(( $w - $h ) / 2);
								if( $h > $w )
									$y = ceil(( $h - $w ) / 2);

								$thumb = imagecreatetruecolor($width, $height);
								$source = imagecreatefromjpeg($img);
								
								imagecopyresized($thumb, $source, 0, 0, $x, $y, $width, $height, ( $w > $h ) ? $h : $w, ( $w > $h ) ? $h : $w);

								switch ($ext) {
									case 'png':
										header('Content-Type: image/png');
										imagepng($thumb);
										break;
									case 'jpg':
										header('Content-Type: image/jpeg');
										imagejpeg($thumb);
										break;
								}

								exit();
								break;
						}
						break;					
					default:
						$arguments[$key] = $value;
						break;
				}
			}
		}
	} else {
		exit('No attrs..');
	}
	$attr = json_encode($arguments);

	$python = `python index.py '$attr' 2>&1`;
	print_r($python);
?>