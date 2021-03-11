REPORT_NAME     = 'Dashboard of local DMR network'           # Name of the monitored HBlink system
#
CONFIG_INC      = True                           # Include HBlink stats
HOMEBREW_INC    = True                           # Display Homebrew Peers status
LASTHEARD_INC   = True                           # Display lastheard table on main page
BRIDGES_INC     = False                          # Display Bridge status and button
EMPTY_MASTERS   = False                          # Display Enable (True) or DISABLE (False) empty masters in status
#
HBLINK_IP       = '127.0.0.1'                    # HBlink's IP Address
HBLINK_PORT     = 4321                           # HBlink's TCP reporting socket
FREQUENCY       = 10                             # Frequency to push updates to web clients
WEB_SERVER_PORT = 8080                           # Has to be above 1024 if you're not running as root
CLIENT_TIMEOUT  = 0                              # Clients are timed out after this many seconds, 0 to disable

# Theme colors
#
# Green 
#THEME_COLOR     = 'background-color:#4a8f3c;color:white;'

# Blue
#THEME_COLOR     = 'background-color:#2A659A;color:white;'

# Blue Gradient 1
THEME_COLOR     = 'background-image: linear-gradient(to bottom, #337ab7 0%, #265a88 100%);color:white;'

# Blue Gradient 2
#THEME_COLOR     = 'background-image: linear-gradient(to bottom, #3333cc 0%, #265a88 100%);color:white;'

# Red Gradient
#THEME_COLOR     = 'background-image:linear-gradient(0deg, rgba(251,0,0,1) 0%, rgba(255,131,131,1) 50%, rgba(255,255,255,1) 100%);color:black;'

# Grey Gradient 
#THEME_COLOR     = 'background-image: linear-gradient(to bottom, #3b3b3b 10%, #808080 100%);color:white;'

# Green Gradient 
#THEME_COLOR     = 'background-image:linear-gradient(to bottom right,#d0e98d, #4e6b00);color:black;'
#

# Put list of NETWORK_ID from OPB links to don't show in lastheard/monitor duplicat entry, for example: "260210,260211,260212"
OPB_FILTER = ""

# Authorization of access to dashboard
WEB_AUTH =  True
WEB_USER =  'hblink'
WEB_PASS =  'hblink'

# Files and stuff for loading alias files for mapping numbers to names
PATH            = './'                           # MUST END IN '/'
PEER_FILE       = 'peer_ids.json'                # Will auto-download from DMR-MARC
SUBSCRIBER_FILE = 'subscriber_ids.json'          # Will auto-download from DMR-MARC
TGID_FILE       = 'talkgroup_ids.json'           # User provided, should be in "integer TGID, TGID name" format
LOCAL_SUB_FILE  = 'local_subscriber_ids.json'    # User provided (optional, leave '' if you don't use it), follow the format of DMR-MARC
LOCAL_PEER_FILE = 'local_peer_ids.json'          # User provided (optional, leave '' if you don't use it), follow the format of DMR-MARC
FILE_RELOAD     = 30                              # Number of days before we reload DMR-MARC database files
PEER_URL        = 'https://database.radioid.net/static/rptrs.json'
SUBSCRIBER_URL  = 'https://database.radioid.net/static/users.json'

# Settings for log files
LOG_PATH        = './log/'                       # MUST END IN '/'
LOG_NAME        = 'hbmon.log'
