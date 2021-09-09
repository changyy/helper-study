<?php

if ($argc < 3) {
	echo "Usage> php ".$argv[0]." RunningLog SetLockTimeout MaxQueryCount\n\n";
	echo "\t$ php ".$argv[0]." /tmp/db_helper.log 5 10\n";
	echo "\t$ echo '{}' | php ".$argv[0]." /tmp/db_helper.log 5 10\n";
	echo "\n";
	exit;
}

function out_exit($data, $return_code = 1) {
	echo json_encode($data)."\n";
	exit ($return_code);
}

function get_running_id($running_log_path, $max_running_number = 10, $lock_timeout = 5) {
	global $argv;

	$max_running_number = intval($max_running_number);
	if ($max_running_number < 0)
		$max_running_number = 5;
	$lock_timeout = intval($lock_timeout);
	if ($lock_timeout < 0)
		$lock_timeout = 5;

	$start_time = microtime(true);
	$block = 0;
	$lock_file_path = '/tmp/lock_'.basename($argv[0]); //$argv[1];

	$lock_file = NULL;
	$lock_timeout = $lock_timeout > 0 ? $lock_timeout : 5;
	$lock_file = fopen($lock_file_path, "a+");
	$get_lock = false;
	while( (microtime(true) - $start_time) < $lock_timeout ) {
		if (!flock($lock_file,LOCK_EX, $block)) {
			usleep(100);
		} else {
			$get_lock = true;
			break;
		}
	}

	if (!$get_lock) {
		if ($lock_file)
			fclose($lock_file);
		return false;
	}

	$current_max_id = intval(@file_get_contents($running_log_path));
	if ($current_max_id < $max_running_number) {
		$current_max_id++;
		file_put_contents($running_log_path, sprintf("%d\n", $current_max_id));
		flock($lock_file, LOCK_UN);
		fclose($lock_file);
		return $current_max_id;
	}

	flock($lock_file, LOCK_UN);
	fclose($lock_file);
	return false;
}

function release_running_id($running_log_path) {
	global $argv;
	$block = 1;
	$lock_file_path = '/tmp/lock_'.basename($argv[0]); //$argv[1];

	$lock_file = NULL;
	$lock_file = fopen($lock_file_path, "a+");
	if (flock($lock_file,LOCK_EX, $block)) {
		$current_max_id = intval(@file_get_contents($running_log_path));
		--$current_max_id;
		if ($current_max_id < 0)
			$current_max_id = 0;
		file_put_contents($running_log_path, sprintf("%d\n", $current_max_id));
	}
	flock($lock_file, LOCK_UN);
	fclose($lock_file);
}

$output = array( 'status' => false, 'log' => array() );
$running_id = get_running_id($argv[1], $argv[2], $argv[3]);
if ($running_id === false) {
	$output['error'] = 1;
	$output['message'] = 'lock failed or timeout';
	out_exit($output);
}

// Step 1: read input
$input = @json_decode(file_get_contents("php://stdin"), true);

// Step 2: check db info
if (!isset($input['db_host']) || !isset($input['db_user']) || !isset($input['db_pass']) || !isset($input['db_database']) ) {
	$output['error'] = -1;
	$output['message'] = 'no db info: db_host('.(isset($input['db_host']) ? $input['db_host'] : '').'), db_user('.(isset($input['db_user']) ? $input['db_user'] : '').'), db_pass('.(isset($input['db_pass']) ? '***' : '').'), db_database('.(isset($input['db_database']) ? $input['db_database'] : '').')';
	release_running_id($argv[1]);
	out_exit($output);
}
// Step 3: check db query
if (!isset($input['db_query']) || empty($input['db_query'])) {
	$output['error'] = -2;
	$output['message'] = 'no db_query info';
	release_running_id($argv[1]);
	out_exit($output);
}

$time_begin = microtime(true);

// Step 4: db connect
$link = mysql_connect( $input['db_host'], $input['db_user'], $input['db_pass']);
if (!$link) {
	$output['error'] = 2;
	$output['message'] = 'Could not connect: '.mysql_error();
	release_running_id($argv[1]);
	out_exit($output);
}

array_push($output['log'], microtime(true) - $time_begin);

$time_begin = microtime(true);
// Step 5: select database
$db_selected = mysql_select_db($input['db_database'], $link);
if (!$db_selected) {
	$output['error'] = 3;
	$output['message'] = 'USE database error: '.mysql_error();
	release_running_id($argv[1]);
	out_exit($output);
}

array_push($output['log'], microtime(true) - $time_begin);

// Step 6: do db query
if (!is_array($input['db_query'])) {
	$input['db_query'] = array( $input['db_query'] );
}
//array_unshift($input['db_query'], "set names 'utf8'");

$output['input'] = array();
foreach($input['db_query'] as $sub_query) {
	$time_begin = microtime(true);
	$result = mysql_query($sub_query, $link);
	array_push($output['log'], microtime(true) - $time_begin);
	if ($result === false) {
		$output['error'] = 4;
		$output['message'] = 'db query failed: '.mysql_error();
		$output['db_query_failed'] = $sub_query;
		mysql_close($link);
		release_running_id($argv[1]);
		out_exit($output);
	}
	$sub_output = array();
	if (mysql_num_rows($result) != 0) {
		while (($row = mysql_fetch_assoc($result)) != false) {
			array_push($sub_output, $row);
		}
		mysql_free_result($result);
	}
	array_push($output['input'], $sub_output);
}
$output['status'] = true;
mysql_close($link);
release_running_id($argv[1]);
out_exit($output, 0);
?>
