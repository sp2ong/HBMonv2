<?php
$progname = basename($_SERVER['SCRIPT_FILENAME'],".php");
include_once 'include/config.php';
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="30">
<title>DMR Server monitor - STATUS</title>
<script type="text/javascript" src="scripts/hbmon.js"></script>
<link rel="stylesheet" type="text/css" href="css/styles.php" />
<meta name="description" content="Copyright &copy; 2016-2022.The Regents of the K0USY Group. All rights reserved. Version SP2ONG 2019-2022" />
</head>
<body style="background-color: #d0d0d0;font: 10pt arial, sans-serif;">
<center><div style="width:1100px; text-align: center; margin-top:5px;">
<img src="img/logo.png?random=323527528432525.24234" alt="" />
</div>
<div style="width: 1150px;">
<p style="text-align:center;"><span style="color:#000;font-size: 18px; font-weight:bold;"><?php echo REPORT_NAME;?></span></p>
<p></p>
</div>
<?php include_once 'buttons.html'; ?>
<div style="width: 1100px;">
<p align="middle">
<div style="overflow-x:auto;">
<center><fieldset style="background-color:#e0e0e0e0;margin-left:15px;margin-right:15px;margin-top:15px;font-size:14px;border-top-left-radius: 10px; border-top-right-radius: 10px;border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;">
<table style="border-collapse: collapse; border: 1px solid #C1DAD7; width: 100%;background-color:#f0f0f0;">
    <thead><tr><th colspan=9 style="height: 30px;font-size:18px;font-weight:bold;">LastHeard</th></tr></thead>
<tr class="theme_color" style="height:35px; text-align: center;font-weight:bold;"><TH>&nbsp;&nbsp;Date<TH>&nbsp;Time<TH>&nbsp;Callsign (DMR-Id)<TH>&nbsp;&nbsp;Name<TH>&nbsp;TG#<TH>&nbsp;&nbsp;TG Name<TH>TX (s)&nbsp;<TH>Source
</tr>

<?php
// logging extension "last heard list" for hbmonitor
// developed by Heiko Amft,DL1BZ dl1bz@bzsax.de

// define array for CSV import of logfile
$log_time=array();
$transmit_timer=array();
$calltype=array();
$event=array();
$system=array();
$src_id=array();
$src_name=array();
$ts=array();
$tg=array();
$tgname=array();
$user_id=array();
$user_call=array();
$user_name=array();

// define location and name of logfile
// best practise is write logfile in the directory where this php script is saved because some php installations have problems to read files outside the webserver directories
$handle = fopen("/opt/HBMonv2/log/lastheard.log","r");

// import to array
while (($data = fgetcsv ($handle)) !==false)
{
    $log_time[] = $data[0];
    $transmit_timer[] = $data[1];
    $calltype[] = $data[2];
    $event[] = $data[3];
    $system[] = $data[4];
    $src_id[] = $data[5];
    $src_name[] = $data[6];
    $ts[] = $data[7];
    $tg[] = $data[8];
    $tgname[] = $data[9];
    $user_id[] = $data[10];
    $user_call[] = $data[11];
    $user_name[] = $data[12];
}

// define some macros for table output
$s = "<TD class=\"log\">";
$s_r = "<TD align=\"right\">";
$s_m = "<TD align=\"center\">";

// output to html table from the newest entry to the oldest
for ($i=count($log_time)-1; $i >= 0; $i--)

{
// prepare date string for output in european format
$split_date = substr($log_time[$i],0,10);
$date_eu = explode("-", $split_date);

$ts[$i] = substr($ts[$i],-1);
$tg[$i] = substr($tg[$i],2);

// define special character convert for number zero - we write calls with number zero with this character in logs in Germany
$src_name[$i] = str_replace("0","&Oslash;",$src_name[$i]);
if (substr($user_call[$i],2,1)=="0") { $user_call[$i] = str_replace("0","&Oslash;",$user_call[$i]); }

$log_time[$i]=substr($log_time[$i],0,19);

// thats a special thing for an Id comes without DMR-Id from PEGASUS project - it means we need to convert to "NoCall" thats for calls from source ECHOLINK
if ($user_id[$i]=="1234567") {$user_call[$i] = "*NoCallsign*"; $user_id[$i]="-";}

// output table
echo "<TR class=\"log\" style=\"height:25px; text-align: center;\">".$s.'&nbsp;'.$date_eu[2].".".$date_eu[1].".".$date_eu[0].$s.'&nbsp;'.substr($log_time[$i],11,5).$s.'<font color=#0066ff><b>&nbsp;'.$user_call[$i]."</b></font><font size=\"-1\"> (".$user_id[$i].")</font>".$s.'<font color=#002d62><b>'.TRIM($user_name[$i]).'</b></font>'.$s.'<font color=#b5651d><b>'.$tg[$i].'</b></font>'.$s.'<font color=green><b>&nbsp;'.$tgname[$i].'</b></font>'.$s."<center>".round($transmit_timer[$i])."</center>".$s.$system[$i]."</TR>\n";
}

echo "\n</table></fieldset></div>";

// close logfile after parsing
fclose ($handle);
?>
<div style="width: 1100px;">
<p style="text-align: center;"><span style="text-align: center;">
Copyright &copy; 2016-2022<br>The Regents of the <a target="_blank" href=http://k0usy.mystrikingly.com/>K0USY Group</a>. All rights reserved.<br><a title="HBMonv2 SP2ONG" target="_blank" href=https://github.com/sp2ong/HBMonv2>Version SP2ONG 2019-2022</a><br></span>
    <!-- THIS COPYRIGHT NOTICE MUST BE DISPLAYED AS A CONDITION OF THE LICENCE GRANT FOR THIS SOFTWARE. ALL DERIVATEIVES WORKS MUST CARRY THIS NOTICE -->
    <!-- This is version of HBMonitor v2 SP2ONG 2019-2022 -->
<font size="-2">&copy; developed by DL1BZ as logging-extension of HBmonitor (2018,2019)</font><br>
</p>
</div>
</center>
</body>
</html>
