# plugin.sh - DevStack plugin.sh dispatch script for gluon

gluon_debug() {
    if [ ! -z "$GLUON_DEVSTACK_DEBUG" ] ; then
	"$@" || true # a debug command failing is not a failure
    fi
}

# For debugging purposes, highlight gluon sections
gluon_debug tput setab 1

name=gluon

# The server

GITREPO['gluon']=${GLUON_REPO:-https://github.com/iawells/gluon.git}
GITBRANCH['gluon']=${GLUON_BRANCH:-demo}
GITDIR['gluon']=$DEST/gluon

# The client API libraries
GITREPO['gluonlib']=${GLUONLIB_REPO:-https://github.com/iawells/gluonlib.git}
GITBRANCH['gluonlib']=${GLUONLIB_BRANCH:-master}
GITDIR['gluonlib']=$DEST/gluonlib

# The Nova client plugin
GITREPO['gluon-nova']=${GLUON_NOVA_REPO:-https://github.com/iawells/gluon-nova.git}
GITBRANCH['gluon-nova']=${GLUON_NOVA_BRANCH:-master}
GITDIR['gluon-nova']=$DEST/gluon-nova

function pre_install_me {
    :
}

gluon_libs_executed=''
function install_gluon_libs {
    if [ -z "$gluon_libs_executed" ] ; then
        gluon_libs_executed=1 
(

	git_clone_by_name gluonlib # $GLUONLIB_REPO ${GITLIB['gluonlib']} $GLUONLIB_BRANCH
        cd ${GITDIR['gluonlib']}
	setup_dev_lib 'gluonlib'

	git_clone_by_name 'gluon-nova' #  $GLUON_NOVA_REPO ${GITDIR['gluon-nova']} $GLUON_NOVA_BRANCH
        cd ${GITDIR['gluon-nova']}
	setup_dev_lib 'gluon-nova'
)
    fi
}

function install_me {
    git_clone_by_name 'gluon' # $GLUON_REPO ${GITDIR['gluon']} $GLUON_BRANCH
    setup_develop ${GITDIR['gluon']}
}

function init_me {
    run_process $name "env GLUON_SETTINGS='/etc/gluon/gluon.config' '$GLUON_BINARY'"
}

function configure_me {
    # Nova needs adjusting from what it thinks it's doing
    iniset $NOVA_CONF DEFAULT network_api_class "gluon_nova.api.API"

# This will want switching to the Openstack way of doing things when
# we switch frameworks, but the Flask config files look like this:
    sudo mkdir -p /etc/gluon || true
    sudo tee /etc/gluon/gluon.config >/dev/null <<EOF
NEUTRON_USERNAME = '$ADMIN_USERNAME'
NEUTRON_PASSWORD = '$ADMIN_PASSWORD'
NEUTRON_TENANTNAME = '$ADMIN_TENANT'
KEYSTONE_URL = '$KEYSTONE_AUTH_URI'
EOF
}

function shut_me_down {
    stop_process $name
}


# check for service enabled
if is_service_enabled $name; then

    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        # Set up system services
        echo_summary "Configuring system services $name"
	pre_install_me

    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        # Perform installation of service source
        echo_summary "Installing $name"
        install_me

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        # Configure after the other layer 1 and 2 services have been configured
        echo_summary "Configuring $name"
        configure_me

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        # Initialize and start the service
        echo_summary "Initializing $name"
        init_me
    fi

    if [[ "$1" == "unstack" ]]; then
        # Shut down services
	shut_me_down
    fi

    if [[ "$1" == "clean" ]]; then
        # Remove state and transient data
        # Remember clean.sh first calls unstack.sh
        # no-op
        :
    fi
fi

gluon_debug tput setab 9
