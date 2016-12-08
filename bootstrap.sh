#!/bin/sh
tar_url='https://github.com/Crystalnix/termius-cli/archive/master.zip'

command_exists() {
    command -v "$@" > /dev/null 2>&1
}

eval_sh_c() {
    user="$(id -un 2>/dev/null || true)"

    _sh_c='sh -c'
    if [ "$user" != 'root' ]; then
	if command_exists sudo; then
	    _sh_c='sudo -E sh -c'
	elif command_exists su; then
	    _sh_c='su -c'
	else
	    cat >&2 <<-'EOF'
			Error: this installer needs the ability to run commands as root.
			We are unable to find either "sudo" or "su" available to make this happen.
			EOF
	    exit 1
	fi
    fi
    echo $_sh_c
}

do_install() {
    sh_c=$(eval_sh_c)
    curl=''
    if command_exists curl; then
	curl='curl -sSL'
    elif command_exists wget; then
	curl='wget -qO-'
    elif command_exists busybox && busybox --list-modules | grep -q wget; then
	curl='busybox wget -qO-'
    fi

    apt_requirements='python gcc python-dev libffi-dev libssl-dev'
    yum_requirements='python gcc python-devel libffi-devel openssl-devel'
    zypper_requirements='python gcc python-devel libffi-devel openssl-devel'

    lsb_dist=''
    if command_exists lsb_release; then
        lsb_dist="$(lsb_release -si)"
    fi
    if [ -z "$lsb_dist" ] && [ -r /etc/lsb-release ]; then
        lsb_dist="$(. /etc/lsb-release && echo "$DISTRIB_ID")"
    fi
    if [ -z "$lsb_dist" ] && [ -r /etc/debian_version ]; then
        lsb_dist='debian'
    fi
    if [ -z "$lsb_dist" ] && [ -r /etc/fedora-release ]; then
        lsb_dist='fedora'
    fi
    if [ -z "$lsb_dist" ] && [ -r /etc/os-release ]; then
        lsb_dist="$(. /etc/os-release && echo "$ID")"
    fi

    lsb_dist="$(echo "$lsb_dist" | tr '[:upper:]' '[:lower:]')"

    case "$lsb_dist" in
        amzn|fedora|centos)
	    (
	        set -x
	        $sh_c "sleep 3; yum -y -q install $yum_requirements"
	    )
	    ;;

        'opensuse project'|opensuse|'suse linux'|sled)
	    (
	        set -x
	        $sh_c "sleep 3; zypper -n install $zypper_requirements"
	    )
	    ;;

        ubuntu|debian|linuxmint|'elementary os'|kali)
	    export DEBIAN_FRONTEND=noninteractive

	    if [ -z "$curl" ]; then
		apt_get_update
		( set -x; $sh_c 'sleep 3; apt-get install -y -q curl ca-certificates' )
		curl='curl -sSL'
	    fi

	    did_apt_get_update=
	    apt_get_update() {
	        if [ -z "$did_apt_get_update" ]; then
		    ( set -x; $sh_c 'sleep 3; apt-get update' )
		    did_apt_get_update=1
	        fi
	    }


	    apt_get_update
            (
	        set -x
	        $sh_c "sleep 3; apt-get install -y -q $apt_requirements"
	    )
	    ;;
    esac

    if ! (command_exists easy_install); then
        $sh_c "$curl https://bootstrap.pypa.io/ez_setup.py |  python"
    fi
    easy_install -U $tar_url

    if command_exists termius; then
	(
	    set -x
	) || true
    fi
    exit 0
}

do_install
