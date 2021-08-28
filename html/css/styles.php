<?php
include_once '../include/config.php';
// Output CSS and not plain text
header("Content-type: text/css");
?>
.link <?php echo "{".THEME_COLOR."}\n"; ?>
.button <?php echo "{".THEME_COLOR."}\n"; ?>
.dropbtn <?php echo "{".THEME_COLOR."}\n"; ?>

#lact {
 height:<?php echo HEIGHT_ACTIVITY; ?>;
 width: 100%;
 border-collapse: collapse;
 border:none;
}
#rcorner {
  display: flex;
  align-items: center;
  justify-content: center;
  vertical-align: middle;
  text-align:center;
  justify-content: center;
  align-items: center;
  border-radius: 10px;
  -moz-border-radius:10px;
  -webkit-border-radius:10px;
  border: 1px solid LightGrey;
  background: #e9e9e9;
  font: 12pt arial, sans-serif; 
  font-weight:bold;
  margin-top:2px;
  margin-right:0px;
  margin-left:0px;
  margin-bottom:0px;
  color:#002d62;
  white-space:normal;
  height: 100%;
  line-height:21px;
}
#rcornerh {
  display: flex;
  display: -webkit-flex;
  justify-content: center;
  align-items: center;
  border-radius:8px;
  -moz-border-radius:8px;
  -webkit-border-radius:8px;
  font: 9pt arial, sans-serif; 
  font-weight:bold;
  color:white;
  height:25px;
  line-height:25px;
  <?php echo THEME_COLOR."\n"; ?>
}

table, td, th {
  border: .5px solid #d0d0d0; 
  padding: 2px; 
  border-collapse: collapse;
  border-spacing: 0;
  text-align:center;}
tr.theme_color <?php echo "{".THEME_COLOR."}\n"; ?>
th.theme_color <?php echo "{".THEME_COLOR."}\n"; ?>

html {
    overflow: -moz-scrollbars-vertical; 
    overflow-y: scroll;
}


table.log {background-color: #f0f0f0; border-collapse: collapse; border: 1px solid #C1DAD7; width: 100%;}
th.log {height: 30px; text-align: center;}
tr:nth-child(even).log {background-color: #fafafa;text-align: center;}
td.log {font-family: Monospace; height: 20px;}


a:link {
  color: #0066ff;
  text-decoration: none;
}

/* visited link */
a:visited {
  color: #0066ff;
  text-decoration: none;
}

/* mouse over link */
a:hover {
  color: hotpink;
  text-decoration: underline;
}
/* selected link */
a:active {
  color: #0066ff;
  text-decoration: none;
}
.tooltip {
  position: relative;
  opacity: 1;
  display: inline-block;
  border-bottom: 1px dotted black;
}

.tooltip .tooltiptext {
  visibility: hidden;
  width: 280px;
  background-color: #6E6E6E;
  box-shadow: 4px 4px 6px #3b3b3b;
  color: #FFFFFF;
  text-align: left;
  border-radius: 6px;
  padding: 8px 0;
  left: 100%;
  opacity: 1;
  /* Position the tooltip */
  position: absolute;
  z-index: 1;
}

.tooltip:hover .tooltiptext {
  right: 100%;
  opacity: 1;
  visibility: visible;
}
.button {
  border: none;
  padding: 8px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 14px;
  font-weight: 500;
  margin: 4px 2px;
  border-radius: 8px;
  box-shadow: 0px 8px 10px rgba(0,0,0,0.1);
}

.link:hover {background-color:rgb(140,140,140);background: rgb(140,140,140); color:white;}  
.dropdown:hover .dropbtn {background-color:rgb(140,140,140);background: rgb(140,140,140); color:white;} 

.dropbtn {
  border: none;
  padding: 8px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 14px;
  font-weight: 500;
  margin: 4px 2px;
  border-radius: 8px;
  box-shadow: 0px 8px 10px rgba(0,0,0,0.1);
}

/* The container <div> - needed to position the dropdown content */
.dropdown {
  position: relative;
  display: inline-block;
}

/* Dropdown Content (Hidden by Default) */
.dropdown-content {
  display: none;
  position: absolute;
  background-color: #f1f1f1;
  min-width: 140px;
  box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
  z-index: 1000;
}

/* Links inside the dropdown */
.dropdown-content a {
  color: black;
  padding: 6px 16px;
  text-decoration: none;
  display: block;
}

/* Change color of dropdown links on hover */
.dropdown-content a:hover {background-color: #ddd;}

/* Show the dropdown menu on hover */
.dropdown:hover .dropdown-content {display: block;}

