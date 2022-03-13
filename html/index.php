<?php
$progname = basename($_SERVER['SCRIPT_FILENAME'],".php");
include_once 'include/config.php';
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" lang="en">
<head>
<meta charset="UTF-8">
<title>DMR Server monitor - STATUS</title>
<script type="text/javascript" src="scripts/hbmon.js"></script>
<link rel="stylesheet" type="text/css" href="css/styles.php" />
<meta name="description" content="Copyright &copy; 2016-2022.The Regents of the K0USY Group. All rights reserved. Version SP2ONG 2019-2022 (v20211012)" />
</head>
<body style="background-color: #d0d0d0;font: 10pt arial, sans-serif;">
<center><div style="width:1100px; text-align: center; margin-top:5px;">
<img src="img/logo.png?random=323527528432525.24234" alt="" />
</div>
<div style="width: 1100px;">
<p style="text-align:center;"><span style="color:#000;font-size: 18px; font-weight:bold;"><?php echo REPORT_NAME;?></span></p>
<p></p>
</div>
<?php include_once 'buttons.html'; ?>
<div style="width: 1100px;">
<noscript>You must enable JavaScript</noscript>
    <p id="main"></p>
</div>
<!-- LOG monitor if you want on main page -->
<!--
<div style="width: 1100px; margin-left:0px;">
<fieldset style="width: 1045px; margin-left:0px;margin-right:0px;font-size:14px;border-top-left-radius: 10px; border-top-right-radius: 10px;border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;">
	<legend><b><font color="#000">&nbsp;.: Call log window :.&nbsp;</font></b></legend>
        <pre id="log" style="height: 20em; text-align: left; overflow-y: scroll; font-size:13px; background-color: #000000; color:#b1eee9;"></pre>
</fieldset></div>
-->
<div style="width: 1100px;">
<p style="text-align: center;"><span style="text-align: center;">
Copyright &copy; 2016-2022<br>The Regents of the <a target="_blank" href=http://k0usy.mystrikingly.com/>K0USY Group</a>. All rights reserved.<br><a title="HBMonv2 SP2ONG v20220312" target="_blank" href=https://github.com/sp2ong/HBMonv2>Version SP2ONG 2019-2022</a><br><br></span>
    <!-- THIS COPYRIGHT NOTICE MUST BE DISPLAYED AS A CONDITION OF THE LICENCE GRANT FOR THIS SOFTWARE. ALL DERIVATEIVES WORKS MUST CARRY THIS NOTICE -->
    <!-- This is version of HBMonitor SP2ONG 2019-2022 -->
</p>
</div>
</center>
</body>
</html>
