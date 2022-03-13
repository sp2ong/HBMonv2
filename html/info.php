<?php
$progname = basename($_SERVER['SCRIPT_FILENAME'],".php");
include_once 'include/config.php';
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" lang="en">
<head>
<meta charset="UTF-8">
<title>DMR Server monitor - Info</title>
<script type="text/javascript" src="scripts/hbmon.js"></script>
<link rel="stylesheet" type="text/css" href="css/styles.php" />
<meta name="description" content="Copyright &copy; 2016-2022.The Regents of the K0USY Group. All rights reserved. Version SP2ONG 2019-2022" />
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
<!-- TG table -->
<div style="width: 1100px; margin-left:0px;">
<fieldset style="box-shadow:0 0 10px #999;background-color:#e0e0e0e0; width:1050px;margin-left:15px;margin-right:15px;font-size:14px;border-top-left-radius: 10px; border-top-right-radius: 10px;border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;">
<legend><b><font color="#000">&nbsp;.: Talk Groups :.&nbsp;</font></b></legend>
<table style="margin-top:5px; table-layout:fixed; font: 10pt arial, sans-serif;background-color: #f9f9f9f9;">
    <tr class="theme_color" style=" height: 32px;font: 10pt arial, sans-serif;border:0;">
        <th style='width: 150px;'>TG#</th>
        <th style='width: 80px;'>TS 1</th>
        <th style='width: 80px;'>TS 2</th>
        <th style='width: 790px;'>Description</th>
    </tr>
   <tr>
        <td>&nbsp;<b>TG 5</b>&nbsp;</td>
        <td>&nbsp;<b></b>&nbsp;</td>
    <td>&nbsp;<b>D | S</b>&nbsp;</td>
    <td>Talk group XLX132-D D-Star/DMR/C4FM.</td>
    </tr>
     <tr>
        <td>&nbsp;<b>TG 9999</b>&nbsp;</td>
    <td>&nbsp;<b></b>&nbsp;</td>
    <td>&nbsp;<b>D | S</b>&nbsp;</td>
        <td>Echo (Parrot).</td>
    </tr>
</table>
<br>
<span style="text-align: center;">Hotspot: D - duplex | S - simplex</span>
</fieldset></div><br>

<p style="text-align: center;"><span style="text-align: center;">
Copyright &copy; 2016-2022<br>The Regents of the <a href=http://k0usy.mystrikingly.com/>K0USY Group</a>. All rights reserved.<br><a href=https://github.com/sp2ong/HBMonv2>Version SP2ONG 2019-2022</a><br><br></span>
    <!-- THIS COPYRIGHT NOTICE MUST BE DISPLAYED AS A CONDITION OF THE LICENCE GRANT FOR THIS SOFTWARE. ALL DERIVATEIVES WORKS MUST CARRY THIS NOTICE -->
    <!-- This is version of HBMonitor SP2ONG 2019-2022 -->
</p>
</center>
</body>
</html>
